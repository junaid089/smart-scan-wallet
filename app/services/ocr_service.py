"""
OCR Service using OpenAI Vision API

Analyzes receipt images and extracts structured expense data using GPT-4o-mini.
Supports both URLs and local file paths.
Compatible with OpenRouter API.
"""
import base64
import decimal
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from openai import AsyncOpenAI
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.category import ExpenseCategory


# OpenRouter API base URL (compatible with OpenAI SDK)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


# Initialize async OpenAI client (works with OpenRouter)
def get_openai_client() -> AsyncOpenAI:
    """Get configured OpenAI/OpenRouter async client."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI/OpenRouter API key not configured"
        )
    
    # Check if using OpenRouter key (starts with sk-or-)
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
        # Standard OpenAI
        return AsyncOpenAI(api_key=settings.openai_api_key)


# System prompt for receipt analysis
SYSTEM_PROMPT = """You are an expense tracking assistant specialized in analyzing receipt images.

Your task is to extract structured data from receipt images and return ONLY valid JSON.

IMPORTANT RULES:
1. Extract the merchant name, transaction date, total amount, and determine the category.
2. The category MUST be exactly one of: "Food", "Transport", "Utilities", "Entertainment", "Health", "Shopping", "Other"
3. Determine if this appears to be a subscription/recurring charge based on the receipt content.
4. If you cannot determine a value with confidence, use reasonable defaults:
   - merchant: Use visible store/business name, or "Unknown Merchant"
   - date: Use today's date if not visible
   - amount: Extract the total/grand total, not subtotals
   - category: Default to "Other" if unclear
   - is_subscription: Default to false unless clearly a recurring service

Return ONLY a valid JSON object with no additional text or markdown formatting."""


def get_user_prompt(image_url: str, current_date: str) -> str:
    """Generate the user prompt with the image URL."""
    return f"""Analyze this receipt image and extract the expense data.

Image URL: {image_url}

Today's date for reference: {current_date}

Return your response as a JSON object with this EXACT structure:
{{
    "merchant": "Name of the store or business",
    "date": "YYYY-MM-DD",
    "amount": 0.00,
    "category": "One of: Food, Transport, Utilities, Entertainment, Health, Shopping, Other",
    "is_subscription": false
}}

Remember:
- "amount" must be a number (float), not a string
- "date" must be in YYYY-MM-DD format
- "category" must be exactly one of the allowed values
- "is_subscription" must be a boolean (true/false)"""


def validate_and_parse_response(response_text: str) -> dict:
    """
    Validate and parse the OpenAI response into structured data.
    
    Args:
        response_text: Raw text response from OpenAI
        
    Returns:
        Validated dictionary with expense data
        
    Raises:
        HTTPException: If response cannot be parsed or validated
    """
    # Clean up response - remove markdown code blocks if present
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    # Parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse AI response as JSON: {str(e)}"
        )
    
    # Validate required fields
    required_fields = ["merchant", "date", "amount", "category"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required field in AI response: {field}"
            )
    
    # Validate and normalize category
    category_value = data.get("category", "Other")
    valid_categories = ExpenseCategory.get_all_values()
    
    if category_value not in valid_categories:
        # Try to match case-insensitively
        category_lower = category_value.lower()
        matched = False
        for valid_cat in valid_categories:
            if valid_cat.lower() == category_lower:
                category_value = valid_cat
                matched = True
                break
        if not matched:
            category_value = "Other"
    
    # Validate and parse date
    try:
        date_str = data["date"]
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        # Default to today if date parsing fails
        parsed_date = datetime.utcnow()
    
    # Validate and parse amount
    try:
        amount = Decimal(str(data["amount"]))
        if amount < 0:
            amount = abs(amount)
    except (ValueError, TypeError, decimal.InvalidOperation):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid amount value in AI response"
        )
    
    # Build validated response
    return {
        "merchant": str(data.get("merchant", "Unknown Merchant"))[:255],
        "date": parsed_date,
        "amount": amount,
        "category": ExpenseCategory(category_value),
        "is_subscription": bool(data.get("is_subscription", False))
    }


async def analyze_receipt(image_url: str) -> dict:
    """
    Analyze a receipt image using OpenAI Vision API.
    
    Args:
        image_url: Public URL of the receipt image
        
    Returns:
        Dictionary containing extracted expense data:
        - merchant: str
        - date: datetime
        - amount: Decimal
        - category: ExpenseCategory
        - is_subscription: bool
        
    Raises:
        HTTPException: If analysis fails
    """
    client = get_openai_client()
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Handle local file paths - convert to base64
    image_content = None
    if image_url.startswith("file://"):
        local_path = image_url.replace("file://", "")
        try:
            with open(local_path, "rb") as f:
                image_data = f.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
            # Determine mime type from extension
            ext = os.path.splitext(local_path)[1].lower()
            mime_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
            mime_type = mime_types.get(ext, "image/jpeg")
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}",
                    "detail": "high"
                }
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read local image: {str(e)}"
            )
    else:
        # Use URL directly
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": image_url,
                "detail": "high"
            }
        }
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": get_user_prompt(image_url, current_date)
                        },
                        image_content
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.1  # Low temperature for consistent structured output
        )
        
        # Extract response content
        if not response.choices or not response.choices[0].message.content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Empty response from AI service"
            )
        
        response_text = response.choices[0].message.content
        
        # Validate and parse the response
        return validate_and_parse_response(response_text)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )

