"""Entry point for `yap` / `yapshell`.

Runs the setup wizard the first time (interactive terminals only), then
hands off to the normal yap-shell main().
"""
from __future__ import annotations

import sys


def main() -> int | None:
    from yapshell import installer

    args = sys.argv[1:]

    # Explicit setup request: `yap --setup [--yes] [--skip-model] [--check]`
    if args and args[0] == "--setup":
        return installer.main(args[1:])

    # First run after `pip install`: run the wizard once.
    if not installer.is_setup_done() and sys.stdin.isatty() and sys.stdout.isatty():
        try:
            installer.run()
        except KeyboardInterrupt:
            print("\n  Setup skipped. Run `yap --setup` whenever you're ready.")
        print()

    from yapshell.main import main as yap_main

    return yap_main()


if __name__ == "__main__":
    sys.exit(main())
