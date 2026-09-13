#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
project_root=$(pwd)
cd "$project_root/frontend"
npm ci --no-audit --no-fund
cd "$project_root/frontend"
npm run build
cd "$project_root/backend"
python -m pip install -e ".[dev]"
cd "$project_root/backend"
python -m pytest
