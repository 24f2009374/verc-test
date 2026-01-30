from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import statistics
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

app=FastAPI()

from pathlib import Path
import json

BASE_DIR = Path(__file__).parent

@app.post("/api")
def analyze(payload: dict):
    with open(BASE_DIR / "telemetry.json", encoding="utf-8") as f:
        data = json.load(f)

    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0,
            }
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        latencies_sorted = sorted(latencies)
        p95 = latencies_sorted[int(0.95 * (len(latencies_sorted) - 1))]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": p95,
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return result
