"""Utility functions for the Scoutbot application."""

import json
from importlib.resources import files


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
