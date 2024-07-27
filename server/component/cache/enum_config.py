from enum import Enum


class RedisKeyPrefixEnum(Enum):
    MATERIAL_DETAIL = "md", "素材详情"
    MATERIAL = "ma", "素材id"
    MATERIAL_STUDY_PROGRESS = "msp", "学习进度"
    COLLECT = "collect", "收藏"

