"""MCP Tools API endpoints for PyWinAutoMCP.

This module provides FastAPI routes for discovering and executing MCP tools
directly from the webapp, enabling real application control.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Use absolute import to match pywinauto_mcp structure
from pywinauto_mcp.app import app

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router with OpenAPI tags
router = APIRouter(tags=["tools"], prefix="/v1/tools")


# Request/Response Models
class ToolParameter(BaseModel):
    """Information about a tool parameter."""

    name: str
    type: str
    description: str | None = None
    default: Any | None = None
    required: bool = True


class ToolInfo(BaseModel):
    """Information about an MCP tool."""

    name: str = Field(..., description="Unique tool name")
    description: str = Field(..., description="Human-readable description")
    parameters: list[ToolParameter] = Field(
        default_factory=list, description="List of tool parameters"
    )


class ToolCallRequest(BaseModel):
    """Request model for calling an MCP tool."""

    name: str = Field(..., description="Name of the tool to call")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Arguments to pass to the tool"
    )


class ToolCallResponse(BaseModel):
    """Response model for a tool call."""

    status: str = Field(..., description="Status of the tool call (success/error)")
    result: Any = Field(None, description="Result of the tool call")
    message: str | None = Field(None, description="Optional status message")


# API Endpoints
@router.get("/", response_model=list[ToolInfo])
async def list_tools() -> list[ToolInfo]:
    """List all registered MCP tools for this server.

    This enables the webapp to dynamically discover available functionality.
    """
    try:
        if not app:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FastMCP app not initialized",
            )

        tools: list[ToolInfo] = []

        # FastMCP 2.13.1 internal tool manager access
        # This matches the get_registered_tools() logic in main.py
        tool_sources = []
        if hasattr(app, "_tool_manager") and hasattr(app._tool_manager, "tools"):
            tool_sources = list(app._tool_manager.tools.values())
        elif hasattr(app, "_tools"):
            tool_sources = list(app._tools.values())

        for tool in tool_sources:
            params = []
            # Extract parameter info if available (FastMCP 2.13.1 specific)
            if hasattr(tool, "parameters"):
                # FastMCP internal schema parsing
                schema = (
                    tool.parameters.get("properties", {}) if hasattr(tool, "parameters") else {}
                )
                required_list = (
                    tool.parameters.get("required", []) if hasattr(tool, "parameters") else []
                )

                for p_name, p_info in schema.items():
                    params.append(
                        ToolParameter(
                            name=p_name,
                            type=p_info.get("type", "any"),
                            description=p_info.get("description"),
                            default=None,  # FastMCP doesn't expose defaults easily in the schema
                            required=p_name in required_list,
                        )
                    )

            tools.append(
                ToolInfo(name=tool.name, description=tool.description or "", parameters=params)
            )

        return tools

    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {str(e)}",
        )


@router.post("/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """Execute a registered MCP tool.

    This provides a direct bridge for the webapp to perform real-world actions.
    """
    try:
        if not app:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FastMCP app not initialized",
            )

        logger.info(f"Calling tool via API: {request.name} with args: {request.arguments}")

        # Execute the tool using app.call_tool (FastMCP standard)
        result = await app.call_tool(request.name, request.arguments)

        return ToolCallResponse(
            status="success", result=result, message=f"Tool {request.name} executed successfully"
        )

    except ValueError as e:
        # Usually tool not found or invalid arguments
        logger.warning(f"Validation error calling tool {request.name}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error calling tool {request.name}: {str(e)}", exc_info=True)
        return ToolCallResponse(status="error", message=str(e))
