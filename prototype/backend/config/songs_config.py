SONGS_METADATA = [
    {
        "id": "murmur_song",
        "title": "Murmur 哼唱",
        "filename": "murmur.mp3",
        "duration": 10.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "thinking", "proportion": 0.0},
            {"tag": "neutral", "proportion": 0.15},
            {"tag": "listening", "proportion": 0.3},
            {"tag": "thinking", "proportion": 0.45},
            {"tag": "neutral", "proportion": 0.6},
            {"tag": "listening", "proportion": 0.75},
            {"tag": "thinking", "proportion": 0.85},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "JazzDancing", "proportion": 0.0},
            {"name": "WeightShift", "proportion": 0.2}, 
            {"name": "Swaying", "proportion": 0.5}, # 假設有輕微搖擺動作
            {"name": "Flair", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "singing_song",
        "title": "歌唱片段",
        "filename": "song_singing.mp3",
        "duration": 15.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "neutral", "proportion": 0.0},
            {"tag": "happy", "proportion": 0.1},
            {"tag": "amused", "proportion": 0.2},
            {"tag": "joyful", "proportion": 0.3},
            {"tag": "excited", "proportion": 0.45},
            {"tag": "playful", "proportion": 0.6},
            {"tag": "triumphant", "proportion": 0.75},
            {"tag": "happy", "proportion": 0.85},
            {"tag": "content", "proportion": 0.95},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDynamicPose", "proportion": 0.0},
            {"name": "JazzDancing", "proportion": 0.15},
            {"name": "HipHopDancin", "proportion": 0.5},
            {"name": "Cheering", "proportion": 0.85},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "male_vocal_song",
        "title": "男性哼唱片段",
        "filename": "male_vocal.mp3",
        "duration": 10.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "neutral", "proportion": 0.0},
            {"tag": "thinking", "proportion": 0.2},
            {"tag": "content", "proportion": 0.4}, # 使用 content 作為替代
            {"tag": "playful", "proportion": 0.7},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "MaleDynamicPose", "proportion": 0.0},
            {"name": "HipHopDancin", "proportion": 0.25},
            {"name": "Flair", "proportion": 0.65},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "female_talking_song",
        "title": "女性說話片段",
        "filename": "female_talking1.mp3",
        "duration": 10.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "neutral", "proportion": 0.0},
            {"tag": "listening", "proportion": 0.15},
            {"tag": "thinking", "proportion": 0.3},
            {"tag": "content", "proportion": 0.45},
            {"tag": "neutral", "proportion": 0.6},
            {"tag": "listening", "proportion": 0.75},
            {"tag": "thinking", "proportion": 0.85},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "Talking_Neutral", "proportion": 0.0},
            {"name": "Listening_Neutral", "proportion": 0.25},
            {"name": "Talking_Explaining", "proportion": 0.5},
            {"name": "WeightShift", "proportion": 0.75},
            {"name": "Idle_Neutral", "proportion": 1.0}
        ]
    }
]

# 在 murmur 時播放歌曲的機率 (0.0 至 1.0)
# 例如，0.1 代表 10% 的機率播放歌曲而不是生成一般 murmur
SONG_PLAY_PROBABILITY = 0.6 # 你可以調整這個值 