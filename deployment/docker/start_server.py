#!/usr/bin/env python3
"""
Startup script for Enhanced SciRAG API server.
"""
import sys
import os
sys.path.append('/app')

from scirag.api.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
