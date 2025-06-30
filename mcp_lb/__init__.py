# src/mcp_lb/__init__.py
"""
Lightbridge-KS Personal MCP Server Package

A Model Context Protocol (MCP) server providing tools for file operations and
data processing utilities.
"""

__version__ = "0.1.0"
__author__ = "Kittipos Sirivongrungson"
__description__ = "Personal MCP server with file operations and data processing tools"


# Import all tools so they can be accessed easily
from .fs import rename_files_from_excel

# Define what gets imported with "from mcp_lb.tools import *"
__all__ = [
    # File operation tools
    "rename_files_from_excel",
]
