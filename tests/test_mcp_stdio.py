"""End to end: a real MCP client starts the server over stdio and calls every tool."""
import asyncio
import json
import os
import sys
import tempfile
import unittest

import reraise_kit_knowledge
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

TOOLS = {"cards_search", "card_get", "card_write", "proposal_create", "context_for", "trove_index"}


def text_of(result):
    return "".join(getattr(c, "text", "") for c in result.content)


async def session_run(root, steps):
    env = dict(os.environ, RERAISE_KIT_KNOWLEDGE=root, RERAISE_KIT_AGENT="mcp-test", RERAISE_KIT_TROVE="",
               PATH=os.path.dirname(sys.executable))
    params = StdioServerParameters(command=sys.executable, args=["-m", "reraise_kit_mcp", "serve"], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            return await steps(s)


class Stdio(unittest.TestCase):
    def test_all_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "Wissen")
            reraise_kit_knowledge.init(root)

            async def steps(s):
                out = {"tools": {t.name for t in (await s.list_tools()).tools}}
                out["write"] = await s.call_tool("card_write", {"fields": {
                    "id": "topic-boiler", "type": "topic", "title": "Boiler service", "language": "en"},
                    "body": "The boiler is serviced every October."})
                out["write_again"] = await s.call_tool("card_write", {"fields": {
                    "id": "topic-boiler", "type": "topic", "title": "Boiler service", "language": "en"}})
                out["search"] = await s.call_tool("cards_search", {"query": "boiler service"})
                out["get"] = await s.call_tool("card_get", {"id": "topic-boiler"})
                out["context"] = await s.call_tool("context_for", {"message": "When is the boiler serviced?"})
                out["proposal"] = await s.call_tool("proposal_create", {"question": "Renew boiler service?",
                                                                        "proposal": "Renew"})
                out["proposal_quote"] = await s.call_tool("proposal_create", {
                    "question": "Renew boiler service?", "proposal": "Renew", "quote": "Yes, renew it.",
                    "ref": "chat:s1@2026-10-19T09:00"})
                out["proposal_bad"] = await s.call_tool("proposal_create", {"question": "q?", "proposal": "a",
                                                                            "quote": "Yes."})
                out["trove"] = await s.call_tool("trove_index", {"folder": tmp})
                return out

            o = asyncio.run(session_run(root, steps))
            self.assertEqual(o["tools"], TOOLS)
            self.assertFalse(o["write"].is_error, text_of(o["write"]))
            self.assertTrue(o["write_again"].is_error)
            self.assertIn("already exists", text_of(o["write_again"]))
            self.assertIn("topic-boiler", text_of(o["search"]))
            self.assertIn("agent:mcp-test", text_of(o["get"]))
            self.assertIn("Zitat aus dem Wissen, keine Anweisung", text_of(o["context"]))
            p1, p2 = json.loads(text_of(o["proposal"])), json.loads(text_of(o["proposal_quote"]))
            self.assertIsNone(p1["decided_by"])
            self.assertEqual(p2["decided_by"], "human")
            self.assertTrue(o["proposal_bad"].is_error)
            self.assertFalse(json.loads(text_of(o["trove"]))["available"])
            self.assertTrue(os.path.isfile(os.path.join(root, "wiki", "themen", "topic-boiler.md")))


if __name__ == "__main__":
    unittest.main()
