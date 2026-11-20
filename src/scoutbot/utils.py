"""Utility functions for the Scoutbot application."""

import json
import logging
from importlib.resources import files

logger = logging.getLogger(__name__)


def load_json(path: str, package: str = "scoutbot") -> dict:
    "Load a JSON file from the specified package and path."
    text = files(package).joinpath(path).read_text()
    return json.loads(text)


def load_tickets(path: str, package: str = "scoutbot") -> list[dict]:
    "Load tickets from the specified package and path."
    return load_json(path, package)


def load_customers(path: str, package: str = "scoutbot") -> dict[str, dict]:
    "Load customers from the specified package and path."
    return load_json(path, package)


def log_block(block) -> None:
    "Log one content block from a model response, depending on its type."
    if block.type == "text":
        logger.debug("Model text: %s", block.text)
    elif block.type == "server_tool_use":
        logger.info("Server tool call : %s(%s)", block.name, block.input)
    elif block.type == "web_fetch_tool_result":
        logger.info("Web fetch result received")
