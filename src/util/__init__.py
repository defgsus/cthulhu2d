

def dump_object(o, file=None):
    """Dump any python object"""
    keys = [key for key in dir(o) if not key.startswith("_")]
    max_key_len = max(len(key) for key in keys)
    for key in keys:
        print(f"{key:{max_key_len}} = {getattr(o, key)}", file=file)
