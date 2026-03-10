"""
Vast.ai PyWorker configuration for generic model server.

This is the PYWORKER_REPO entry point — cloned and run by Vast.ai's start_server.sh.
It proxies HTTP requests to a FastAPI model server running on localhost.

Environment variables:
    MODEL_SERVER_PORT   — port of the local model server (default: 18000)
    MAX_QUEUE_TIME      — max seconds a request can wait in queue (default: 300)
    BENCHMARK_PAYLOAD   — JSON string for benchmark test payload (default: {"echo":"benchmark"})
"""

import json
import os

from vastai import BenchmarkConfig, HandlerConfig, LogActionConfig, Worker, WorkerConfig

MODEL_SERVER_PORT = int(os.environ.get("MODEL_SERVER_PORT", "18000"))
MAX_QUEUE_TIME = float(os.environ.get("MAX_QUEUE_TIME", "300"))
BENCHMARK_PAYLOAD = json.loads(
    os.environ.get("BENCHMARK_PAYLOAD", '{"echo": "benchmark"}')
)


worker_config = WorkerConfig(
    model_server_url="http://127.0.0.1",
    model_server_port=MODEL_SERVER_PORT,
    model_log_file="/var/log/model/server.log",
    handlers=[
        HandlerConfig(
            route="/process",
            allow_parallel_requests=False,
            max_queue_time=MAX_QUEUE_TIME,
            workload_calculator=lambda payload: 100.0,
            benchmark_config=BenchmarkConfig(
                generator=lambda: BENCHMARK_PAYLOAD,
                runs=2,
                concurrency=1,
            ),
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=["Application startup complete."],
        on_error=[
            "Traceback (most recent call last):",
            "RuntimeError:",
            "CUDA error:",
        ],
    ),
)

if __name__ == "__main__":
    Worker(worker_config).run()
