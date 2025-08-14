"""
Test script for PyWinAuto MCP server.

This script tests the MCP server by sending JSON-RPC requests to its stdio interface.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_request(reader, writer, method: str, params: dict = None, request_id: int = 1) -> dict:
    """Send a JSON-RPC request to the MCP server and return the response."""
    # Prepare the request
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    request_str = json.dumps(request)
    
    # Send the request
    message = f"Content-Length: {len(request_str)}\r\n\r\n{request_str}"
    writer.write(message.encode('utf-8'))
    await writer.drain()
    
    # Read the response
    content_length = None
    while True:
        line = await reader.readline()
        if not line:
            break
        line = line.decode('utf-8').strip()
        if not line:
            break
        if line.lower().startswith('content-length:'):
            content_length = int(line.split(':', 1)[1].strip())
    
    if content_length:
        response_data = await reader.read(content_length)
        return json.loads(response_data.decode('utf-8'))
    
    return {"error": "No response received"}

async def test_health_check(reader, writer):
    """Test the health check endpoint."""
    logger.info("Testing health check...")
    response = await send_request(reader, writer, "health_check")
    print("Health check response:", json.dumps(response, indent=2))
    
    if response.get("result", {}).get("status") == "ok":
        logger.info("Health check test passed!")
        return True
    else:
        logger.error(f"Health check test failed: {response}")
        return False

async def test_find_window(reader, writer):
    """Test the find_window endpoint."""
    logger.info("Testing find_window...")
    response = await send_request(
        reader, 
        writer, 
        "find_window",
        {"title": "Program Manager", "class_name": "Progman", "timeout": 5.0}
    )
    print("Find window response:", json.dumps(response, indent=2))
    
    if "result" in response and "window_handle" in response["result"]:
        logger.info("Find window test passed!")
        return True
    else:
        logger.error(f"Find window test failed: {response}")
        return False

async def run_tests():
    """Run all tests."""
    # Start the MCP server as a subprocess
    server_process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "pywinauto_mcp.main",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for the server to start
    await asyncio.sleep(2)
    
    if server_process.returncode is not None:
        logger.error(f"Server process exited with code {server_process.returncode}")
        stderr = await server_process.stderr.read()
        if stderr:
            logger.error(f"Server stderr: {stderr.decode('utf-8')}")
        return False
    
    try:
        # Create a connection to the server's stdio
        reader = asyncio.StreamReader()
        reader_protocol = asyncio.StreamReaderProtocol(reader)
        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            lambda: asyncio.streams.FlowControlMixin(),
            asyncio.subprocess.PIPE
        )
        writer = asyncio.streams.StreamWriter(
            writer_transport, 
            writer_protocol, 
            None, 
            asyncio.get_event_loop()
        )
        
        # Run tests
        test_results = {}
        
        # Test health check
        health_check_passed = await test_health_check(reader, writer)
        test_results["Health Check"] = "PASSED" if health_check_passed else "FAILED"
        
        # Test find_window if health check passed
        if health_check_passed:
            find_window_passed = await test_find_window(reader, writer)
            test_results["Find Window"] = "PASSED" if find_window_passed else "FAILED"
        else:
            test_results["Find Window"] = "SKIPPED (health check failed)"
        
        # Print test results
        print("\nTest Results:")
        print("-" * 50)
        for test_name, result in test_results.items():
            print(f"{test_name}: {result}")
        
        # Return overall success
        return all(result == "PASSED" for result in test_results.values())
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False
        
    finally:
        # Clean up
        if server_process.returncode is None:
            server_process.terminate()
            await server_process.wait()

if __name__ == "__main__":
    asyncio.run(run_tests())
