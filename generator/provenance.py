import json
import base64

# TODO: 替换为SM2签名的实际实现，目前只是一个模拟函数
def sm2_sign_mock(pae_bytes, private_key="mock_key.pem"):
    """
    Sign the PAE bytes using SM2 with the given private key.
    """
    dummy_sig = b"DUMMY_SM2_SIG_FOR_" + base64.b64encode(pae_bytes[:15])
    return dummy_sig

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

def generate_dsse_envelope(build_info, builder_id="Trust-GM-Builder-01"):
    # in-toto Statement v1
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [
            {
                "name": build_info["artifact_name"],
                "digest": {"sm3": build_info["artifact_hash"]}
            }
        ],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://micro-slsa-gm/gcc-builder",
                "externalParameters": {
                    "source": build_info["source_name"]
                },
                "resolvedDependencies": [
                    {
                        "uri": "file://" + build_info["source_name"],
                        "digest": {"sm3": build_info["source_hash"]}
                    }
                ]
            },
            "runDetails": {
                "builder": {"id": builder_id}
            }
        }
    }

    # serialize the statement to JSON bytes
    payload_bytes = json.dumps(statement, separators=(',', ':'), sort_keys=True).encode('utf-8')
    payload_type_bytes = b"application/vnd.in-toto+json"

    pae_bytes = create_dsse_pae(payload_type_bytes, payload_bytes)
    
    sig_bytes = sm2_sign_mock(pae_bytes)

    envelope = {
        "payloadType": payload_type_bytes.decode('utf-8'),
        # save with base64 encoding for JSON compatibility
        "payload": base64.b64encode(payload_bytes).decode('utf-8'),
        "signatures": [
            {
                "keyid": "builder-sm2-pubkey-01",
                "sig": base64.b64encode(sig_bytes).decode('utf-8')
            }
        ]
    }
    
    return envelope

def save_provenance(envelope, output_path="provenance.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=4)
    print(f"[*] DSSE Envelope saved to {output_path}")

