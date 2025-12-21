# 🧾 Smart-Scan Wallet (AI-Powered Finance Tracker)

A "Senior-Level" financial backend that uses Generative AI to automate expense tracking. Users can upload raw receipts, and the system automatically extracts data, categorizes expenses, and allows users to query their financial data using natural language.

**Tech Stack:** Python 3.11, FastAPI, PostgreSQL (Async), OpenAI GPT-4o, Supabase.

---

## 🚀 Key Features

* **🤖 AI Receipt OCR:** Uses OpenAI Vision to extract Merchant, Date, and Amount from images with 99% accuracy.
* **🧠 Intelligent Categorization:** Automatically maps expenses to fixed categories (Food, Transport, etc.) using strict Enum enforcement.
* **💬 Chat-with-Data (RAG-Lite):** Users can ask "How much did I spend on Sushi?" and the system converts this to safe SQL queries.
* **🛡️ Enterprise Security:** OAuth2 JWT Authentication + Row Level Security (RLS) logic.

---

## 🛠️ Architecture

```
[FastAPI Async Server] <--> [PostgreSQL (via SQLModel)]
       |
       +--> [OpenAI GPT-4o-mini] (For OCR & Text-to-SQL)
       +--> [Supabase Storage] (For Audit-ready Image hosting)
```

### Project Structure

```
smart-scan-wallet/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── alembic/                   # Database migrations
└── app/
    ├── core/                  # Config & Security
    ├── db/                    # Async database setup
    ├── models/                # SQLModel definitions
    ├── schemas/               # Pydantic schemas
    ├── services/              # OCR, Storage, Chat AI
    └── api/v1/endpoints/      # REST endpoints
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/smart-scan-wallet.git
cd smart-scan-wallet
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file:

```bash
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/smartscan"
OPENAI_API_KEY="sk-..."
SECRET_KEY="your-secret-key"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key"
SUPABASE_BUCKET="receipts"
```

### 3. Run Migrations & Server

```bash
# Create database (PostgreSQL)
createdb smartscan

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

### 4. Explore API

Visit `http://localhost:8000/docs` to test the endpoints interactively.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create user account |
| POST | `/api/v1/auth/login` | Get JWT token |
| POST | `/api/v1/receipts/upload` | Upload receipt → OCR → Save |
| GET | `/api/v1/receipts/` | List expenses |
| GET | `/api/v1/analytics/monthly` | Spending by category |
| POST | `/api/v1/chat/` | Natural language queries |

---

## 🔐 Authentication

This API uses **OAuth2 with Bearer tokens**. To access protected endpoints:

1. Register: `POST /api/v1/auth/register`
2. Login: `POST /api/v1/auth/login` → Get `access_token`
3. Include header: `Authorization: Bearer <token>`

---

## 📊 Smart Scan Workflow

```
📷 Upload Image → ☁️ Supabase Storage → 🤖 GPT-4o-mini OCR → 💾 PostgreSQL
```

The OCR extracts:
- **Merchant** name
- **Date** of transaction
- **Amount** (decimal)
- **Category** (auto-classified)
- **Is Subscription** flag

---

## 💬 Chat Examples

Ask natural language questions:

- *"How much did I spend on Uber?"*
- *"What's my total spending this month?"*
- *"Show me my food expenses"*
- *"What are my subscriptions?"*

The AI converts questions to SQL, executes safely, and returns friendly answers.

---

## 📁 Expense Categories

| Category | Color (for charts) |
|----------|-------------------|
| Food | #FF6384 |
| Transport | #36A2EB |
| Utilities | #FFCE56 |
| Entertainment | #9966FF |
| Health | #4BC0C0 |
| Shopping | #FF9F40 |
| Other | #C9CBCF |

---

## 🛡️ Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT tokens with expiration
- ✅ SQL injection prevention in chat
- ✅ User data isolation (RLS pattern)
- ✅ File type validation for uploads

---

## 📄 License

MIT License - Feel free to use for personal or commercial projects.
