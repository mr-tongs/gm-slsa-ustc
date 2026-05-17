import subprocess
import os
import hashlib  # 用于临时 Mock SM3

# TODO: 替换为 core.crypto 中的国密 SM3 算法
def sm3_hash_mock(file_path):
    if not os.path.exists(file_path):
        return "file_not_found"
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def build_artifact(source_file, output_file):
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file {source_file} does not exist.")
    
    source_hash = sm3_hash_mock(source_file)

    # TODO: go with a real sandbox solution to wrap the build process, set the source read-only
    
    print(f"Compiling {source_file} to {output_file}.")
    try:
        subprocess.run(["gcc", source_file, "-o", output_file], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Build failed: {e}")
    except FileNotFoundError:
        raise RuntimeError("GCC compiler not found.")
    
    artifact_hash = sm3_hash_mock(output_file)
    
    return {
        "artifact_name": os.path.basename(output_file),
        "artifact_hash": artifact_hash,
        "source_name": os.path.basename(source_file),
        "source_hash": source_hash
    }