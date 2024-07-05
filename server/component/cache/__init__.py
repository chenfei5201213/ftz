TIMEOUT = 1 * 60 * 15  # 默认缓存时间

REDIS_SEPARATOR = ":"  # redis key分隔符


def to_redis_key(key_prefix: str, *args, application_id: str = 'ftz') -> str:
    if args:
        args_str = list(map(str, args))
        return f"{REDIS_SEPARATOR.join([application_id, key_prefix, *args_str])}"
    return f"{REDIS_SEPARATOR.join([application_id, key_prefix])}"
