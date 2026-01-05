# MCP Chat Completions Server

An MCP (Model Context Protocol) server that exposes the chat completions API endpoint as an MCP tool.

## Overview

This MCP server wraps the chat completions API endpoint (`http://10.20.188.204:3000/v1/chat/completions`) and makes it available as an MCP tool that can be used by MCP clients.

## Features

- Exposes chat completions as an MCP tool
- Supports streaming and non-streaming responses
- Configurable via environment variables
- Handles error cases gracefully

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The server can be configured using environment variables:

- `CHAT_API_URL`: Base URL for the chat API (default: `http://10.20.188.204:5000`)
- `DEFAULT_MODEL`: Default model to use (default: `ibm-granite/granite-3.3-8b-instruct`)
- `DEFAULT_MAX_TOKENS`: Default maximum tokens (default: `512`)
- `DEFAULT_TEMPERATURE`: Default temperature (default: `0.0`)
- `DEFAULT_REPETITION_PENALTY`: Default repetition penalty (default: `1.1`)

## Usage

### Running the Server

The server uses stdio for communication with MCP clients. Run it as:

```bash
python server.py
```

### MCP Client Configuration

To use this server with an MCP client (like Claude Desktop), add it to your MCP configuration file:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chat-completions": {
      "command": "python",
      "args": ["/path/to/mcp-chat-server/server.py"],
      "env": {
        "CHAT_API_URL": "http://10.20.188.204:8000",
        "DEFAULT_MODEL": "ibm-granite/granite-3.3-8b-instruct"
      }
    }
  }
}
```

### Tool Parameters

The `chat_completions` tool accepts the following parameters:

- `messages` (required): Array of message objects with `role` and `content` fields
- `model` (optional): Model identifier (defaults to configured default)
- `max_tokens` (optional): Maximum tokens to generate (default: 512)
- `temperature` (optional): Sampling temperature 0.0-2.0 (default: 0.0)
- `repetition_penalty` (optional): Repetition penalty factor (default: 1.1)
- `stop` (optional): Array of stop sequences
- `stream` (optional): Whether to stream the response (default: true)

### Example Request

```json
{
  "messages": [
    {"role": "user", "content": "What is artificial intelligence?"}
  ],
  "model": "ibm-granite/granite-3.3-8b-instruct",
  "max_tokens": 512,
  "temperature": 0.0,
  "repetition_penalty": 1.1,
  "stream": true
}
```

## Development

The server is built using the Python MCP SDK and uses async/await for handling HTTP requests. It supports both streaming and non-streaming responses from the underlying API.

## License

See the project LICENSE file for license information.

