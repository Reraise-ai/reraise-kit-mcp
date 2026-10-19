"""reraise-kit-mcp serve            run the MCP server on stdio
reraise-kit-mcp context --hook   read a Claude Code UserPromptSubmit event on stdin, print matching cards as context
reraise-kit-mcp context TEXT     print matching cards for TEXT
reraise-kit-mcp search TEXT      print search hits as JSON"""
import json
import sys

from . import store


def _hook():
    """Fail-silent: any problem means no cards, never a blocked prompt."""
    try:
        data = json.loads(sys.stdin.read() or "{}")
        prompt = data.get("prompt") if isinstance(data, dict) else None
        if not isinstance(prompt, str) or len(prompt.strip()) < 8:
            return 0
        block = store.context_for(prompt)
        if block:
            sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                                "additionalContext": block}}, ensure_ascii=False))
    except Exception:
        pass
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["serve"]:
        from .server import run
        run()
        return 0
    if args[:2] == ["context", "--hook"]:
        return _hook()
    if len(args) >= 2 and args[0] in ("context", "search"):
        text = " ".join(args[1:])
        try:
            out = store.context_for(text) if args[0] == "context" else json.dumps(store.search(text), ensure_ascii=False, indent=1)
        except store.StoreError as e:
            print("error: %s" % e, file=sys.stderr)
            return 1
        print(out or "No matching cards.")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
