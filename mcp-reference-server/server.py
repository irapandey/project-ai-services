#!/usr/bin/env python3
"""
MCP Server for Reference Documents API
Exposes the reference documents endpoint as an MCP tool
"""

import json
import os
import warnings
from typing import Any

import httpx
from fastmcp import FastMCP

# Suppress websockets.legacy deprecation warning from FastMCP dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.legacy")


# Configuration
API_BASE_URL = os.getenv("REFERENCE_API_URL", "http://10.20.183.222:5000")
DEFAULT_NUM_CHUNKS_POST_RRF = int(os.getenv("DEFAULT_NUM_CHUNKS_POST_RRF", "10"))
DEFAULT_NUM_DOCS_RERANKER = int(os.getenv("DEFAULT_NUM_DOCS_RERANKER", "3"))
DEFAULT_USE_RERANKER = os.getenv("DEFAULT_USE_RERANKER", "true").lower() == "true"
SERVER_PORT = int(os.getenv("SERVER_PORT", "8003"))


# Create the FastMCP server
mcp = FastMCP("reference-server")


@mcp.tool()
async def reference_documents(
    prompt: str,
    num_chunks_post_rrf: int | None = None,
    num_docs_reranker: int | None = None,
    use_reranker: bool | None = None,
) -> dict[str, Any]:
    """
    Retrieve reference documents for a given prompt using RAG (Retrieval Augmented Generation).
    Searches the knowledge base and returns relevant document chunks.
    
    Args:
        prompt: The search prompt/question to find relevant documents for (required).
        num_chunks_post_rrf: Number of chunks to retrieve after Reciprocal Rank Fusion (default: 10).
        num_docs_reranker: Number of documents to return after reranking (default: 3).
        use_reranker: Whether to use reranking to improve document relevance (default: True).
    
    Returns:
        A dictionary containing:
            - documents: List of relevant document chunks, each with:
                - page_content: The text content of the document chunk
                - filename: The source filename (e.g., "sg248589.pdf")
                - type: The content type (e.g., "text", "table")
                - source: The source/chapter information
                - chunk_id: Unique identifier for the chunk
    """
    if not prompt:
        raise ValueError("prompt cannot be empty")
    
    # Prepare the request payload
    payload: dict[str, Any] = {
        "prompt": prompt,
    }
    
    # Only include optional parameters if explicitly provided
    if num_chunks_post_rrf is not None:
        payload["num_chunks_post_rrf"] = num_chunks_post_rrf
    else:
        payload["num_chunks_post_rrf"] = DEFAULT_NUM_CHUNKS_POST_RRF
    
    if num_docs_reranker is not None:
        payload["num_docs_reranker"] = num_docs_reranker
    else:
        payload["num_docs_reranker"] = DEFAULT_NUM_DOCS_RERANKER
    
    if use_reranker is not None:
        payload["use_reranker"] = use_reranker
    else:
        payload["use_reranker"] = DEFAULT_USE_RERANKER
    
    url = f"{API_BASE_URL}/reference"
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return data
                    
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        raise RuntimeError(f"Error: {error_msg}")
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)}"
        raise RuntimeError(f"Error: {error_msg}")
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        raise RuntimeError(f"Error: {error_msg}")


if __name__ == "__main__":
    # Run the FastMCP server on port 8003 using HTTP transport
    mcp.run(transport="http", host="127.0.0.1", port=SERVER_PORT)

