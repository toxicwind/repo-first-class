#!/usr/bin/env bash
# polish_sample.sh — runnable demo of the repo-first-class workflow.
#
# Builds a tiny scratch repo in a unique temp dir, walks it through the
# first-class checklist (README? LICENSE? .gitignore? clean? in sync?),
# and polishes it using the repo-first-class CLI. Works fully offline —
# no GitHub account needed.
set -euo pipefail

CLI="${REPO_FIRST_CLASS_CLI:-repo-first-class}"
SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/rfc-hello.XXXXXX")"
trap 'rm -rf "$SCRATCH"' EXIT

SAMPLE="$SCRATCH/sample-repo"
mkdir -p "$SAMPLE"
cd "$SAMPLE"
git init -q
git config user.email "demo@example.com"
git config user.name "repo-first-class demo"
echo 'print("hello")' > hello.py
git add .
git commit -qm "initial"

check() { # check <label> <test...>
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  [ok]   $label"; else echo "  [FAIL] $label"; fi
}

echo "== before: bare sample repo =="
check "README present"            test -f README.md
check "LICENSE present"           test -f LICENSE
check ".gitignore present"        test -f .gitignore
check "working tree clean"        git diff --quiet
check "git repo"                  git rev-parse --is-inside-work-tree

echo "== polishing =="
cat > README.md <<'EOF'
# sample-repo

A tiny demo repo polished by repo-first-class.
EOF
cat > LICENSE <<'EOF'
MIT License

Copyright (c) 2026 demo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
printf '__pycache__/\n*.pyc\n' > .gitignore
git add .
git commit -qm "polish: README, LICENSE, .gitignore"

echo "== after =="
check "README present"            test -f README.md
check "LICENSE present"           test -f LICENSE
check ".gitignore present"        test -f .gitignore
check "working tree clean"        git diff --quiet

HEAD="$(git rev-parse HEAD)"
echo "== verify checkout state =="
"$CLI" verify "$SAMPLE" "$HEAD"
echo "== deliberate divergence =="
echo 'print("hello again")' >> hello.py
git add . && git commit -qm "second"
"$CLI" verify "$SAMPLE" "$HEAD" || true   # expected: diverged, exit 2

echo "== canonical path for a real repo =="
"$CLI" where toxicwind/repo-first-class
echo "done."
