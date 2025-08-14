"""
Test script for PyWinAuto MCP server.

This script sends a health check request to the MCP server and prints the response.
"""
import json
import sys
import time

def send_request(method: str, params: dict = None, request_id: int = 1) -> dict:
    """Send a JSON-RPC request to the MCP server."""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    
    # Print the request to stdout (which is connected to the server's stdin)
    request_str = json.dumps(request)
    print(f"Content-Length: {len(request_str)}\r\n\r\n{request_str}", flush=True)
    
    # Read the response from stdin
    content_length = None
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        if line.startswith("Content-Length:"):
            content_length = int(line.split(":")[1].strip())
    
    if content_length:
        response = sys.stdin.read(content_length)
        return json.loads(response)
    
    return {"error": "No response received"}

if __name__ == "__main__":
    # Test health check
    print("Sending health check request...")
    response = send_request("health_check")
    print("Response:", json.dumps(response, indent=2))
