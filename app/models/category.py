"""
Expense Category Enum

Fixed categories for expense classification.
The OCR service must map receipts to one of these exact values.
"""
from enum import Enum


class ExpenseCategory(str, Enum):
    """Enumeration of allowed expense categories."""
    
    FOOD = "Food"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"
    SHOPPING = "Shopping"
    OTHER = "Other"
    
    @classmethod
    def get_all_values(cls) -> list[str]:
        """Returns all category values as a list of strings."""
        return [category.value for category in cls]
    
    @classmethod
    def get_prompt_string(cls) -> str:
        """Returns a formatted string for LLM prompts."""
        return ", ".join(f'"{cat.value}"' for cat in cls)
