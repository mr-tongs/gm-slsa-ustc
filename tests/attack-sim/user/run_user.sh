#!/usr/bin/env bash
set -euo pipefail
WORK=/work/attack-sim
LOGDIR=/work/attack-sim/logs
ART=$WORK/artifacts/demo.exe
PROV=$WORK/artifacts/provenance.json
TS=$(date +%s)
mkdir -p "$LOGDIR"
echo "[user] starting at $(date -Iseconds)" | tee "$LOGDIR/user-$TS.log"
if [ -f "$ART" ]; then
  echo "[user] found artifact, size=$(stat -c%s $ART)" | tee -a "$LOGDIR/user-$TS.log"
else
  echo "[user] artifact missing" | tee -a "$LOGDIR/user-$TS.log"
fi
if [ -f "$PROV" ]; then
  echo "[user] found provenance, dumping summary:" | tee -a "$LOGDIR/user-$TS.log"
  head -n 50 "$PROV" | tee -a "$LOGDIR/user-$TS.log"
  # attempt to verify using repository verifier
  python3 /work/main.py verify -a "$ART" -p "$PROV" 2>&1 | tee -a "$LOGDIR/user-$TS.log" || true
else
  echo "[user] provenance missing" | tee -a "$LOGDIR/user-$TS.log"
fi
echo "[user] finished" | tee -a "$LOGDIR/user-$TS.log"
