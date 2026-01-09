# MCP ai-services CLI Server

An MCP (Model Context Protocol) server that exposes the `ai-services` CLI
version information as an MCP tool.

## Overview

This MCP server wraps the `ai-services version` command and makes it available
as an MCP tool that can be used by MCP clients (e.g. Claude Desktop).

The tool parses the CLI output and returns:

- `version`
- `git_commit`
- `build_date`
- `raw_output`

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

## Development

The server is built using the Python `fastmcp` SDK and uses `asyncio` to execute
the underlying CLI command. It is intentionally minimal and focused on exposing
version information, but can be extended with additional tools that wrap other
`ai-services` subcommands.


