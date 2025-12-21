// API Response Types
export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Expense {
  id: number;
  user_id: number;
  merchant: string;
  amount: number;
  date: string;
  category: ExpenseCategory;
  is_subscription: boolean;
  receipt_url: string | null;
  created_at: string;
}

export type ExpenseCategory = 
  | 'FOOD' 
  | 'TRANSPORT' 
  | 'UTILITIES' 
  | 'ENTERTAINMENT' 
  | 'HEALTH' 
  | 'SHOPPING' 
  | 'OTHER';

export interface ReceiptUploadResponse {
  message: string;
  expense: Expense;
  ocr_data: {
    merchant: string;
    amount: number;
    date: string;
    category: string;
    is_subscription: boolean;
  };
}

export interface CategorySpending {
  category: string;
  amount: number;
  color: string;
  percentage: number;
}

export interface MonthlyAnalytics {
  month: string;
  year: number;
  total_spending: number;
  categories: CategorySpending[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  query: string;
  result_count: number;
}

export interface SpendingSummary {
  total_spending: number;
  expense_count: number;
  average_per_expense: number;
  top_category: string;
  top_category_amount: number;
}
