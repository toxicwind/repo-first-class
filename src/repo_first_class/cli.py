"""Command-line interface for repo-first-class."""

from __future__ import annotations

import argparse
import sys

from . import __version__, canonical_dest, ensure_checkout, verify_state


def _print_state(state, out=sys.stdout) -> None:
    print(f"visibility : {state.visibility}", file=out)
    print(f"branch     : {state.branch}", file=out)
    print(f"local_head : {state.local_head}", file=out)
    print(f"remote_head: {state.remote_head}", file=out)
    print(f"in_sync    : {state.in_sync}", file=out)
    if state.dirty:
        print("dirty      :", file=out)
        for line in state.dirty:
            print(f"  {line}", file=out)


def cmd_ensure(args: argparse.Namespace) -> int:
    dest = args.dest or str(canonical_dest(args.repo))
    try:
        state = ensure_checkout(args.repo, dest)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _print_state(state)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    verdict = verify_state(args.dest, args.remote_sha)
    print(f"status     : {verdict.status}", file=sys.stdout)
    print(f"local_head : {verdict.local_head or '(none)'}", file=sys.stdout)
    print(f"remote_head: {verdict.remote_head}", file=sys.stdout)
    if verdict.dirty:
        print("dirty      :", file=sys.stdout)
        for line in verdict.dirty:
            print(f"  {line}", file=sys.stdout)
    return 0 if verdict.ok() else 2


def cmd_where(args: argparse.Namespace) -> int:
    print(canonical_dest(args.name, base=args.base))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-first-class",
        description="Make any GitHub repo first-class: canonical checkout, verified in sync.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ensure = sub.add_parser(
        "ensure",
        help="Clone (if missing) or ff-only pull a repo, then report sync state.",
    )
    p_ensure.add_argument("repo", help="owner/repo, e.g. toxicwind/repo-first-class")
    p_ensure.add_argument("dest", nargs="?", help="checkout path (default: canonical box path)")
    p_ensure.set_defaults(func=cmd_ensure)

    p_verify = sub.add_parser(
        "verify",
        help="Pure-git check: is <dest> sitting on <remote-sha>? No network needed.",
    )
    p_verify.add_argument("dest", help="local checkout path")
    p_verify.add_argument("remote_sha", help="expected remote HEAD SHA")
    p_verify.set_defaults(func=cmd_verify)

    p_where = sub.add_parser("where", help="Print the canonical box path for a repo.")
    p_where.add_argument("name", help="owner/repo or repo")
    p_where.add_argument("--base", default="/home/toxic/projects", help="canonical base dir")
    p_where.set_defaults(func=cmd_where)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
