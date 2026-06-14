import subprocess
import os
from crypto.sm_hasher import sm3_file

def build_artifact(source_file, output_file):
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file {source_file} does not exist.")
    
    source_hash = sm3_file(source_file)

    # TODO: go with a real sandbox solution to wrap the build process, set the source read-only
    
    print(f"Compiling {source_file} to {output_file}.")
    try:
        subprocess.run(["gcc", source_file, "-o", output_file], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Build failed: {e}")
    except FileNotFoundError:
        raise RuntimeError("GCC compiler not found.")
    
    artifact_hash = sm3_file(output_file)
    
    return {
        "artifact_name": os.path.basename(output_file),
        "artifact_hash": artifact_hash,
        "source_name": os.path.basename(source_file),
        "source_hash": source_hash
    }