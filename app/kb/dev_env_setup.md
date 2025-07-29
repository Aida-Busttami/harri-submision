# Developer Environment Setup

Setting up your development environment at Harri ensures you can build, test, and deploy with confidence.
Please follow these steps carefully. If you encounter issues, reach out to the DevOps team.

---

## 1. System Requirements

- Ubuntu 22.04 LTS or MacOS 12+
- Python 3.10 or higher
- Docker Desktop (latest stable)
- Node.js 18+ (for frontend projects)
- 8GB+ RAM recommended

---

## 2. Initial Setup Steps

1. Clone the main monorepo from GitHub using your SSH key.
   Repository: git@github.com:harri/main-monorepo.git

2. Create and activate a virtual environment:
      python3 -m venv venv
      source venv/bin/activate

3. Copy .env.example to .env and update environment variables with credentials (ask your team lead for secrets).

4. Install dependencies:
      pip install -r requirements.txt

   For frontend:
      cd frontend
      npm install

---

## 3. Dockerized Local Services

- Ensure Docker is running.
- Start backend and supporting services:
      docker-compose up -d
- Verify services by running:
      docker ps
  and check that harri-backend, harri-db, and harri-redis are healthy.

---

## 4. Running the App

- Start the backend server:
      python main.py
- Start the frontend (optional):
      cd frontend
      npm run dev
- Access the app at http://localhost:3000

---

## 5. Troubleshooting

- For common Docker issues, see Docker Troubleshooting Guide (https://docs.docker.com/get-docker/).
- Database connection issues: Check .env credentials and that harri-db is running.
- Dependency errors: Delete venv, reinstall dependencies, and clear npm cache.

---

## 6. Support

- DevOps: Adam Smith (adam@harri.com)
- Backend: Ahmed Ali (ahmed@harri.com)

*Refer to 'deployment_process.md' for information on deploying to staging and production.*
