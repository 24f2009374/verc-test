from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import statistics

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "telemetry.json"

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)


def compute(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 2),
            "p95_latency": round(statistics.quantiles(latencies, n=20)[18], 2),
            "avg_uptime": round(statistics.mean(uptimes), 2),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return result


# ✅ Handle BOTH routes
@app.post("/")
@app.post("/api")
def analyze(payload: dict):
    return compute(payload)
