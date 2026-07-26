#!/bin/bash
set -e

# Fix vikunja volume permissions
# The vikunja container runs as uid 1000 but Docker creates volumes as root
if command -v docker &> /dev/null; then
  docker run --rm -v project_vikunja_files:/data alpine chown -R 1000:0 /data 2>/dev/null || true
fi
