# Attack Simulation (local, Docker)

This folder contains a Docker Compose based simulation that reproduces a SolarWinds-style supply-chain compromise in a fully local and safe way.

Important: run only on an isolated local machine. The simulator only performs harmless file modifications (no network worms or remote exploits).

Usage (requires Docker Desktop with WSL2):

```bash
cd attack-sim
docker compose up --build --abort-on-container-exit
```

After the run, logs are in `attack-sim/logs/` and artifacts in `attack-sim/artifacts/`.

If you want me to run the simulation, reply to authorize; otherwise inspect scripts first.
