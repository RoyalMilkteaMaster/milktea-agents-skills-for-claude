#!/usr/bin/env sh

set -u

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_path=${2:-"$PWD"}

if ! command -v node >/dev/null 2>&1; then
  printf '%s\n' '{"schema_version":2,"status":"prerequisites_missing","reason_codes":["node_missing"]}'
  exit 20
fi

if [ "${1:-}" != "--confirmed" ]; then
  exec node "$script_dir/open-code-review.js" install --repo "$repo_path"
fi

exec node "$script_dir/open-code-review.js" install --confirmed --repo "$repo_path"
