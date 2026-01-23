# MCP ai-services CLI Server

An MCP (Model Context Protocol) server that exposes the `ai-services` CLI commands as MCP tools.

## Overview

This MCP server wraps several `ai-services` CLI commands and makes them available
as MCP tools that can be used by MCP clients (e.g. Claude Desktop).

The server provides three tools:

1. **`ai_services_version`** - Returns version information from the CLI
2. **`ai_services_templates_info`** - Lists available application templates
3. **`ai_services_template_images`** - Lists container images for a specific template

## Installation

1. Create and activate a Python environment (optional but recommended).
2. Install the required dependencies:

```bash
cd /Users/ira/OpenSource/project-ai-services/mcp-ai-services
pip install -r requirements.txt
```

Make sure the `ai-services` CLI binary is built and either:

- available on your `PATH` as `ai-services`, or
- referenced via the `AI_SERVICES_CLI_PATH` environment variable.

## Configuration

The server can be configured using environment variables:

- `AI_SERVICES_CLI_PATH`: Path to the `ai-services` binary
  (default: `ai-services` on `PATH`).
- `SERVER_PORT`: Port for the optional HTTP transport used for local testing
  (default: `8001`).

## Usage

### Running the Server (for MCP stdio clients)

Most MCP clients (like Claude Desktop) will run the server via stdio, so you
typically just configure the command and arguments in the client config:

```json
{
  "mcpServers": {
    "ai-services-cli": {
      "command": "python",
      "args": ["/Users/ira/OpenSource/project-ai-services/mcp-ai-services/server.py"],
      "env": {
        "AI_SERVICES_CLI_PATH": "/usr/local/bin/ai-services"
      }
    }
  }
}
```

### Local HTTP Testing

For quick local testing without an MCP client, you can run:

```bash
cd /Users/ira/OpenSource/project-ai-services/mcp-ai-services
python server.py
```

This starts an HTTP server on `127.0.0.1:8001`. Refer to the `fastmcp`
documentation for details on calling tools over HTTP.

## Exposed Tools

### `ai_services_version`

**Description**: Returns version information from the `ai-services` CLI.

**Parameters**:

- `binary_path` (optional, string): Explicit path to the `ai-services` binary.
  If omitted, the server uses `AI_SERVICES_CLI_PATH` or `ai-services` on `PATH`.

**Result**:

```json
{
  "version": "v0.1.0",
  "git_commit": "abcdef123456",
  "build_date": "2026-01-09T12:34:56Z",
  "raw_output": "Version: v0.1.0\nGitCommit: abcdef123456\nBuildDate: 2026-01-09T12:34:56Z"
}
```

### `ai_services_templates_info`

**Description**: Lists all available application templates from the `ai-services` CLI.

**Parameters**:

- `binary_path` (optional, string): Explicit path to the `ai-services` binary.
  If omitted, the server uses `AI_SERVICES_CLI_PATH` or `ai-services` on `PATH`.

**Result**:

```json
{
  "count": 3,
  "templates": ["fastapi", "go-service", "python-service"],
  "raw_output": "Available application templates:\n- fastapi\n- go-service\n- python-service"
}
```

### `ai_services_template_images`

**Description**: Lists container images used by a specific application template.

**Parameters**:

- `template_name` (required, string): Name of the application template.
- `binary_path` (optional, string): Explicit path to the `ai-services` binary.
  If omitted, the server uses `AI_SERVICES_CLI_PATH` or `ai-services` on `PATH`.

**Result**:

```json
{
  "template": "fastapi",
  "count": 2,
  "images": ["python:3.11-slim", "nginx:alpine"],
  "raw_output": "Container images for application template 'fastapi':\n- python:3.11-slim\n- nginx:alpine"
}
```

## Development

The server is built using the Python `fastmcp` SDK and uses `asyncio` to execute
the underlying CLI commands. The server can be extended with additional tools that
wrap other `ai-services` subcommands by following the existing pattern:

1. Create an async helper function (e.g., `_run_ai_services_<command>`) that
   executes the CLI command and parses the output.
2. Create an MCP tool function decorated with `@mcp.tool()` that calls the helper
   and handles parameter validation.
3. Update this README to document the new tool.


