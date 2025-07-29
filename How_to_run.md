# How to Run: Harri AI Assistant

## Prerequisites
- **Python 3.10+**
- **pip** (Python package manager)

## Quick Start

### **1. Activate Virtual Environment**
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### **2. Install Dependencies**
```bash
cd app
pip install -r requirements.txt
```

### **3. Set OpenAI API Key (Optional)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### **4. Initialize Database**
```bash
python3 init_db.py
```

### **5. Start Backend**
```bash
python3 main.py
```
**Backend:** http://localhost:8000

### **6. Start Frontend (New Terminal)**
```bash
streamlit run ui.py --server.port 8501
```
**Frontend:** http://localhost:8501

## Access
- **Web Interface:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

## Sample Queries
- "Who are the employees?"
- "What are the open tickets?"
- "How do I set up my development environment?"
- "What are the recent deployments?"

## Troubleshooting
- **Port in use:** Use different port or kill existing process
- **Database errors:** Run `python3 init_db.py` again
- **API issues:** Check `echo $OPENAI_API_KEY` 