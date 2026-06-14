#!/usr/bin/env bash
set -euo pipefail
WORK=/work/attack-sim
LOGDIR=/work/attack-sim/logs
ART=$WORK/artifacts/demo.exe
PROV=$WORK/artifacts/provenance.json
TS=$(date +%s)
mkdir -p "$LOGDIR"
echo "[attacker] starting at $(date -Iseconds)" | tee "$LOGDIR/attacker-$TS.log"
sleep 2
if [ -f "$ART" ]; then
  cp "$ART" "$ART.orig"
  # simulate simple tamper by appending marker
  echo "SIMULATED_BACKDOOR" >> "$ART"
  echo "[attacker] appended marker to artifact" | tee -a "$LOGDIR/attacker-$TS.log"
  # tamper the provenance JSON by adding a 'tampered' field
  if [ -f "$PROV" ]; then
    python3 - <<'PY'
import json
f='''/work/attack-sim/artifacts/provenance.json'''
data=json.load(open(f))
data['tampered_by_simulator']=True
json.dump(data,open(f,'w'),indent=2)
print('provenance modified')
PY
    echo "[attacker] modified provenance.json" | tee -a "$LOGDIR/attacker-$TS.log"
  else
    echo "[attacker] provenance not found" | tee -a "$LOGDIR/attacker-$TS.log"
  fi
else
  echo "[attacker] artifact not found, nothing to tamper" | tee -a "$LOGDIR/attacker-$TS.log"
fi
echo "[attacker] finished" | tee -a "$LOGDIR/attacker-$TS.log"
