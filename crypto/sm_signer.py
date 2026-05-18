import os

try:
    from gmssl import sm2, func
    _HAS_GMSSL = True
except Exception:
    sm2 = None
    func = None
    _HAS_GMSSL = False


class SM2UnavailableError(RuntimeError):
    pass


def _require_gmssl():
    if not _HAS_GMSSL:
        raise SM2UnavailableError(
            "gmssl is required for SM2 signing. Install with: pip install gmssl"
        )


def _read_key_hex(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Key file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _write_key_hex(path, key_hex, overwrite=False):
    if os.path.exists(path) and not overwrite:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(key_hex)


def generate_keypair(private_key_path, public_key_path, overwrite=False):
    _require_gmssl()
    if (
        not overwrite
        and os.path.exists(private_key_path)
        and os.path.exists(public_key_path)
    ):
        return

    private_key = func.random_hex(64)
    crypt = sm2.CryptSM2(private_key=private_key, public_key="")
    public_key = crypt._kg(int(private_key, 16), crypt.ecc_table["g"])

    _write_key_hex(private_key_path, private_key, overwrite=overwrite)
    _write_key_hex(public_key_path, public_key, overwrite=overwrite)


def ensure_keypair(private_key_path, public_key_path):
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        return
    generate_keypair(private_key_path, public_key_path, overwrite=False)


def load_private_key(private_key_path):
    return _read_key_hex(private_key_path)


def load_public_key(public_key_path):
    return _read_key_hex(public_key_path)


def sign_bytes(data, private_key_path):
    _require_gmssl()
    private_key = load_private_key(private_key_path)
    crypt = sm2.CryptSM2(private_key=private_key, public_key="")
    signature_hex = crypt.sign(data, func.random_hex(64))
    return bytes.fromhex(signature_hex)


def verify_bytes(data, signature_bytes, public_key_path):
    _require_gmssl()
    public_key = load_public_key(public_key_path)
    crypt = sm2.CryptSM2(private_key="", public_key=public_key)
    return crypt.verify(signature_bytes.hex(), data)
