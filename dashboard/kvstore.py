def kv_set(key, value):
    from diskcache import Cache
    cache = Cache("kv_store")
    cache[key] = value

def kv_get(key, default=None):
    from diskcache import Cache
    cache = Cache("kv_store")
    return cache.get(key, default)

def kv_delete(key):
    from diskcache import Cache
    cache = Cache("kv_store")
    cache.pop(key, None)