import sys
import subprocess
import json

# Test if pywinauto-mcp starts without JSON parsing errors
try:
    # Run the server and send a test message
    process = subprocess.Popen(
        [sys.executable, "-m", "src.pywinauto_mcp.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=r"D:\Dev\repos\pywinauto-mcp",
        text=True
    )
    
    # Send a simple initialize message
    test_msg = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"roots": {"listChanged": True}},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        },
        "id": 1
    }
    
    # Send message and wait for response
    stdout, stderr = process.communicate(input=json.dumps(test_msg) + "\n", timeout=10)
    
    print("✅ STDOUT (should be valid JSON):")
    print(repr(stdout))
    print("\n🔧 STDERR (logs should go here):")
    print(repr(stderr))
    
    # Try to parse the stdout as JSON
    if stdout.strip():
        try:
            response = json.loads(stdout.strip())
            print("\n🎯 SUCCESS: Valid JSON response received!")
            print(f"Response: {response}")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON PARSING ERROR: {e}")
            print(f"Raw stdout: {repr(stdout)}")
    else:
        print("\n⚠️  No stdout received")
        
except subprocess.TimeoutExpired:
    print("⏰ Timeout - server took too long to respond")
    process.kill()
except Exception as e:
    print(f"❌ Test failed: {e}")
