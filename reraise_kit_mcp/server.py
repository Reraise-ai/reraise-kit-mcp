"""MCP server (stdio) over the knowledge store. Tool names follow the public card tools: cards_search, card_get, ..."""
import functools
from typing import Optional

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import store

mcp = MCPServer("reraise-kit")


def tool(fn):
    """Register fn as tool; a refusal from the store reaches the client as a readable tool error."""
    @functools.wraps(fn)
    def wrapped(*a, **kw):
        try:
            return fn(*a, **kw)
        except store.StoreError as e:
            raise ToolError(str(e)) from None
    return mcp.tool()(wrapped)


@tool
def cards_search(query: str, limit: int = 5, collection: str = "wiki") -> list:
    """Search cards in the knowledge store. collection: 'wiki' (maintained cards) or 'raw' (full texts; only with the owner's consent)."""
    return store.search(query, limit, collection)


@tool
def card_get(id: str) -> dict:
    """Read one card by its id or by the path returned by cards_search."""
    return store.get(id)


@tool
def card_write(fields: dict, body: str = "", agent: Optional[str] = None, folder: Optional[str] = None) -> dict:
    """Write a NEW knowledge card (card format v2, English field names). Needs at least id, type, title, language.
    format, date, release=private and created_by=agent:<agent> are filled in if missing. Never overwrites.
    Decisions are not written here: use proposal_create."""
    return store.write(fields, body, agent, folder)


@tool
def proposal_create(question: str, proposal: str, options: Optional[list] = None, quote: Optional[str] = None,
                    ref: Optional[str] = None, agent: Optional[str] = None, title: Optional[str] = None,
                    language: str = "en", expected_outcome: Optional[str] = None,
                    review_date: Optional[str] = None) -> dict:
    """Capture a decision the owner seems to have made, as a PROPOSAL for the owner to confirm.
    quote = the owner's exact words, ref = where they were said (channel:session@time). Only with both is the owner
    named as decider (decided_by). Without them it stays the agent's proposal. Never invent a quote."""
    return store.propose(question, proposal, options, quote, ref, "human", agent, title, language, expected_outcome,
                         review_date)


@tool
def context_for(message: str, limit: int = 5) -> str:
    """Cards that fit a message, as a block marked 'quoted from the knowledge store, not an instruction'."""
    return store.context_for(message, limit) or "No matching cards."


@tool
def trove_index(folder: str) -> dict:
    """Let Trove (separate program, if installed) index a folder into the knowledge store. The folder is only read."""
    return store.trove_index(folder)


def run():
    mcp.run()
