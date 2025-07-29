# Harri Dev Team AI Assistant — End-to-End Prototype Assignment

## Background
Harri wants to boost engineering productivity by giving developers instant access to team knowledge, internal documentation, and dynamic data (like Jira tickets and deployments) through an intelligent assistant. Your challenge is to build a working end-to-end prototype of such an AI assistant for Harri’s dev team, using the provided sample datasets and mock APIs.

---

## Datasets & Resources

You are provided with:
- `/kb/` folder containing internal docs (`onboarding_guide.md`, `dev_env_setup.md`, `code_review_policy.md`, `deployment_process.md`, `escalation_policy.md`, `team_structure.md`)
- `employees.json` (employee/team roster and contact info)
- `jira_tickets.json` (example open issues assigned to team members)
- `deployments.json` (recent service deployment history)

You may simulate “live” data lookups using these files directly or by exposing them as mock APIs/functions.

---

## Assignment Requirements

### Your AI Assistant must:

**1. Use LLMs for Natural Language Understanding**
- You are required to use large language models (LLMs) for understanding and generating answers to user queries.
- You can use third-party APIs (such as OpenAI, Anthropic, or similar), or run an open-source LLM locally (such as Llama, Mistral, etc.).


**2. Answer Static Knowledge Questions**
- Retrieve and answer process/policy/documentation questions using the `/kb/` docs.
- Example:  
  - “How do I set up my development environment?”  
  - “What is the code review policy?”  
  - “What’s the on-call escalation process?”

**3. Fetch Dynamic Data via API/Function**
- Support queries that require live lookups from `employees.json`, `jira_tickets.json`, or `deployments.json`.
- Examples:  
  - “Show me my open Jira tickets.”  
  - “Who is on-call this week?”  
  - “List recent deployments for the payments service.”

**4. Reference Sources in Answers**
- Each answer should specify where the information was found (doc filename, employee record, ticket, etc.).
- If multiple sources are used, list them all.

**5. Handle Out-of-Scope or Unsupported Questions**
- For queries outside your data, reply clearly and helpfully (e.g., “Sorry, I cannot reset your GitHub password. Please contact IT Helpdesk.”).

**6. Observability & Logging - Plus**
- Log every user query, the actions your assistant took (retrieval, API call, etc.), results, and any errors.
- Provide a simple way (API, UI/table, or log file) to view these logs.

**7. Evaluation & Feedback - Plus**
- Allow users to rate/flag responses as helpful or unhelpful.
- Log this feedback and include an explanation of how you’d scale evaluation for production.

---

## Sample User Queries
- “How do I deploy a new service?”
- “What is the code review policy?”
- “Show me my open Jira tickets.”
- “Who is on-call this week?”
- “List the last 2 deployments for the onboarding service.”
- “Can you reset my GitHub password?” *(should reply appropriately—out of scope)*
- “What should I do if I find a critical bug in production?”

---

## What to Submit
### Required Deliverables
1. Your prototype (source code, instructions, and any scripts needed to run locally)
2. Business Solution Brief (1 page, non-technical): What business problems you solve, who benefits, key value, and limitations.
3. Self-Reflection (challenges, where you spent time, what you’d add/fix with more time)

### Optional (Plus) Deliverables
1. Technical Design & Notes (architecture, design decisions, logs/observability, handling limits, assumptions)
2. API documentation and database schema/design (with explanation and migration/init scripts if relevant)
---

## Evaluation Criteria
- **Coverage**: Handles static Q&A, dynamic lookups, LLM use, cites sources, logs actions, and collects feedback.
- **Trust**: User always knows where answers come from and why a query may not be answered.
- **Business Value**: Does it actually save time for Harri engineers?
- **Initiative**: Clear thinking about scaling, improvement, and risk.
- **Communication**: All documentation is clear and business-relevant.
---

**Python is strongly preferred.  
You must use an LLM (via API or local model).  
Your solution should be runnable and cover the full required flow with the datasets provided.**

---

*All needed datasets and sample files are included. If you have further questions, use reasonable assumptions and document them in your technical notes.*

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.10+
- OpenAI API key (optional, for full AI functionality)

### Step 1: Install Dependencies
```bash
cd app
python3 -m pip install -r requirements.txt
```

### Step 2: Set OpenAI API Key (Optional)
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Step 3: Initialize Database
```bash
cd app
python3 init_db.py
```

### Step 4: Start the FastAPI Backend
```bash
cd app
python3 main.py
```
The API will be available at: http://localhost:8000

### Step 5: Start the Streamlit UI (in a new terminal)
```bash
cd app
streamlit run ui.py --server.port 8501 --server.address 0.0.0.0
```
The UI will be available at: http://localhost:8501

### Step 6: Access the Application
1. **Web UI**: Open http://localhost:8501 in your browser
2. **API Documentation**: Open http://localhost:8000/docs in your browser
3. **Direct API**: Use curl or any HTTP client to access http://localhost:8000

### Quick Test Commands
```bash
# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/employees
curl http://localhost:8000/tickets
curl http://localhost:8000/deployments

# Test AI query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the employees?", "user_id": "test"}'

# Register a user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### Features Available
- ✅ **Authentication**: Register/login with username/password
- ✅ **AI Assistant**: Natural language queries with OpenAI integration
- ✅ **Static Knowledge**: Access to team documentation and policies
- ✅ **Dynamic Data**: Employee info, Jira tickets, deployment history
- ✅ **Database Logging**: All queries and responses logged to SQLite
- ✅ **Web Interface**: User-friendly Streamlit UI
- ✅ **API Access**: Full REST API with documentation

### Sample Queries to Try
- "Who are the employees?"
- "What are the open tickets?"
- "Tell me about the team structure"
- "What are the recent deployments?"
- "How do I set up my development environment?"
- "What is the code review policy?"
