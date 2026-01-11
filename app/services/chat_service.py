"""
Chat Service - Text-to-SQL with AI

Converts natural language questions into SQL queries and provides human-friendly answers.
Uses OpenAI/OpenRouter for both SQL generation and answer synthesis.
"""
import re
from typing import Any

from openai import AsyncOpenAI
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings


# OpenRouter API base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_openai_client() -> AsyncOpenAI:
    """Get configured OpenAI/OpenRouter async client."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI/OpenRouter API key not configured"
        )
    
    # Check if using OpenRouter key
    if settings.openai_api_key.startswith("sk-or-"):
        return AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://smartscan-wallet.local",
                "X-Title": "Smart-Scan Wallet"
            }
        )
    else:
        return AsyncOpenAI(api_key=settings.openai_api_key)


# Database schema description for the LLM
DATABASE_SCHEMA = """
Table: expenses
Columns:
- id: INTEGER (primary key)
- user_id: INTEGER (foreign key to users table)
- merchant: VARCHAR(255) (name of store/business)
- amount: DECIMAL(10,2) (transaction amount in dollars)
- date: TIMESTAMP (date of the expense)
- category: TEXT (one of: 'FOOD', 'TRANSPORT', 'UTILITIES', 'ENTERTAINMENT', 'HEALTH', 'SHOPPING', 'OTHER')
- is_subscription: BOOLEAN (true if recurring expense)
- receipt_url: VARCHAR (URL to receipt image)
- created_at: TIMESTAMP (when record was created)

Important Notes:
- Always filter by user_id = {user_id} for security
- Use ILIKE for case-insensitive text matching on merchant
- Category column should be cast to TEXT and compared: category::TEXT = 'FOOD'
- Amount is stored as decimal, use SUM() for totals
"""

SQL_GENERATION_PROMPT = """You are a PostgreSQL SQL expert. Your job is to convert natural language questions into valid SQL SELECT queries.

{schema}

CRITICAL RULES:
1. ONLY generate SELECT statements - never INSERT, UPDATE, DELETE, DROP, or any other modifying query
2. ALWAYS include WHERE user_id = {user_id} to ensure data security
3. Return ONLY the raw SQL query - no markdown, no explanation, no code blocks
4. Use proper PostgreSQL syntax
5. For date filtering, use EXTRACT() or date comparisons
6. For "today" queries, handling timezones is critical. Query for: date >= CURRENT_DATE - INTERVAL '1 day' AND date <= CURRENT_DATE + INTERVAL '1 day'
7. For text search on merchant, use ILIKE for case-insensitive matching
8. For category filtering, use: category::TEXT = 'FOOD' (uppercase, cast to TEXT)
9. If the question is unclear, make reasonable assumptions
10. Limit results to 100 rows maximum
11. If the user input is a greeting (e.g., 'hi', 'hello') or not a data question, return: SELECT 'greeting' as message;

Category mapping:
- food/restaurant/grocery -> 'FOOD'
- transport/uber/taxi/gas -> 'TRANSPORT'  
- utilities/electric/water -> 'UTILITIES'
- entertainment/movie/games -> 'ENTERTAINMENT'
- health/medical/pharmacy -> 'HEALTH'
- shopping/store/amazon -> 'SHOPPING'
- other -> 'OTHER'

Examples:
- "How much did I spend on food?" -> SELECT SUM(amount) FROM expenses WHERE user_id = {user_id} AND category::TEXT = 'FOOD'
- "Show my Uber expenses" -> SELECT * FROM expenses WHERE user_id = {user_id} AND merchant ILIKE '%uber%' LIMIT 100
- "What's my total spending this month?" -> SELECT SUM(amount) FROM expenses WHERE user_id = {user_id} AND EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM CURRENT_DATE)
- "Hi" -> SELECT 'greeting' as message;
"""

ANSWER_SYNTHESIS_PROMPT = """You are a friendly financial assistant. The user asked a question about their expenses, and you have the database result.

User's question: "{question}"
Database result: {result}

Provide a friendly, concise answer in 1-2 sentences. If the result is a number, format it as currency (e.g., $45.00). 
If there's no data, say something like "I couldn't find any matching expenses."
If the result contains multiple rows, summarize the key points.
Don't mention SQL or databases - just give a natural answer."""


