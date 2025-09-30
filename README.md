# Data Dashboard Project

A web application to upload .csv/Excel files and visualize data with animated graphs. Uses React (frontend), Node.js/Express (backend), Python/FastAPI (data processing), and MongoDB (storage).

## Setup
1. Install MongoDB Atlas free tier (get URI for `.env`).
2. `cd frontend`, `npm install`, `npm start`.
3. `cd backend`, `npm install`, `node server.js`.
4. `cd python-microservice`, `pip install -r requirements.txt`, `uvicorn app.main:app --reload`.
5. Update `config/.env` with your MongoDB URI.

## Features
- Upload files, auto-generate graphs on left.
- Switch graph types (bar, donut, etc.).
- Dark mode, download graphs, AI chat.

## Expand
- Add R (`optional/r-scripts/`), C++ (`optional/cpp/`), or Java (`optional/java/`).
