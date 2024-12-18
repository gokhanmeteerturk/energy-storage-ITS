## Intelligent Tutoring System for Energy Storage Systems

Backend: FastAPI, SQLAlchemy, SQLite with gokhanmeteerturk/adaptive-shots
Frontend: React, Vite
Ontology from the ontology folder is created using Protege

Current Ontology Url:
https://w3id.org/gokhanmeteerturk/energy-storage-ITS/v1.1/ontology/energy-storage.owx

## Getting Started

1. Clone the repository

```bash
git clone https://github.com/gokhanmeteerturk/energy-storage-ITS.git
```

2. Install dependencies

```bash
cd frontend/energy-storage-ITS
npm install
cd ../../backend
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

3. Run the backend and frontend

```bash
cd backend
uvicorn main:app --reload --port 8000

cd ../frontend/energy-storage-ITS
npm run dev
```
