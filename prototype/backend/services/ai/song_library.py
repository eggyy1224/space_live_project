"""
歌曲庫元數據
"""

SONG_LIBRARY = [
    {
        "id": "song_001", 
        "title": "星空下的低語", 
        "file_name": "lullaby_of_stars.mp3", # 假設您會在 prototype/backend/songs/ 中放入此檔案
        "duration_seconds": 120 
    },
    {
        "id": "song_002", 
        "title": "宇宙搖擺", 
        "file_name": "cosmic_swing.mp3", # 假設您會在 prototype/backend/songs/ 中放入此檔案
        "duration_seconds": 150
    },
    # 您可以在此處添加更多歌曲...
    # 例如：
    # {
    #     "id": "song_003", 
    #     "title": "月球漫步Disco", 
    #     "file_name": "moonwalk_disco.mp3",
    #     "duration_seconds": 185
    # },
]

def get_song_library():
    """返回歌曲庫列表"""
    return SONG_LIBRARY

def get_random_song():
    """從歌曲庫隨機選擇一首歌，如果庫為空則返回 None"""
    import random
    library = get_song_library()
    if not library:
        return None
    return random.choice(library)

if __name__ == '__main__':
    # 簡單測試
    print(f"歌曲庫: {get_song_library()}")
    random_song = get_random_song()
    if random_song:
        print(f"隨機選歌: {random_song['title']}")
    else:
        print("歌曲庫是空的。") 