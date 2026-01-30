import json, csv, statistics
import numpy as np
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length=int(self.headers["Content-Length"])
        body=self.rfile.read(length)
        payload=json.loads(body)

        regions=payload["regions"]
        threshold=payload["threshold_ms"]
        data=[]

        with open("q-vercel-latency.json") as f:
            reader=csv.DictReader(f)
            for row in reader:
                data.append({
                    "region": row["region"],
                    "latency": float(row["latency"]),
                    "uptime": float(row["uptime"])
                })
        result={}

        for region in regions:
            rows = [r for r in data if r["region"] == region]

            latencies = [r["latency"] for r in rows]
            uptimes = [r["uptime"] for r in rows]

            result[region] = {
                "avg_latency": statistics.mean(latencies),
                "p95_latency": float(np.percentile(latencies, 95)),
                "avg_uptime": statistics.mean(uptimes),
                "breaches": sum(1 for l in latencies if l > threshold)
            }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

