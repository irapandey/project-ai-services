#!/usr/bin/env python3
"""
MCP Server for the ai-services CLI.

Exposes tools that wrap the ai-services CLI:
- Version information
- Application templates information
- Container images for a given application template
"""

import asyncio
import os
from typing import Any

from fastmcp import FastMCP


AI_SERVICES_CLI_PATH = os.getenv("AI_SERVICES_CLI_PATH", "ai-services")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))


mcp = FastMCP("ai-services-cli-server")


async def _run_ai_services_cmd(
    binary_path: str,
    *args: str,
) -> tuple[str, str, int]:
    """
    Run the ai-services CLI with the given arguments and return stdout, stderr and exit code.
    """
    process = await asyncio.create_subprocess_exec(
        binary_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_bytes, stderr_bytes = await process.communicate()

    stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
    stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

    return stdout, stderr, process.returncode


async def _run_ai_services_version(binary_path: str) -> dict[str, Any]:
    """
    Run the ai-services CLI `version` command and parse its output.
    """
    stdout, stderr, code = await _run_ai_services_cmd(binary_path, "version")

    if code != 0:
        raise RuntimeError(
            f"ai-services CLI exited with code {code}. "
            f"stdout: {stdout or '<empty>'}; stderr: {stderr or '<empty>'}"
        )

    combined_output = "\n".join([s for s in (stdout, stderr) if s])

    version = "unknown"
    git_commit = "unknown"
    build_date: str | None = None

    for line in combined_output.splitlines():
        line = line.strip()
        if line.lower().startswith("version:"):
            version = line.split(":", 1)[1].strip() or version
        elif line.lower().startswith("gitcommit:"):
            git_commit = line.split(":", 1)[1].strip() or git_commit
        elif line.lower().startswith("builddate:"):
            build_date_value = line.split(":", 1)[1].strip()
            build_date = build_date_value or build_date

    return {
        "version": version,
        "git_commit": git_commit,
        "build_date": build_date,
        "raw_output": combined_output,
    }


async def _run_ai_services_application_templates(binary_path: str) -> dict[str, Any]:
    """
    Run `ai-services application templates` and parse the available templates.
    """
    stdout, stderr, code = await _run_ai_services_cmd(
        binary_path,
        "application",
        "templates",
    )

    if code != 0:
        raise RuntimeError(
            f"ai-services CLI (application templates) exited with code {code}. "
            f"stdout: {stdout or '<empty>'}; stderr: {stderr or '<empty>'}"
        )

    combined_output = "\n".join([s for s in (stdout, stderr) if s])

    templates: list[str] = []
    in_list = False

    for line in combined_output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.lower().startswith("available application templates"):
            in_list = True
            continue

        if in_list:
            if not stripped.startswith("- "):
                # Stop if we hit something that doesn't look like a template entry
                # after we've begun listing.
                continue

            # Template line format: "- <name>"
            name = stripped[2:].strip()
            if name:
                templates.append(name)

    return {
        "count": len(templates),
        "templates": templates,
        "raw_output": combined_output,
    }


async def _run_ai_services_image_list(
    binary_path: str,
    template_name: str,
) -> dict[str, Any]:
    """
    Run `ai-services application image list -t <template>` and parse image names.
    """
    stdout, stderr, code = await _run_ai_services_cmd(
        binary_path,
        "application",
        "image",
        "list",
        "--template",
        template_name,
    )

    if code != 0:
        raise RuntimeError(
            f"ai-services CLI (application image list) exited with code {code}. "
            f"stdout: {stdout or '<empty>'}; stderr: {stderr or '<empty>'}"
        )

    combined_output = "\n".join([s for s in (stdout, stderr) if s])

    images: list[str] = []
    in_list = False

    for line in combined_output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("Container images for application template"):
            in_list = True
            continue

        if in_list:
            if not stripped.startswith("- "):
                continue

            image = stripped[2:].strip()
            if image:
                images.append(image)

    return {
        "template": template_name,
        "count": len(images),
        "images": images,
        "raw_output": combined_output,
    }


@mcp.tool()
async def ai_services_version(binary_path: str | None = None) -> dict[str, Any]:
    """
    Get version information from the ai-services CLI.

    Args:
        binary_path: Optional explicit path to the ai-services binary. If not
            provided, uses the AI_SERVICES_CLI_PATH environment variable or
            falls back to 'ai-services' on PATH.

    Returns:
        A dictionary containing:
            - version: The ai-services version string.
            - git_commit: The git commit hash used to build the binary.
            - build_date: The build date string (if available).
            - raw_output: The raw combined stdout/stderr from the CLI call.
    """
    selected_binary = binary_path or AI_SERVICES_CLI_PATH

    if not selected_binary:
        raise ValueError(
            "No ai-services binary specified. "
            "Set AI_SERVICES_CLI_PATH or pass binary_path explicitly."
        )

    return await _run_ai_services_version(selected_binary)


@mcp.tool()
async def ai_services_templates_info(
    binary_path: str | None = None,
) -> dict[str, Any]:
    """
    Get information about available application templates from the ai-services CLI.

    Args:
        binary_path: Optional explicit path to the ai-services binary. If not
            provided, uses the AI_SERVICES_CLI_PATH environment variable or
            falls back to 'ai-services' on PATH.

    Returns:
        A dictionary containing:
            - count: Number of available templates.
            - templates: List of template names.
            - raw_output: Raw combined stdout/stderr from the CLI call.
    """
    selected_binary = binary_path or AI_SERVICES_CLI_PATH

    if not selected_binary:
        raise ValueError(
            "No ai-services binary specified. "
            "Set AI_SERVICES_CLI_PATH or pass binary_path explicitly."
        )

    return await _run_ai_services_application_templates(selected_binary)


@mcp.tool()
async def ai_services_template_images(
    template_name: str,
    binary_path: str | None = None,
) -> dict[str, Any]:
    """
    Get container images used by a specific application template.

    Args:
        template_name: Name of the application template (required).
        binary_path: Optional explicit path to the ai-services binary. If not
            provided, uses the AI_SERVICES_CLI_PATH environment variable or
            falls back to 'ai-services' on PATH.

    Returns:
        A dictionary containing:
            - template: The template name.
            - count: Number of images found.
            - images: List of image references.
            - raw_output: Raw combined stdout/stderr from the CLI call.
    """
    if not template_name:
        raise ValueError("template_name is required and cannot be empty")

    selected_binary = binary_path or AI_SERVICES_CLI_PATH

    if not selected_binary:
        raise ValueError(
            "No ai-services binary specified. "
            "Set AI_SERVICES_CLI_PATH or pass binary_path explicitly."
        )

    return await _run_ai_services_image_list(selected_binary, template_name)


if __name__ == "__main__":
    # Run the FastMCP server using HTTP transport by default, which can be
    # useful for local testing. MCP clients typically use stdio transport.
    mcp.run(transport="http", host="127.0.0.1", port=SERVER_PORT)


