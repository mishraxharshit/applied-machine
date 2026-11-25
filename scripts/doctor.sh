#!/usr/bin/env bash
# Checks which tools you have, so you know what `make test` / `make up` can do.
set -u
check() {
  if command -v "$1" >/dev/null 2>&1; then printf "  ok       %-8s %s\n" "$1" "$("$1" $2 2>&1 | head -n1)"
  else printf "  MISSING  %-8s %s\n" "$1" "$3"; fi
}
echo "Applied Machine environment check"
check python3 --version "install python 3.10+"
check go version "https://go.dev/dl"
check cargo --version "https://rustup.rs"
check node --version "install Node 20+ (for the website)"
check docker --version "https://docs.docker.com/engine/install"
