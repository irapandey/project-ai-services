#!/usr/bin/env python3
"""
MCP Server for Chat Completions API
Exposes the chat completions endpoint as an MCP tool
"""

import json
import os
from typing import Any

import httpx
from fastmcp import FastMCP


# Configuration
API_BASE_URL = os.getenv("CHAT_API_URL", "http://10.20.188.204:5000")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "ibm-granite/granite-3.3-8b-instruct")
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.0"))
DEFAULT_REPETITION_PENALTY = float(os.getenv("DEFAULT_REPETITION_PENALTY", "1.1"))
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


# Create the FastMCP server
mcp = FastMCP("chat-completions-server")


@mcp.tool()
async def chat_completions(
    user_input: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    repetition_penalty: float = DEFAULT_REPETITION_PENALTY,
    stop: list[str] | None = None,
    stream: bool = True
) -> str:
    """
    Send a chat completion request to the AI model. Supports streaming responses.
    
    Args:
        messages: Array of message objects with role and content. Each message should have 'role' (user/assistant/system) and 'content' (string).
        model: The model to use for completion.
        max_tokens: Maximum number of tokens to generate.
        temperature: Sampling temperature (0.0 to 2.0).
        repetition_penalty: Repetition penalty factor.
        stop: Stop sequences.
        stream: Whether to stream the response.
    
    Returns:
        The completion text from the AI model.
    """
    if not user_input:
        raise ValueError("messages cannot be empty")
    
    # Use default stop sequences if not provided
    if stop is None:
        stop = ["Context:", "Question:", "\nContext:", "\nAnswer:", "\nQuestion:", "Answer:"]
    
    # Prepare the request payload
    payload = {
        "messages": [{"role": "user", "content": user_input}],
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "repetition_penalty": repetition_penalty,
        "stop": ["Context:", "Question:", "\nContext:", "\nAnswer:", "\nQuestion:", "Answer:"],
        "stream": stream
    }
    
    url = f"{API_BASE_URL}/v1/chat/completions"
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            if stream:
                # Handle streaming response
                response_text = ""
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        response_text += content
                            except json.JSONDecodeError:
                                continue
                
                return response_text
            else:
                # Handle non-streaming response
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract the completion text
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    return content
                else:
                    return json.dumps(data, indent=2)
                    
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
    # Run the FastMCP server on port 5000 using HTTP transport
    mcp.run(transport="http", host="127.0.0.1", port=SERVER_PORT)

