# AI SQL Workspace

Ask your database questions in plain English. Get SQL, results, statistical insights and auto-selected charts.

## Features
- **Hybrid query engine:** 50+ rule-based patterns answer common questions instantly. Complex queries (JOINs etc.) go to an LLM with database schema context.
- **SQL safety:** every query is validated with sqlglot (single SELECT statement only), so INSERT / UPDATE / DELETE / DROP are blocked.
- **Insights:** min, max, average and total for numeric columns.
- **Smart charts:** automatically picks bar, pie or line charts.
- Dataset Explorer, 33 example prompts, SQL viewer with copy, Recent Runs.

## Tech Stack
Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Framer Motion, FastAPI, SQLAlchemy, SQLite, sqlglot, LLM API

## How It Works
User question → Next.js → FastAPI → keyword engine (else LLM) → sqlglot validation → SQLite → rows + insights + chart

## Setup

### Backend
```bash
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
pip install fastapi uvicorn sqlalchemy sqlglot pydantic python-dotenv google-generativeai
```
Create a `.env` file with your API key:
```
GEMINI_API_KEY=your_key_here
```
Seed the database and run:
```bash
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend/frontend
npm install
npm run dev
```
App: http://localhost:3000

## Sample Data
Seeded e-commerce data: 80 users and 220 orders across 18 Indian cities and 8 product categories.

## Example Queries
- how many users
- users by segment
- top 10 products by revenue
- show repeat customers

## Limitations
SQLite only, no authentication, Recent Runs are not persisted.

## Author
Anchal Kumari | [GitHub](https://github.com/anchal15-o) | [LinkedIn](https://linkedin.com/in/anchal-kumari-344a93297)
