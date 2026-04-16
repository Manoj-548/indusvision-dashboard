from diskcache import Cache

cache = Cache("kv_store")

def kv_set(key, value):
    cache[key] = value

def kv_get(key, default=None):
    return cache.get(key, default)

def kv_delete(key):
    cache.pop(key, None)