"""yap-shell setup wizard.

Checks/prepares everything yap-shell needs:
  1. Python version + `requests`
  2. Ollama binary (offers to install on Linux)
  3. Ollama server running
  4. The qwen3.6 model pulled
  5. `yap` command on PATH

Run it with any of:
    yap --setup
    yapshell-setup
    python -m yapshell.installer
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import site
import subprocess
import sys
import time
from pathlib import Path

MODEL = os.environ.get("YAPSHELL_MODEL", "qwen3.6")
MARKER_VERSION = 1
OLLAMA_DOWNLOAD_URL = "https://ollama.com/download"
OLLAMA_LINUX_INSTALL = "curl -fsSL https://ollama.com/install.sh | sh"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def config_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "yapshell"


def marker_path() -> Path:
    return config_dir() / "setup.json"


def is_setup_done() -> bool:
    try:
        data = json.loads(marker_path().read_text(encoding="utf-8"))
        return data.get("marker_version") == MARKER_VERSION
    except (OSError, ValueError):
        return False


def _write_marker(status: dict) -> None:
    try:
        config_dir().mkdir(parents=True, exist_ok=True)
        payload = {"marker_version": MARKER_VERSION, "model": MODEL, **status}
        marker_path().write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"  (couldn't save setup state: {exc})")


def _say(icon: str, msg: str) -> None:
    print(f"  {icon} {msg}")


def _ok(msg: str) -> None:
    _say("[ok]", msg)


def _warn(msg: str) -> None:
    _say("[!!]", msg)


def _info(msg: str) -> None:
    _say("[..]", msg)


def _ask(question: str, assume_yes: bool) -> bool:
    """Yes/no prompt. Non-interactive sessions answer 'no' unless --yes."""
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        return False
    try:
        answer = input(f"  [??] {question} [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


# --------------------------------------------------------------------------- #
# Individual checks
# --------------------------------------------------------------------------- #
def check_python() -> bool:
    if sys.version_info < (3, 9):
        _warn(f"Python 3.9+ required, found {platform.python_version()}")
        return False
    _ok(f"Python {platform.python_version()}")
    return True


def check_requests() -> bool:
    try:
        import requests  # noqa: F401
    except ImportError:
        _warn("`requests` is missing. Fix with: pip install --upgrade yapshell")
        return False
    _ok("requests installed")
    return True


def check_ollama_binary(assume_yes: bool) -> bool:
    if shutil.which("ollama"):
        _ok("Ollama found")
        return True

    _warn("Ollama is not installed.")
    system = platform.system()

    if system == "Linux" and shutil.which("curl") and shutil.which("sh"):
        print(f"       Official installer: {OLLAMA_LINUX_INSTALL}")
        if _ask("Run the official Ollama installer now?", assume_yes):
            try:
                subprocess.run(OLLAMA_LINUX_INSTALL, shell=True, check=True)
            except (subprocess.CalledProcessError, OSError) as exc:
                _warn(f"Ollama install failed: {exc}")
                return False
            if shutil.which("ollama"):
                _ok("Ollama installed")
                return True
            _warn("Installer finished but `ollama` isn't on PATH yet. Open a new terminal.")
            return False
    elif system == "Darwin":
        print("       Install with: brew install ollama   (or download the app)")
    print(f"       Download: {OLLAMA_DOWNLOAD_URL}")
    return False


def _list_models() -> tuple[bool, list[str]]:
    """Return (server_reachable, model_names)."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, []
    if result.returncode != 0:
        return False, []
    lines = result.stdout.strip().splitlines()[1:]  # skip header row
    return True, [ln.split()[0] for ln in lines if ln.strip()]


def ensure_server() -> bool:
    reachable, _ = _list_models()
    if reachable:
        _ok("Ollama server is running")
        return True

    _info("Ollama server isn't running. Trying to start it...")
    try:
        kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "nt":
            kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(["ollama", "serve"], **kwargs)
    except OSError as exc:
        _warn(f"Couldn't start Ollama: {exc}. Run `ollama serve` in another terminal.")
        return False

    for _ in range(20):
        time.sleep(0.5)
        reachable, _ = _list_models()
        if reachable:
            _ok("Ollama server started")
            return True

    _warn("Ollama server didn't come up. Run `ollama serve` in another terminal.")
    return False


def check_model(assume_yes: bool) -> bool:
    _, names = _list_models()
    wanted = MODEL.split(":")[0]
    has_it = any(n == MODEL or n.split(":")[0] == wanted for n in names)

    if has_it:
        _ok(f"Model '{MODEL}' is available")
        return True

    _warn(f"Model '{MODEL}' hasn't been pulled yet (this can be a large download).")
    if not _ask(f"Pull '{MODEL}' now?", assume_yes):
        print(f"       Later, run: ollama pull {MODEL}")
        return False

    try:
        subprocess.run(["ollama", "pull", MODEL], check=True)
    except (subprocess.CalledProcessError, OSError) as exc:
        _warn(f"Pull failed: {exc}")
        return False
    _ok(f"Model '{MODEL}' pulled")
    return True


def check_path() -> bool:
    if shutil.which("yap"):
        _ok("`yap` command is on your PATH")
        return True

    user_bin = Path(site.getuserbase()) / ("Scripts" if os.name == "nt" else "bin")
    _warn("`yap` isn't on your PATH yet.")
    print(f"       Add this folder to PATH: {user_bin}")
    if os.name != "nt":
        print(f'       e.g.  echo \'export PATH="{user_bin}:$PATH"\' >> ~/.bashrc')
    print("       Meanwhile you can always use: python -m yapshell.main")
    return False


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def run(assume_yes: bool = False, skip_model: bool = False, check_only: bool = False) -> int:
    print()
    print("  yap-shell setup")
    print("  ---------------")

    if check_only:
        assume_yes = False

    status = {
        "python": check_python(),
        "requests": check_requests(),
        "ollama": False,
        "server": False,
        "model": False,
        "path": False,
    }

    if check_only:
        status["ollama"] = bool(shutil.which("ollama"))
        (_ok if status["ollama"] else _warn)("Ollama " + ("found" if status["ollama"] else "missing"))
        if status["ollama"]:
            reachable, names = _list_models()
            status["server"] = reachable
            wanted = MODEL.split(":")[0]
            status["model"] = any(n.split(":")[0] == wanted for n in names)
            (_ok if reachable else _warn)("Ollama server " + ("running" if reachable else "not running"))
            (_ok if status["model"] else _warn)(f"Model '{MODEL}' " + ("present" if status["model"] else "missing"))
        status["path"] = check_path()
        return 0 if all(status.values()) else 1

    status["ollama"] = check_ollama_binary(assume_yes)
    if status["ollama"]:
        status["server"] = ensure_server()
        if status["server"] and not skip_model:
            status["model"] = check_model(assume_yes)
        elif skip_model:
            _info("Skipping model check (--skip-model)")
    status["path"] = check_path()

    _write_marker(status)

    print()
    if all(status.values()) or (skip_model and status["ollama"] and status["server"]):
        print("  All set! Type `yap` to start chatting.")
        return 0
    print("  Setup finished with warnings (see above). Rerun anytime with: yap --setup")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="yapshell-setup", description="Set up yap-shell (Ollama + model + PATH)."
    )
    parser.add_argument("-y", "--yes", action="store_true", help="answer yes to all prompts")
    parser.add_argument("--skip-model", action="store_true", help="don't check/pull the model")
    parser.add_argument("--check", action="store_true", help="only report status, change nothing")
    args = parser.parse_args(argv)
    return run(assume_yes=args.yes, skip_model=args.skip_model, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
