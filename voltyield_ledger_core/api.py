from fastapi import FastAPI
from .models import TelemetryBatch
from .ledger import record_entry

app = FastAPI()

@app.post("/ingest/")
async def ingest_data(batch: TelemetryBatch):
    record_entry(batch.dict())
    return {"status": "SUCCESS", "message": "Inked to Rail"}
