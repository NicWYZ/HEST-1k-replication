"""Round 6 extension, cheatsheet track: start one confined headless Claude Code child.

Round 6's runner (round6_cheatsheet_child.py) adapted to the container on the
Mac (instruction section 6.5). Every trial, revision, audit and probe is one
`claude -p` process inside a bubblewrap confinement that shows it only its own
trial directory (mounted at /work), with no network except a Unix socket to the
filtering proxy, which allows only the Anthropic API host.

What differs from round 6's command, each recorded in the plan:
- no /opt, /lib64, CA bundle or credential folder is bound. Node, Claude Code
  and Python sit under /usr, and the API's certificate verifies against Node's
  own store, since the filter tunnels TLS unchanged.
- the child authenticates with CLAUDE_CODE_OAUTH_TOKEN, read from the token
  file in the private folder.
- the clean environment of `env -i` is given through the process environment
  of bwrap (which starts from exactly the variables listed) instead of on an
  `env -i` command line, so the token never appears in a process listing.
- `--disable-slash-commands` is kept from round 6 (its flag F11).
- a role chooses the tools and the turn cap, and `--resume` continues a
  writer's session for a revision.

    python round6_cheatsheet_ext_child.py TRIAL_DIR PROMPT_FILE --name NAME
           [--role writer|checker|other] [--resume SESSION_ID] [--log-dir DIR]

Logs go to --log-dir, outside the trial directory. Prints one JSON line.
"""
import argparse
import json
import os
import shutil
import subprocess
import threading
import time
import uuid

TOKEN_FILE = "/private/oauth_token"
PROXY_DIR = "/srv/r6_proxy"
MODEL = "claude-opus-5-5"
ROLE_TOOLS = {"writer": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
              "other": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
              "checker": ["Read", "Write", "Glob"]}
ROLE_TURNS = {"writer": 120, "other": 80, "checker": 80, "revision": 60}


def command(trial_dir, prompt, session_id, role="other", max_turns=None, resume=None,
            model=MODEL, effort="medium"):
    tools = ROLE_TOOLS[role]
    if max_turns is None:
        max_turns = ROLE_TURNS["revision" if resume else role]
    bw = [
        "bwrap", "--unshare-all", "--new-session", "--die-with-parent",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/bin", "/bin", "--ro-bind", "/sbin", "/sbin", "--ro-bind", "/etc", "/etc",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--tmpfs", "/home",
        "--tmpfs", "/srv", "--tmpfs", "/root",
        "--bind", PROXY_DIR, "/run/proxy",
        "--bind", os.path.abspath(trial_dir), "/work", "--chdir", "/work",
        "/run/proxy/start.sh",
    ]
    ident = ["--resume", resume] if resume else ["--session-id", session_id]
    cl = [
        "claude", "--safe-mode", "--disable-slash-commands", "-p", prompt,
        *ident, "--model", model, "--effort", effort,
        "--tools", ",".join(tools),
        "--disallowedTools", "WebFetch", "WebSearch", "Agent",
        "--allowedTools", *tools,
        "--permission-mode", "dontAsk",
        "--max-turns", str(max_turns),
        "--output-format", "stream-json", "--verbose",
    ]
    return bw + cl


def environment(effort="medium", token_file=TOKEN_FILE):
    """Exactly the variables the child gets, the equivalent of `env -i`."""
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/work",
        "HTTPS_PROXY": "http://127.0.0.1:3128", "https_proxy": "http://127.0.0.1:3128",
        "CLAUDE_CODE_EFFORT_LEVEL": effort,
        "CLAUDE_CODE_OAUTH_TOKEN": open(token_file).read().strip(),
    }


def run(trial_dir, prompt, log_dir, name, role="other", max_turns=None, resume=None,
        timeout=4 * 3600, model=MODEL, effort="medium", token_file=TOKEN_FILE):
    os.makedirs(log_dir, exist_ok=True)
    sid = resume or str(uuid.uuid4())
    cmd = command(trial_dir, prompt, sid, role, max_turns, resume, model, effort)
    out = os.path.join(log_dir, f"{name}.stream.jsonl")
    err = os.path.join(log_dir, f"{name}.stderr.txt")
    t0 = time.time()
    # stdout and stderr go through pipes, not file descriptors on the log files,
    # so the child cannot reach the log files through /proc/<pid>/fd (round 6, C0.2)
    with open(out, "wb") as fo, open(err, "wb") as fe:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL, env=environment(effort, token_file))
        pumps = [threading.Thread(target=shutil.copyfileobj, args=(proc.stdout, fo)),
                 threading.Thread(target=shutil.copyfileobj, args=(proc.stderr, fe))]
        for t in pumps:
            t.start()
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            rc = "timeout"
        for t in pumps:
            t.join()
    return {"name": name, "rc": rc, "wall_s": round(time.time() - t0, 1), "session_id": sid,
            "resumed": bool(resume), "role": role, "stream": out, "stderr": err}


def summarise(stream_path):
    """Served model, tools, MCP servers, cost, tokens and turns from a stream."""
    init, result = {}, {}
    for line in open(stream_path, errors="replace"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            init = e
        elif e.get("type") == "result":
            result = e
    u = result.get("usage", {}) or {}
    return {
        "served_model": init.get("model"), "claude_code_version": init.get("claude_code_version"),
        "tools": init.get("tools"), "mcp_servers": init.get("mcp_servers"),
        "plugins": init.get("plugins"), "result_subtype": result.get("subtype"),
        "skills": init.get("skills"), "slash_commands": init.get("slash_commands"),
        "agents": init.get("agents"),
        "is_error": result.get("is_error"), "num_turns": result.get("num_turns"),
        "cost_usd": result.get("total_cost_usd"), "duration_ms": result.get("duration_ms"),
        "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
        "cache_read": u.get("cache_read_input_tokens"), "cache_write": u.get("cache_creation_input_tokens"),
        "result_text": (result.get("result") or "")[:2000],
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("trial_dir")
    ap.add_argument("prompt_file")
    ap.add_argument("--name", required=True)
    ap.add_argument("--role", default="other", choices=sorted(ROLE_TOOLS))
    ap.add_argument("--resume", default=None)
    ap.add_argument("--log-dir", default="/private/logs")
    ap.add_argument("--max-turns", type=int, default=None)
    ap.add_argument("--timeout", type=int, default=4 * 3600)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--effort", default="medium")
    a = ap.parse_args()
    r = run(a.trial_dir, open(a.prompt_file).read(), a.log_dir, a.name, a.role,
            a.max_turns, a.resume, a.timeout, a.model, a.effort)
    r.update(summarise(r["stream"]))
    print(json.dumps(r))
