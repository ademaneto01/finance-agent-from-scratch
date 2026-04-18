from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingestion_yahoo, ingestion_edgar, search, agent

app = FastAPI(title="Financial Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(agent.router)
app.include_router(ingestion_yahoo.router)
app.include_router(ingestion_edgar.router)


@app.get("/")
def root():
    return {"status": "online"}
