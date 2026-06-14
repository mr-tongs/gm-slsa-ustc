#!/usr/bin/env bash
set -euo pipefail
WORK=/work/attack-sim
LOGDIR=/work/attack-sim/logs
mkdir -p "$WORK"
mkdir -p "$LOGDIR"
echo "[source] initializing source repo at $WORK/source_repo" | tee "$LOGDIR/source-$(date +%s).log"
rm -rf "$WORK/source_repo"
mkdir -p "$WORK/source_repo"
# copy demo C file into source_repo
if [ -f /work/tests/demo_project/test.c ]; then
  cp /work/tests/demo_project/test.c "$WORK/source_repo/test.c"
else
  cat > "$WORK/source_repo/test.c" <<'EOF'
#include <stdio.h>
int main(){ printf("hello demo\n"); return 0; }
EOF
fi
cd "$WORK/source_repo"
git init >/dev/null 2>&1
git config user.email "sim@local"
git config user.name "sim"
git add .
git commit -m "initial commit" >/dev/null 2>&1
echo "[source] repo ready" | tee -a "$LOGDIR/source-$(date +%s).log"
echo "source done"
