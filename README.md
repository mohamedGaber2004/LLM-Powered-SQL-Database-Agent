# 🤖 AI-Powered SQL Query Generator

A Streamlit app that converts **natural language queries** into **SQL**, executes them automatically, and displays results in a **colorful, animated, modern interface**.

---

## 🚀 Features

- 🌟 **One-step SQL generation and execution** from natural language.  
- 🎨 **Animated, colorful UI** with gradients, hover effects, and expanding SQL boxes.  
- 🛠️ **View generated SQL** in an expandable, styled code box.  
- 📊 **Query results table** with download to CSV.  
- 📜 **Query history** (last 5 queries) with prompt & SQL.  
- 💡 **Optimization tips** for SQL queries returned by backend.  
- ✅ **Backend health check** in sidebar.  
- 📝 **Example queries** for quick testing.  
- 🗑️ **Clear history** button.

---

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
