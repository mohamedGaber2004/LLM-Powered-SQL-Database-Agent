# 🤖 LLM-Powered SQL Database Agent

A full-stack intelligent SQL query agent that converts **natural language** into **SQL queries**, executes them against your database, and presents results through a **modern, animated Streamlit interface**. Built with LangChain, LangGraph, and Groq's GPT-OSS models.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🚀 Features

- 🌟 **Natural Language to SQL** - Converts plain English queries into SQL using Groq's GPT-OSS model
- 🔄 **Automated Execution** - Executes generated SQL queries directly against your database
- 🎨 **Modern UI** - Animated, colorful Streamlit interface with gradients and hover effects
- 📊 **Query Results** - View results in formatted tables with CSV export capability
- 📜 **Query History** - Track last 5 queries with prompts and generated SQL
- 💡 **Query Optimization** - Receives optimization tips for generated queries
- ✅ **Health Checks** - Monitor backend API status from the sidebar
- 📝 **Example Queries** - Pre-configured examples for quick testing
- 🔗 **REST API** - Full FastAPI backend for programmatic access
- 📦 **Multi-Database Support** - Compatible with MySQL, PostgreSQL, and more via SQLAlchemy
- 🛠️ **LangGraph Workflow** - Intelligent agentic workflow for query generation and execution

---

## Architecture

The project follows a **microservices architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (UI.py)                    │
│                  - Natural Language Input                    │
│                  - Results Display & History                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                      HTTP (FastAPI)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               FastAPI Backend (main.py)                      │
│         - SQL Generation Endpoint                            │
│         - Query Execution Endpoint                           │
│         - Health Check                                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
           ┌───────────────────┴───────────────────┐
           │                                       │
    ┌──────▼──────────┐              ┌────────────▼────────┐
    │  LangGraph      │              │  Database Module    │
    │  Agent Flow     │              │  (SQLAlchemy)       │
    │  - Generate SQL │              │  - Schema Retrieval │
    │  - Execute Queries             │  - Query Execution  │
    └─────────────────┘              └─────────────────────┘
           │
    ┌──────▼──────────┐
    │  Groq LLM       │
    │  (GPT-OSS)      │
    └─────────────────┘
```

---

## Prerequisites

- **Python 3.11+** (as specified in `pyproject.toml`)
- **MySQL Server** (or compatible database)
- **Groq API Key** (for LLM access)
- **pip** or **uv** package manager
- Internet connection for LLM API calls

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LLM-Powered-SQL-Database-Agent
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pyproject.toml
pip install -e .
```

---

## Configuration

### Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name
MYSQL_PORT=3306
```

**Getting a Groq API Key:**
1. Visit [Groq Console](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key and copy it to your `.env` file

### Database Connection

The project uses **SQLAlchemy** for database abstraction. It currently supports:
- **MySQL** (default)
- **PostgreSQL** (requires `psycopg2-binary`)
- **Other databases** (via appropriate drivers)

To use a different database, update the `DATABASE_URL` in [Config/config.py](Config/config.py).

---

## Usage

### Option 1: Using Streamlit UI (Recommended)

```bash
# Start the backend API first (in one terminal)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# In another terminal, start the Streamlit app
streamlit run UI.py
```

The UI will open at `http://localhost:8501`

### Option 2: Using REST API Directly

```bash
# Start the API server
python -m uvicorn main:app --reload

# Example: Generate SQL from natural language
curl -X POST "http://127.0.0.1:8000/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me all users who registered in the last 30 days"}'

# Example: Execute a SQL query
curl -X POST "http://127.0.0.1:8000/execute-sql" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY);"}'
```

---

## API Endpoints

### 1. **Generate SQL from Natural Language**

**Endpoint:** `POST /generate-sql`

**Request:**
```json
{
  "prompt": "Show me all users who registered in the last 30 days"
}
```

**Response:**
```json
{
  "sql_query": "SELECT * FROM users WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY);",
  "status": "success"
}
```

### 2. **Execute SQL Query**

**Endpoint:** `POST /execute-sql`

**Request:**
```json
{
  "query": "SELECT * FROM users LIMIT 10;"
}
```

**Response:**
```json
{
  "results": [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"}
  ],
  "row_count": 2,
  "status": "success"
}
```

### 3. **Health Check**

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Project Structure

