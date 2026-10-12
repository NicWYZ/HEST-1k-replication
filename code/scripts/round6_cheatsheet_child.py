"""Round 6 cheatsheet track: start one confined headless Claude Code child.

Every trial and every probe is one `claude -p` process inside a bubblewrap
confinement that shows it only its own trial directory (mounted at /work),
with no network except a Unix socket to the filtering proxy, which allows
only the Anthropic API host (instruction section 6.4).

Departures from the instruction's command, recorded in the plan:
- the CA bundle is bound after `--tmpfs /root`, because it lives under /root
  and a bind made before the tmpfs is hidden by it (flag F6).
- `--disable-slash-commands` is added, because `--safe-mode` still lists
  Claude Code's bundled skills in the session (flag F11).
- no authentication variables are passed by default: C0.1's leave-one-out
  test found that the child authenticates with none of them (flag F3).
- reasoning effort is a parameter. C0 and the C1 pilot ran at high; from C2
  on every trial runs at medium (C1 memo, section 3.1), which is the default.

    python round6_cheatsheet_child.py TRIAL_DIR MODEL PROMPT_FILE [--max-turns 80]
           [--auth-vars VAR ...] [--timeout SECONDS]

Writes TRIAL_DIR/../<id>.stream.jsonl and .stderr.txt next to (not inside)
the trial directory when --log-dir is given, else into --log-dir default
/srv/r6_private/logs. Prints one JSON line with rc, wall seconds, session id.
"""
import argparse
import json
import os
import shutil
import subprocess
import threading
import time
import uuid

CA_BUNDLE = "/root/.ccr/ca-bundle.crt"
AUTH_DIR = "/home/claude/.claude/remote"
PROXY_DIR = "/srv/r6_proxy"
DEFAULT_AUTH_VARS = [
    "ANTHROPIC_BASE_URL", "CLAUDE_CODE_REMOTE", "CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE",
    "CLAUDE_SESSION_INGRESS_TOKEN_FILE", "CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST",
    "CLAUDE_CODE_ACCOUNT_UUID", "CLAUDE_CODE_ORGANIZATION_UUID", "CLAUDE_CODE_USE_CCR_V2",
    "CLAUDE_CODE_PROXY_RESOLVES_HOSTS", "CLAUDE_CODE_ENTRYPOINT", "SESSION_INGRESS_URL",
    "CLAUDE_CODE_REMOTE_SESSION_ID", "CLAUDE_CODE_SESSION_ID",
]
TOOLS = "Bash,Read,Write,Edit,Glob,Grep"


def command(trial_dir, model, prompt, session_id, max_turns, auth_vars, effort="medium"):
    auth_env = [f"{v}={os.environ[v]}" for v in auth_vars if v in os.environ]
    bw = [
        "bwrap", "--unshare-all", "--new-session", "--die-with-parent",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/bin", "/bin", "--ro-bind", "/sbin", "/sbin", "--ro-bind", "/etc", "/etc",
        "--ro-bind", "/opt", "/opt",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--tmpfs", "/home",
        "--tmpfs", "/srv", "--tmpfs", "/root",
        "--ro-bind", CA_BUNDLE, CA_BUNDLE,
        "--ro-bind", AUTH_DIR, AUTH_DIR,
        "--bind", PROXY_DIR, "/run/proxy",
        "--bind", os.path.abspath(trial_dir), "/work", "--chdir", "/work",
        "/run/proxy/start.sh",
    ]
    env = [
        "env", "-i", "PATH=/usr/bin:/bin:/opt/node22/bin", "HOME=/work",
        "HTTPS_PROXY=http://127.0.0.1:3128", "https_proxy=http://127.0.0.1:3128",
        f"SSL_CERT_FILE={CA_BUNDLE}", f"NODE_EXTRA_CA_CERTS={CA_BUNDLE}",
        f"CLAUDE_CODE_EFFORT_LEVEL={effort}",
    ] + auth_env
    cl = [
        "claude", "--safe-mode", "--disable-slash-commands", "-p", prompt,
        "--session-id", session_id, "--model", model, "--effort", effort,
        "--tools", TOOLS,
        "--disallowedTools", "WebFetch", "WebSearch", "Agent",
        "--allowedTools", "Read", "Write", "Edit", "Glob", "Grep", "Bash",
        "--permission-mode", "dontAsk",
        "--max-turns", str(max_turns),
        "--output-format", "stream-json", "--verbose",
    ]
    return bw + env + cl


def run(trial_dir, model, prompt, log_dir, name, max_turns=80, auth_vars=None, timeout=4 * 3600, effort="medium"):
    os.makedirs(log_dir, exist_ok=True)
    sid = str(uuid.uuid4())
    cmd = command(trial_dir, model, prompt, sid, max_turns, [] if auth_vars is None else auth_vars, effort)
    out = os.path.join(log_dir, f"{name}.stream.jsonl")
    err = os.path.join(log_dir, f"{name}.stderr.txt")
    t0 = time.time()
    # stdout and stderr go through pipes, not file descriptors on the log files,
    # so the child cannot reach the log files through /proc/<pid>/fd (C0.2 finding)
    with open(out, "wb") as fo, open(err, "wb") as fe:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
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
            "stream": out, "stderr": err}


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
    ap.add_argument("model")
    ap.add_argument("prompt_file")
    ap.add_argument("--name", required=True)
    ap.add_argument("--log-dir", default="/srv/r6_private/logs")
    ap.add_argument("--max-turns", type=int, default=80)
    ap.add_argument("--timeout", type=int, default=4 * 3600)
    ap.add_argument("--auth-vars", nargs="*", default=None)
    ap.add_argument("--effort", default="medium")
    a = ap.parse_args()
    r = run(a.trial_dir, a.model, open(a.prompt_file).read(), a.log_dir, a.name,
            a.max_turns, a.auth_vars, a.timeout, a.effort)
    r.update(summarise(r["stream"]))
    print(json.dumps(r))
