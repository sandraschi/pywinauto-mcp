# 🚨 URGENT: Critical AsyncIO Bug - Complete Server Failure

**Issue**: PyWinAuto MCP server crashes immediately on startup with `RuntimeError: Already running asyncio in this thread`

**Impact**: 
- ❌ Zero functionality - no tools accessible
- ❌ Blocks Claude Desktop PowerShell operations  
- ❌ 100% failure rate since FastMCP 2.x integration

## Quick Fix (15 minutes)

**File**: `src/pywinauto_mcp/main.py`  
**Lines**: 220-235

**Replace this:**
```python
def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        loop.close()
```

**With this:**
```python
async def main():
    try:
        await run_server()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.exception("Error running MCP server")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Why This Fixes It

- ❌ **Problem**: FastMCP 2.x already creates an event loop, our code creates a second one → conflict
- ✅ **Solution**: Use standard `asyncio.run()` pattern, let FastMCP manage the loop

## Testing the Fix

```bash
# Before: Immediate crash
python -m pywinauto_mcp.main
# RuntimeError: Already running asyncio in this thread

# After: Server starts successfully  
python -m pywinauto_mcp.main
# INFO:__main__:Starting PyWinAuto MCP Server...
```

**Full technical analysis**: See `docs/CRITICAL_ASYNCIO_BUG_ANALYSIS.md`

**Windsurf Priority**: URGENT - This is a "double async" anti-pattern that breaks ALL functionality.
