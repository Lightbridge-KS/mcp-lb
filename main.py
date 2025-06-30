#!/usr/bin/env python3
"""
Main entry point for the Lightbridge-KS Personal MCP Server.

This script initializes and runs the MCP server with all available tools.
"""

from mcp_lb.fs import mcp

if __name__ == "__main__":
    mcp.run()
