#!/usr/bin/env python
"""
Start backend with debug logging enabled
"""
import logging
import sys

# Configure logging BEFORE importing app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_logs.txt', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to INFO
logging.getLogger('app.modules.ai.service').setLevel(logging.INFO)
logging.getLogger('app.modules.ai.router').setLevel(logging.INFO)
logging.getLogger('app.modules.cv.router').setLevel(logging.INFO)
logging.getLogger('app.modules.cv.service').setLevel(logging.INFO)

print("✅ Debug logging configured!")
print("📝 Logs will be written to: debug_logs.txt")
print("🚀 Starting backend...\n")

# Now start uvicorn
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
