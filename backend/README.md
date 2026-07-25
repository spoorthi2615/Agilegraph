# AgileGraph Backend

## Project Overview
AgileGraph Backend is the enterprise-grade foundation for an AI-powered Post Quantum Cryptography Migration Platform. It provides a modular, production-ready REST API built with FastAPI.

## Folder Structure
```
backend/
├── app/
│   ├── api/           # API routers and endpoints
│   ├── config/        # Environment and application settings
│   ├── core/          # Core utilities like logging and exceptions
│   ├── evaluation/    # Evaluation metrics and tools
│   ├── explainability/# AI explainability modules
│   ├── graph/         # Graph database interaction logic
│   ├── heuristic/     # Heuristic analysis logic
│   ├── ml/            # Machine learning models
│   ├── models/        # Database models (ORM/ODM)
│   ├── scanners/      # Code scanning and parsing logic
│   ├── schemas/       # Pydantic schemas for data validation
│   ├── services/      # Business logic services
│   ├── utils/         # Helper functions
│   └── main.py        # Application entrypoint
├── logs/              # Application log files
├── outputs/           # Generated outputs
├── scripts/           # Utility scripts
├── tests/             # Unit and integration tests
├── uploads/           # Uploaded files
├── .env.example       # Example environment variables
├── docker-compose.yml # Docker compose configuration
├── Dockerfile         # Docker image definition
└── requirements.txt   # Python dependencies
```

## Installation
1. Ensure you have Python 3.12 installed.
2. Clone the repository and navigate to the `backend` directory.
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

## Running locally
Run the development server using Uvicorn directly or via the main script:
```bash
python -m app.main
```
Or using Uvicorn:
```bash
uvicorn app.main:app --reload
```

## Running Docker
To start the application and Neo4j database using Docker Compose:
```bash
docker-compose up -d
```
This will build the backend image and start both the FastAPI server and the Neo4j database.

## API Docs
Once the server is running, the interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