def validate_sql_query(sql: str) -> bool:
    """
    Validate that the SQL query is safe to execute.
    
    Returns True if the query is a SELECT statement without dangerous operations.
    """
    # Normalize whitespace and convert to uppercase for checking
    normalized = " ".join(sql.upper().split())
    
    # Dangerous keywords that should never appear
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE",
        "ALTER", "CREATE", "GRANT", "REVOKE", "EXEC",
        "EXECUTE", "INTO", "MERGE", "REPLACE", "--", "/*"
    ]
    
    for keyword in dangerous_keywords:
        if keyword in normalized:
            return False
    
    # Must start with SELECT
    if not normalized.strip().startswith("SELECT"):
        return False
    
    return True


def clean_sql_response(response: str) -> str:
    """Clean the SQL response from markdown formatting."""
    cleaned = response.strip()
    
    # Remove markdown code blocks
    if cleaned.startswith("```sql"):
        cleaned = cleaned[6:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Remove semicolon if present (we'll add it)
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1]
    
    return cleaned


async def generate_sql_query(question: str, user_id: int) -> str:
    """
    Generate a SQL query from a natural language question.
    
    Args:
        question: User's natural language question
        user_id: The authenticated user's ID
        
    Returns:
        Valid SQL SELECT query
        
    Raises:
        HTTPException: If SQL generation fails or produces invalid query
    """
    client = get_openai_client()
    
    schema_with_user = DATABASE_SCHEMA.format(user_id=user_id)
    system_prompt = SQL_GENERATION_PROMPT.format(
        schema=schema_with_user,
        user_id=user_id
    )
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.0  # Deterministic for SQL generation
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate SQL query"
            )
        
        sql = clean_sql_response(response.choices[0].message.content)
        
        # Validate the generated SQL
        if not validate_sql_query(sql):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Generated query failed security validation"
            )
        
        # Ensure user_id filter is present (skip for greetings)
        is_greeting = "'greeting' as message" in sql.lower()
        if not is_greeting and f"user_id = {user_id}" not in sql and f"user_id={user_id}" not in sql:
            # Add user_id filter if missing
            if "WHERE" in sql.upper():
                sql = sql.replace("WHERE", f"WHERE user_id = {user_id} AND", 1)
            else:
                sql += f" WHERE user_id = {user_id}"
        
        return sql
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL generation failed: {str(e)}"
        )


async def execute_sql_query(sql: str, session: AsyncSession) -> list[Any]:
    """
    Execute a SQL query and return results.
    
    Args:
        sql: SQL SELECT query to execute
        session: Database session
        
    Returns:
        List of result rows
    """
    try:
        result = await session.execute(text(sql))
        rows = result.fetchall()
        return rows
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


async def synthesize_answer(question: str, sql_result: list[Any]) -> str:
    """
    Convert SQL results into a human-friendly answer.
    
    Args:
        question: Original user question
        sql_result: Raw result from SQL query
        
    Returns:
        Human-friendly answer string
    """
    client = get_openai_client()
    
    # Format result for the prompt
    if not sql_result:
        result_str = "No results found"
    elif len(sql_result) == 1 and len(sql_result[0]) == 1:
        # Single value result (e.g., SUM)
        value = sql_result[0][0]
        result_str = str(value) if value is not None else "No data"
    else:
        # Multiple rows - format as list
        result_str = str([tuple(row) for row in sql_result[:10]])  # Limit to 10 rows
        if len(sql_result) > 10:
            result_str += f" ... and {len(sql_result) - 10} more rows"
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": ANSWER_SYNTHESIS_PROMPT.format(
                        question=question,
                        result=result_str
                    )
                },
                {"role": "user", "content": "Please summarize the result."}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        if not response.choices or not response.choices[0].message.content:
            return f"Query result: {result_str}"
        
        return response.choices[0].message.content.strip()
        
    except Exception:
        # Fallback to raw result if synthesis fails
        return f"Query result: {result_str}"


async def process_user_query(
    user_query: str,
    user_id: int,
    session: AsyncSession
) -> dict:
    """
    Process a natural language query about expenses.
    
    This function:
    1. Generates SQL from the user's question
    2. Executes the SQL against the database
    3. Synthesizes a human-friendly answer
    
    Args:
        user_query: Natural language question
        user_id: Authenticated user's ID
        session: Database session
        
    Returns:
        Dictionary with response and metadata
    """
    # Step 1: Generate SQL
    sql_query = await generate_sql_query(user_query, user_id)
    
    # Step 2: Execute SQL
    results = await execute_sql_query(sql_query, session)
    
    # Step 3: Synthesize answer
    answer = await synthesize_answer(user_query, results)
    
    return {
        "response": answer,
        "query": sql_query,  # Include for debugging/transparency
        "result_count": len(results)
    }
