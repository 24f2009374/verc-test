from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load your telemetry data once
with open("telemetry.json") as f:
    data = json.load(f)

@app.post("/api")
def analyze(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": statistics.quantiles(latencies, n=20)[18],
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return result
