"""Extension declaration, capabilities, health check for Pleo Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "pleo-connector",
    version="0.1.0",
    display_name="Pleo",
    icon="icon.svg",
    capabilities=["pleo:manage"],
    description="Official Imperal connector for Pleo (C29. Expense Management & Corporate Cards). Manage operations securely."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("pleo_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Pleo connection(s) configured." if count else "Not connected yet."
    }
