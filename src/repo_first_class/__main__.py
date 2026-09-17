"""Allow ``python -m repo_first_class`` as an alias for the CLI."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
