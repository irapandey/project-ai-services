# MCP Reference Documents Server

An MCP (Model Context Protocol) server that exposes the reference documents API endpoint as an MCP tool.

## Overview

This MCP server wraps the reference documents API endpoint (`http://10.20.186.136:5000/reference`) and makes it available as an MCP tool that can be used by MCP clients. The reference API uses RAG (Retrieval Augmented Generation) to search a knowledge base and return relevant document chunks for a given prompt.

## Features

- Exposes reference document retrieval as an MCP tool
- Configurable via environment variables
- Handles error cases gracefully
- Supports RAG-based document search with optional reranking

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The server can be configured using environment variables:

- `REFERENCE_API_URL`: Base URL for the reference API (default: `http://10.20.186.136:5000`)
- `DEFAULT_NUM_CHUNKS_POST_RRF`: Default number of chunks after Reciprocal Rank Fusion (default: `10`)
- `DEFAULT_NUM_DOCS_RERANKER`: Default number of documents after reranking (default: `3`)
- `DEFAULT_USE_RERANKER`: Whether to use reranking by default (default: `true`)
- `SERVER_PORT`: Port for HTTP transport (default: `8003`)

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
    "reference": {
      "command": "python",
      "args": ["/path/to/mcp-reference-server/server.py"],
      "env": {
        "REFERENCE_API_URL": "http://10.20.186.136:5000"
      }
    }
  }
}
```

### Tool Parameters

The `reference_documents` tool accepts the following parameters:

- `prompt` (required): The search prompt/question to find relevant documents for
- `num_chunks_post_rrf` (optional): Number of chunks to retrieve after Reciprocal Rank Fusion (default: 10)
- `num_docs_reranker` (optional): Number of documents to return after reranking (default: 3)
- `use_reranker` (optional): Whether to use reranking to improve document relevance (default: true)

### Example Request

```json
{
  "prompt": "what is power11"
}
```

### Example Response

```json
{
  "documents": [
    {
      "page_content": "Ch cloud platforms. This combination makes it a versatile choice for enterprises seeking scalable, AI-ready infrastructure.",
      "filename": "sg248589.pdf",
      "type": "text",
      "source": "Chapter: Introduction to Power11 ",
      "chunk_id": "4703759871821069985"
    },
    {
      "page_content": "The and VIOS operating systems. Additionally, it covers firmware and hardware management console requirements...",
      "filename": "sg248589.pdf",
      "type": "table",
      "source": "<table><tbody><tr><td>Notices...</td></tr></tbody></table>",
      "chunk_id": 7197323795142637909
    }
  ]
}
```

## Development

The server is built using the Python MCP SDK (FastMCP) and uses async/await for handling HTTP requests. It follows the same pattern as other MCP servers in this project.

## License

See the project LICENSE file for license information.

