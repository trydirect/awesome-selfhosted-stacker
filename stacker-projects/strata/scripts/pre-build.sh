#!/bin/bash
# pre_build hook: make sure .env exists and the Strata source tree (build
# context) is present. Upstream is not vendored into this repo — it is cloned
# on demand (depth 1, ~30 MB) into strata-src/, which is gitignored.
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/generate-secrets.sh

if [ ! -d strata-src/.git ]; then
  echo "Cloning Strata source into strata-src/ (build context) ..."
  git clone --depth 1 https://github.com/Niko1221/Strata strata-src
fi
