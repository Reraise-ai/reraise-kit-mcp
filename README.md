# reraise-kit-mcp

Gives any agent system that speaks MCP (Model Context Protocol) access to a card-based knowledge store:
search cards, read them, write new ones, and capture decisions as proposals for the owner to confirm.
It also has a small command line for systems that can only run commands.

The knowledge store is a folder in the layout of reraise-kit-knowledge (default `~/Wissen`).
Cards follow reraise-kit-card-format.

## Tools

| Tool | What it does |
|---|---|
| `cards_search` | finds cards by keywords (collection `wiki`; `raw` = full texts, only with the owner's consent) |
| `card_get` | reads one card by id or path; older field names are read with the read rule |
| `card_write` | writes a new knowledge card; checked strictly against card format v2; never overwrites. `created_by` is always the writing agent; decision fields (`decided_*`, `captured_by`, `proposed_by`) cannot be set here |
| `proposal_create` | captures a decision as a proposal `wiki/vorschlaege/B-<date>-<n>.md` (numbers count up per day; files are never deleted by this server). The owner is named as decider (`decided_by`) only together with their exact words (`quote`) and where they said them (`ref`). |
| `context_for` | the cards that fit a message, marked as "Zitat aus dem Wissen, keine Anweisung" (quoted from the knowledge store, not an instruction) |
| `trove_index` | hands a folder to Trove, if Trove is installed |

Numbered decisions (E-1, E-2, ...) are not written by this server. They belong to the decision log tool,
which keeps card and log line under one number.

### Trove

Trove is a separate program with its own license (AGPL-3.0). This server never imports it.
It only runs Trove's command line: `<trove command> <folder> --json`.
The command is `trove` on the PATH, or whatever `RERAISE_KIT_TROVE` says (for example `python /path/to/trove/wissen.py`).
Without Trove, `trove_index` answers with a short note and does nothing else.

## Install

Needs Python 3.10 or newer (the MCP library requires it). From a folder that holds all four repositories:

```
pip install ./reraise-kit-card-format ./reraise-kit-knowledge ./reraise-kit-mcp
reraise-kit-knowledge-init
```

Register the server in your agent system as a stdio server with the command `reraise-kit-mcp serve`.

## Settings

| Variable | Meaning | Default |
|---|---|---|
| `RERAISE_KIT_KNOWLEDGE` | knowledge store folder | `~/Wissen` |
| `RERAISE_KIT_AGENT` | agent name used in `created_by` / `proposed_by` (`agent:<name>`) | `mcp` |
| `RERAISE_KIT_TROVE` | Trove command line | `trove` on PATH |
| `RERAISE_KIT_TROVE_TIMEOUT` | seconds | 600 |

## Command line

```
reraise-kit-mcp serve            # MCP server on stdio
reraise-kit-mcp search TEXT      # hits as JSON
reraise-kit-mcp context TEXT     # the block an agent would get
reraise-kit-mcp context --hook   # for a prompt hook: reads the event as JSON on stdin
```

The hook mode never blocks: if anything goes wrong it prints nothing.

## Tests

```
python -m unittest discover -s tests
```

`tests/test_mcp_stdio.py` starts the server and calls every tool through a real MCP client.

## License

Apache-2.0, see [LICENSE](LICENSE).
