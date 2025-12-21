#!/bin/bash
set -e

echo "Creating database tables..."
python -c "
import asyncio
from app.db.database import init_db

asyncio.run(init_db())
print('Tables created successfully!')
"

echo "Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
