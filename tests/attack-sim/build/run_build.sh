#!/usr/bin/env bash
set -euo pipefail
WORK=/work/attack-sim
LOGDIR=/work/attack-sim/logs
ARTDIR=/work/attack-sim/artifacts
mkdir -p "$LOGDIR" "$ARTDIR"
TS=$(date +%s)
echo "[build] starting build at $(date -Iseconds)" | tee "$LOGDIR/build-$TS.log"
SRC=/work/attack-sim/source_repo/test.c
OUT=$ARTDIR/demo.exe
PROV=$ARTDIR/provenance.json
cd /work
echo "running build: src=$SRC out=$OUT prov=$PROV" | tee -a "$LOGDIR/build-$TS.log"
# make sure python requirements are available; try to install gmssl if possible
pip install --no-cache-dir -r ./crypto/requirements.txt >/dev/null 2>&1 || true
python3 main.py build -s "$SRC" -o "$OUT" -p "$PROV" 2>&1 | tee -a "$LOGDIR/build-$TS.log" || true
# record artifact hash
if [ -f "$OUT" ]; then
  HASH=$(python3 - <<'PY'
from hashlib import sha256
print(sha256(open('/work/attack-sim/artifacts/demo.exe','rb').read()).hexdigest())
PY
)
  echo "artifact_hash:$HASH" | tee -a "$LOGDIR/build-$TS.log"
else
  echo "artifact missing" | tee -a "$LOGDIR/build-$TS.log"
fi
echo "[build] finished" | tee -a "$LOGDIR/build-$TS.log"
echo "build done"
