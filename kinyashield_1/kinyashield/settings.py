"""Read configuration from environment variables first, then Streamlit secrets. Never hard-code or print secret values."""
from __future__ import annotations
import os


def get(name: str, default: str = "") -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st
        value = str(st.secrets.get(name, "")).strip()
    except Exception:       # no secrets file, or streamlit not installed (tests)
        value = ""
    return value or default


def flag(name: str, default: bool = False) -> bool:
    v = get(name, "")
    if not v:
        return default
    return v.lower() in {"1", "true", "yes", "on"}


def number(name: str, default: int = 0) -> int:
    try:
        return int(get(name, str(default)) or default)
    except ValueError:
        return default
