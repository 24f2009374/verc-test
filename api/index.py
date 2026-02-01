from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "telemetry.json"

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)


def compute(payload: dict, telemetry: list[dict]):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]

        if not records:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        latencies_sorted = sorted(latencies)
        idx = max(0, int(0.95 * len(latencies_sorted)) - 1)
        p95 = latencies_sorted[idx]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(p95, 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return result


# ✅ Handle BOTH routes
@app.post("/")
@app.post("/api")
def analyze(payload: dict):
    return compute(payload)
