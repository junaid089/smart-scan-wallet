"""
Receipts Endpoints

Handles receipt image upload, OCR processing, and expense creation.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.expense import Expense
from app.schemas.expense import ExpenseResponse, ReceiptUploadResponse
from app.services.storage import upload_receipt_file
from app.services.ocr_service import analyze_receipt


router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a receipt image",
    description="Upload a receipt image for OCR processing. The image will be analyzed and an expense record will be created."
)
async def upload_receipt(
    file: Annotated[UploadFile, File(description="Receipt image file (JPEG, PNG, WebP, or HEIC)")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ReceiptUploadResponse:
    """
    Upload and process a receipt image.
    
    This endpoint:
    1. Uploads the image to Supabase Storage
    2. Sends the image to OpenAI Vision API for OCR
    3. Extracts expense data (merchant, amount, date, category)
    4. Creates an Expense record in the database
    5. Returns the created expense with OCR data
    
    Supported image formats: JPEG, PNG, WebP, HEIC
    """
    # Validate file is provided
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Step 1: Upload to storage (Supabase or local)
    try:
        print(f"[DEBUG] Uploading file for user {current_user.id}")
        receipt_url = await upload_receipt_file(
            file=file,
            user_id=current_user.id
        )
        print(f"[DEBUG] File uploaded successfully: {receipt_url}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Step 2: Analyze receipt with OpenAI Vision
    try:
        print(f"[DEBUG] Analyzing receipt with OpenAI...")
        ocr_data = await analyze_receipt(image_url=receipt_url)
        print(f"[DEBUG] OCR completed: {ocr_data}")
    except HTTPException as e:
        print(f"[ERROR] OCR HTTPException: {e.detail}")
        raise
    except Exception as e:
        print(f"[ERROR] OCR failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze receipt: {str(e)}"
        )
    
    # Step 3: Create Expense record in database
    try:
        new_expense = Expense(
            user_id=current_user.id,
            merchant=ocr_data["merchant"],
            amount=ocr_data["amount"],
            currency=ocr_data.get("currency", "INR"),
            date=ocr_data["date"],
            category=ocr_data["category"],
            is_subscription=ocr_data["is_subscription"],
            receipt_url=receipt_url
        )
        
        db.add(new_expense)
        await db.commit()
        await db.refresh(new_expense)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save expense: {str(e)}"
        )
    
    # Step 4: Build response
    # Convert OCR data for JSON serialization
    ocr_response = {
        "merchant": ocr_data["merchant"],
        "amount": float(ocr_data["amount"]),
        "currency": ocr_data.get("currency", "INR"),
        "date": ocr_data["date"].isoformat(),
        "category": ocr_data["category"].value,
        "is_subscription": ocr_data["is_subscription"]
    }
    
    return ReceiptUploadResponse(
        message="Receipt processed successfully",
        expense=ExpenseResponse.model_validate(new_expense),
        ocr_data=ocr_response
    )


@router.get(
    "/",
    response_model=list[ExpenseResponse],
    summary="List user's expenses",
    description="Get all expenses for the authenticated user."
)
async def list_expenses(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 50
) -> list[Expense]:
    """
    List all expenses for the current user.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    from sqlmodel import select
    
    statement = (
        select(Expense)
        .where(Expense.user_id == current_user.id)
        .order_by(Expense.date.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(statement)
    expenses = result.scalars().all()
    
    return list(expenses)
