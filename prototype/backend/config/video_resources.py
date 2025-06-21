# Video resource lists for backend validation

DANCE_VIDEOS = [
    "/videos/太空熱舞3.mp4",
    "/videos/太空熱舞2.mp4",
    "/videos/太空熱舞.mp4",
    "/videos/太空辣妹跳舞.mp4",
    "/videos/太空走秀.mp4",
    "/videos/太空走秀2.mp4",
]

LIFESTYLE_VIDEOS = [
    "/videos/太空瑜伽3.mp4",
    "/videos/太空瑜伽2.mp4",
    "/videos/太空瑜伽.mp4",
    "/videos/太空直播中.mp4",
    "/videos/太空直播中3.mp4",
    "/videos/太空泡水.mp4",
    "/videos/太空化妝.mp4",
    "/videos/太空打卡.mp4",
    "/videos/太空打卡2.mp4",
    "/videos/太空摘帽帽.mp4",
    "/videos/太空吃東西.mp4",
    "/videos/daily_life_1.mp4",
]

ENTERTAINMENT_VIDEOS = [
    "/videos/太空鋪克牌.mp4",
    "/videos/太空鋪克牌2.mp4",
    "/videos/太空戀愛秀.mp4",
    "/videos/太空帶貨中.mp4",
    "/videos/小綠人動畫.mp4",
    "/videos/小綠人動畫2.mp4",
    "/videos/小綠人動畫3.mp4",
]

VR_TECH_VIDEOS = [
    "/videos/太空VR.mp4",
    "/videos/太空VR2.mp4",
]

SPACE_EFFECT_VIDEOS = [
    "/videos/火箭發射.mp4",
    "/videos/星際小可愛.mp4",
    "/videos/星際小籠包.mp4",
    "/videos/星際聽音樂.mp4",
    "/videos/黑洞.mp4",
    "/videos/模擬星雲圖.mp4",
    "/videos/太空巨乳.mp4",
    "/videos/太空史萊姆.mp4",
    "/videos/space_live_video_1.mp4",
    "/videos/space_live.mp4",
]

ALL_VIDEOS = DANCE_VIDEOS + LIFESTYLE_VIDEOS + ENTERTAINMENT_VIDEOS + VR_TECH_VIDEOS + SPACE_EFFECT_VIDEOS


def is_video_file_valid(filepath: str) -> bool:
    """Return True if the provided video path exists in the known list."""
    return filepath in ALL_VIDEOS
