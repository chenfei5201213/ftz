from enum import Enum


class RedisKeyPrefixEnum(Enum):
    MATERIAL_DETAIL = "md", "素材详情"
    MATERIAL = "ma", "素材id"
    MATERIAL_STUDY_PROGRESS = "msp", "学习进度"
    COLLECT = "collect", "收藏"
    COURSE = "course", "课程"
    COURSE_MATERIAL_COUNT = "course_md_count", "课程素材数量"
    LESSON = "lesson", "课时"
    LESSON_MATERIAL_COUNT = "lesson_md_count", "课时素材数量"
    LESSON_MATERIAL_IDS = "lesson_md_ids", "课时素材id"
    CARD = "card", "卡片"
    LESSON_WORDS = "lesson_words", "单词"
