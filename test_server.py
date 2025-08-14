"""
Test script for PyWinAuto MCP server.

This script sends a health check request to the MCP server and prints the response.
"""
import subprocess
import json
import time

def test_health_check():
    """Test the health check endpoint of the MCP server."""
    # Start the server as a subprocess
    server_process = subprocess.Popen(
        ["python", "-m", "pywinauto_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    try:
        # Give the server a moment to start
        time.sleep(2)
        
        # Prepare the JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "method": "health_check",
            "params": {},
            "id": 1
        }
        request_str = json.dumps(request)
        
        # Send the request to the server
        print(f"Sending request: {request_str}")
        server_process.stdin.write(f"Content-Length: {len(request_str)}\r\n\r\n{request_str}")
        server_process.stdin.flush()
        
        # Read the response
        response = server_process.stdout.readline()
        print(f"Response: {response}")
        
        # Clean up
        server_process.terminate()
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        server_process.terminate()
        return None

if __name__ == "__main__":
    test_health_check()
