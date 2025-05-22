import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8080)}"
workers = max(2, multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 90         # seconds
