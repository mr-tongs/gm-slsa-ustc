import json
import base64
import os
from crypto.sm_hasher import sm3_file
from crypto.sm_signer import verify_bytes, load_public_key

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

    # attempt to use provided keyid as path to public key; otherwise integrator should supply path
    keyid = signatures[0].get("keyid")
    if keyid and os.path.exists(keyid):
        pubkey_path = keyid
    else:
        # fallback to a default expected public key location inside crypto/keys
        pubkey_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "crypto", "keys", "public_key.hex"))

    is_valid_sig = verify_bytes(pae_bytes, sig_bytes, pubkey_path)
    if not is_valid_sig:
        raise ValueError("Signature verification failed. The provenance may have been tampered with.")
        
    # 2. Verify Artifact Hash
    statement = json.loads(payload_bytes.decode('utf-8'))
    subjects = statement.get("subject", [])
    if not subjects:
        raise ValueError("No subject found in the provenance.")
        
    expected_hash = subjects[0].get("digest", {}).get("sm3", "")
    actual_hash = sm3_file(artifact_path)
    
    if actual_hash != expected_hash:
        raise ValueError(f"Artifact hash mismatch! Expected: {expected_hash}, Actual: {actual_hash}")
        
    print(f"Verification successful for {artifact_path}")
    return True
