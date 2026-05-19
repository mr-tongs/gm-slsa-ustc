import os

try:
    from gmssl import sm3, func
    _HAS_GMSSL = True
except Exception:
    sm3 = None
    func = None
    _HAS_GMSSL = False


class SM3UnavailableError(RuntimeError):
    pass


def _require_gmssl():
    if not _HAS_GMSSL:
        raise SM3UnavailableError(
            "gmssl is required for SM3 hashing. Install with: pip install gmssl"
        )


def sm3_bytes(data):
    _require_gmssl()
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes-like")
    return sm3.sm3_hash(func.bytes_to_list(bytes(data)))


def sm3_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    _require_gmssl()
    with open(file_path, "rb") as f:
        data = f.read()
    return sm3_bytes(data)
