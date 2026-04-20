#!/usr/bin/env python3
"""
AgroScan Backend Server
Entry point to run the FastAPI application
"""

import uvicorn
import sys


def main():
    """Run the FastAPI server"""
    print("=" * 60)
    print("AgroScan Backend Server")
    print("=" * 60)
    print("Starting server on http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