```
LLM-Powered-SQL-Database-Agent/
│
├── main.py                 # FastAPI backend application
├── UI.py                   # Streamlit frontend application
├── requirements.txt        # Project dependencies
├── pyproject.toml         # Project metadata and dependencies
├── README.md              # This file
├── LICENSE                # Project license
│
├── Config/
│   ├── __init__.py
│   └── config.py          # Database and configuration settings
│
└── src/
    ├── __init__.py
    │
    ├── Database/
    │   ├── __init__.py
    │   └── database.py     # Database connection and schema retrieval
    │
    ├── LLMs/
    │   ├── __init__.py
    │   └── groq_gpt_oss.py # Groq LLM initialization
    │
    ├── graphs/
    │   ├── __init__.py
    │   └── graph_builder.py # LangGraph workflow orchestration
    │
    ├── prompts/
    │   ├── __init__.py
    │   └── generate_sql_prompt.py # SQL generation prompts
    │
    └── tools/
        ├── __init__.py
        └── database_tool.py # SQL generation and execution tools
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Groq GPT-OSS (120B) | Natural language understanding & SQL generation |
| **Orchestration** | LangGraph | Agentic workflow management |
| **Framework** | LangChain | LLM integration and tooling |
| **Backend API** | FastAPI | REST API server |
| **Frontend** | Streamlit | Interactive user interface |
| **Database ORM** | SQLAlchemy | Database abstraction |
| **Database Drivers** | psycopg2, mysql-connector | Database connectivity |
| **Embeddings** | Sentence Transformers | Vector embeddings (if used) |
| **Vector DB** | ChromaDB | Vector storage and retrieval |

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API authentication key | `gsk_xxxx...` |
| `MYSQL_HOST` | Database hostname | `localhost` |
| `MYSQL_USER` | Database username | `root` |
| `MYSQL_PASSWORD` | Database password | `password123` |
| `MYSQL_DATABASE` | Database name | `my_database` |
| `MYSQL_PORT` | Database port | `3306` |

---

## Key Components

### 1. **Graph Builder** (`src/graphs/graph_builder.py`)
- Orchestrates the workflow using LangGraph
- Manages state transitions between SQL generation and execution
- Handles error management and response formatting

### 2. **Database Module** (`src/Database/database.py`)
- Manages database connections via SQLAlchemy
- Retrieves database schema dynamically
- Ensures connection health and stability

### 3. **LLM Integration** (`src/LLMs/groq_gpt_oss.py`)
- Initializes Groq's GPT-OSS model
- Provides LLM instance for the workflow

### 4. **Tools** (`src/tools/database_tool.py`)
- `generate_sql_query()` - Converts natural language to SQL
- `execute_query()` - Executes SQL and returns results

### 5. **Prompts** (`src/prompts/generate_sql_prompt.py`)
- Contains system and user prompts for SQL generation
- Includes context about database schema

---

## Troubleshooting

### Issue: `GROQ_API_KEY not found`

**Solution:** Ensure your `.env` file is in the project root and contains the `GROQ_API_KEY`.

```bash
# Verify .env exists
ls -la .env

# Check if GROQ_API_KEY is set
grep GROQ_API_KEY .env
```

### Issue: `Connection refused` (Database)

**Solution:** Verify MySQL is running and credentials are correct.

```bash
# Test MySQL connection
mysql -h <MYSQL_HOST> -u <MYSQL_USER> -p<MYSQL_PASSWORD> -D <MYSQL_DATABASE>
```

### Issue: `Port 8000 already in use`

**Solution:** Use a different port for the API server.

```bash
python -m uvicorn main:app --port 8001
```

### Issue: `Module not found` errors

**Solution:** Ensure the virtual environment is activated and dependencies are installed.

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Streamlit can't connect to backend

**Solution:** Ensure the FastAPI backend is running on port 8000.

```bash
# Check if port 8000 is listening
netstat -tuln | grep 8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

---

## Performance Tips

1. **Batch Queries** - Group multiple queries when possible to reduce API calls
2. **Cache Results** - Implement result caching for frequently asked questions
3. **Index Database** - Ensure frequently queried columns are indexed
4. **Optimize Prompts** - Refine system prompts for faster, more accurate SQL generation
5. **Use Connection Pooling** - SQLAlchemy handles this automatically, but monitor pool size if needed

---

## Future Enhancements

- [ ] Query optimization suggestions
- [ ] Multi-database support with database switching
- [ ] Query result caching
- [ ] Advanced error handling and recovery
- [ ] Query performance analytics
- [ ] User authentication and query audit logs
- [ ] Support for complex joins and subqueries
- [ ] Batch query execution
- [ ] Export results to multiple formats (CSV, JSON, Excel)

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation and troubleshooting guides
- Review the [LangChain documentation](https://python.langchain.com)
- Consult [Groq API documentation](https://console.groq.com/docs)

---

## Acknowledgments

- **Groq** for providing the high-performance GPT-OSS model
- **LangChain** for excellent LLM orchestration tools
- **LangGraph** for agentic workflow management
- **FastAPI** for the modern API framework
- **Streamlit** for the interactive UI framework

---

**Last Updated:** January 2026

## 🖥️ Demo

![App Screenshot](path_to_screenshot.png)  
*Note: Add a screenshot of your app here.*

---

## ⚙️ Installation

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/ai-sql-generator.git
cd ai-sql-generator


python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows


pip install -r requirements.txt


streamlit run app.py
