#!/bin/bash
# Wrapper script to run the MCP server from its own directory

cd "$(dirname "$0")"
exec .venv/bin/python3 server.py
