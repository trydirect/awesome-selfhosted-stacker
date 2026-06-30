#!/bin/sh
# Initialize ArchiveBox if needed (creates data directory structure, installs plugins, etc.)
archivebox init || true
# Start the ArchiveBox server
exec archivebox server
