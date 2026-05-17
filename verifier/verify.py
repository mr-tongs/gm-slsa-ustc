import json
import base64
import os
import hashlib

# TODO: 替换为 core.crypto 中的国密 SM2 验签与 SM3 哈希算法
def sm2_verify_mock(pae_bytes, signature_bytes, public_key="mock_key.pem"):
    """
    Verify the SM2 signature against the PAE bytes.
    """
    expected_prefix = b"DUMMY_SM2_SIG_FOR_" + base64.b64encode(pae_bytes[:15])
    return signature_bytes == expected_prefix

def sm3_hash_mock(file_path):
    if not os.path.exists(file_path):
        return ""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def create_dsse_pae(payload_type_bytes, payload_bytes):
    """
    PAE = "DSSEv1" + " " + len(type) + " " + type + " " + len(body) + " " + body
    """
    pae = (
        b"DSSEv1 " + 
        str(len(payload_type_bytes)).encode('utf-8') + b" " +
        payload_type_bytes + b" " +
        str(len(payload_bytes)).encode('utf-8') + b" " +
        payload_bytes
    )
    return pae

def verify_provenance(artifact_path, provenance_path):
    if not os.path.exists(provenance_path):
        raise FileNotFoundError(f"Provenance file not found: {provenance_path}")
    
    with open(provenance_path, "r", encoding="utf-8") as f:
        envelope = json.load(f)
        
    payload_type = envelope.get("payloadType", "")
    payload_b64 = envelope.get("payload", "")
    signatures = envelope.get("signatures", [])
    
    if not signatures:
        raise ValueError("No signatures found in the envelope.")
        
    payload_bytes = base64.b64decode(payload_b64)
    payload_type_bytes = payload_type.encode('utf-8')
    
    # 1. Verify Signature
    pae_bytes = create_dsse_pae(payload_type_bytes, payload_bytes)
    
    sig_val_b64 = signatures[0]["sig"]
    sig_bytes = base64.b64decode(sig_val_b64)
    
    is_valid_sig = sm2_verify_mock(pae_bytes, sig_bytes)
    if not is_valid_sig:
        raise ValueError("Signature verification failed. The provenance may have been tampered with.")
        
    # 2. Verify Artifact Hash
    statement = json.loads(payload_bytes.decode('utf-8'))
    subjects = statement.get("subject", [])
    if not subjects:
        raise ValueError("No subject found in the provenance.")
        
    expected_hash = subjects[0].get("digest", {}).get("sm3", "")
    actual_hash = sm3_hash_mock(artifact_path)
    
    if actual_hash != expected_hash:
        raise ValueError(f"Artifact hash mismatch! Expected: {expected_hash}, Actual: {actual_hash}")
        
    print(f"Verification successful for {artifact_path}")
    return True
