SONGS_METADATA = [
    {
        "id": "murmur_song",
        "title": "Murmur 哼唱",
        "filename": "murmur.mp3",
        "duration": 10.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "joyful", "proportion": 0.0},
            {"tag": "angry", "proportion": 0.15},
            {"tag": "sad", "proportion": 0.3},
            {"tag": "surprised", "proportion": 0.45},
            {"tag": "fearful", "proportion": 0.6},
            {"tag": "disgusted", "proportion": 0.75},
            {"tag": "happy", "proportion": 0.85},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "JazzDancing", "proportion": 0.0},
            {"name": "HipHopDancin", "proportion": 0.2},
            {"name": "Flair", "proportion": 0.5}, 
            {"name": "FemaleDancePose", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "singing_song",
        "title": "歌唱片段",
        "filename": "song_singing.mp3",
        "duration": 15.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "excited", "proportion": 0.0},
            {"tag": "sad", "proportion": 0.1},
            {"tag": "angry", "proportion": 0.2},
            {"tag": "happy", "proportion": 0.3},
            {"tag": "fearful", "proportion": 0.45},
            {"tag": "triumphant", "proportion": 0.6},
            {"tag": "surprised", "proportion": 0.75},
            {"tag": "disgusted", "proportion": 0.85},
            {"tag": "joyful", "proportion": 0.95},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDynamicPose", "proportion": 0.0},
            {"name": "SalsaDancing", "proportion": 0.15},
            {"name": "DancingTwerk", "proportion": 0.5},
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
            {"tag": "angry", "proportion": 0.0},
            {"tag": "happy", "proportion": 0.2},
            {"tag": "sad", "proportion": 0.4},
            {"tag": "excited", "proportion": 0.7},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "MaleDynamicPose", "proportion": 0.0},
            {"name": "Breakdance1990", "proportion": 0.25},
            {"name": "Moonwalk", "proportion": 0.65},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "female_talking_song",
        "title": "女性說話片段",
        "filename": "female_talking1.mp3",
        "duration": 10.0,  # 歌曲時長 (秒)
        "emotionalKeyframes": [
            {"tag": "surprised", "proportion": 0.0},
            {"tag": "fearful", "proportion": 0.15},
            {"tag": "joyful", "proportion": 0.3},
            {"tag": "angry", "proportion": 0.45},
            {"tag": "sad", "proportion": 0.6},
            {"tag": "happy", "proportion": 0.75},
            {"tag": "disgusted", "proportion": 0.85},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDancePose", "proportion": 0.0},
            {"name": "JazzDancing", "proportion": 0.25},
            {"name": "ButterflyTwirl", "proportion": 0.5},
            {"name": "Flair", "proportion": 0.75},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "a_looping_instrument_song",
        "title": "循環樂器片段",
        "filename": "A_looping_instrument.mp3",
        "duration": 10.0,  # TODO: 請確認並修改實際時長
        "emotionalKeyframes": [
            {"tag": "happy", "proportion": 0.0},
            {"tag": "angry", "proportion": 0.3},
            {"tag": "sad", "proportion": 0.6},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},
            {"name": "CanCan", "proportion": 0.4},
            {"name": "Spin In Place", "proportion": 0.7},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "a_male_vocalist_sing_song",
        "title": "男性歌手演唱片段",
        "filename": "A_male_vocalist_sing.mp3",
        "duration": 10.0,  # TODO: 請確認並修改實際時長
        "emotionalKeyframes": [
            {"tag": "triumphant", "proportion": 0.0},
            {"tag": "sad", "proportion": 0.25},
            {"tag": "angry", "proportion": 0.5},
            {"tag": "joyful", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "MaleDynamicPose", "proportion": 0.0},
            {"name": "breaking", "proportion": 0.3},
            {"name": "Flair", "proportion": 0.6},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "ambient_keyboard_cli_song",
        "title": "氛圍鍵盤片段",
        "filename": "Ambient_keyboard_cli.mp3",
        "duration": 10.0,  # TODO: 請確認並修改實際時長
        "emotionalKeyframes": [
            {"tag": "fearful", "proportion": 0.0},
            {"tag": "excited", "proportion": 0.25},
            {"tag": "angry", "proportion": 0.5},
            {"tag": "surprised", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "BreakdanceFootwork2", "proportion": 0.0},
            {"name": "Au", "proportion": 0.3},
            {"name": "twistdance", "proportion": 0.6},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "ambient_keyboard_cli_2_song",
        "title": "氛圍鍵盤片段2",
        "filename": "Ambient_keyboard_cli_2.mp3",
        "duration": 10.0,  # TODO: 請確認並修改實際時長
        "emotionalKeyframes": [
            {"tag": "disgusted", "proportion": 0.0},
            {"tag": "happy", "proportion": 0.25},
            {"tag": "sad", "proportion": 0.5},
            {"tag": "angry", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "Au", "proportion": 0.0},
            {"name": "MacacoSide", "proportion": 0.3},
            {"name": "hiphopdance", "proportion": 0.6},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "energetic_fast_pace_song",
        "title": "活力快節奏片段",
        "filename": "Energetic_fast_pace.mp3",
        "duration": 10.0,  # TODO: 請確認並修改實際時長
        "emotionalKeyframes": [
            {"tag": "joyful", "proportion": 0.0},
            {"tag": "angry", "proportion": 0.2},
            {"tag": "surprised", "proportion": 0.4},
            {"tag": "sad", "proportion": 0.6},
            {"tag": "triumphant", "proportion": 0.8},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},
            {"name": "JazzDancing", "proportion": 0.3},
            {"name": "Cheering", "proportion": 0.6},
            {"name": "Flair", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "winds_blowing_song",
        "title": "風聲音效",
        "filename": "winds_blowing.mp3",
        "duration": 15.0,  
        "emotionalKeyframes": [
            {"tag": "fearful", "proportion": 0.0},
            {"tag": "angry", "proportion": 0.5},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDynamicPose", "proportion": 0.0},
            {"name": "Spin In Place", "proportion": 0.5},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "a_young_taiwanese_gi_1_song",
        "title": "年輕台灣女孩 1",
        "filename": "A_young_Taiwanese_gi_1.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "happy", "proportion": 0.0},
            {"tag": "surprised", "proportion": 0.15},
            {"tag": "joyful", "proportion": 0.3},
            {"tag": "playful", "proportion": 0.45},
            {"tag": "excited", "proportion": 0.6},
            {"tag": "triumphant", "proportion": 0.75},
            {"tag": "affectionate", "proportion": 0.9},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDynamicPose", "proportion": 0.0},
            {"name": "JazzDancing", "proportion": 0.2},
            {"name": "twistdance", "proportion": 0.4},
            {"name": "Cheering", "proportion": 0.6},
            {"name": "ButterflyTwirl", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "a_young_taiwanese_gi_2_song",
        "title": "年輕台灣女孩 2",
        "filename": "A_young_Taiwanese_gi_2.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "serene", "proportion": 0.0},
            {"tag": "hopeful", "proportion": 0.15},
            {"tag": "amused", "proportion": 0.3},
            {"tag": "grateful", "proportion": 0.45},
            {"tag": "content", "proportion": 0.6},
            {"tag": "interested", "proportion": 0.75},
            {"tag": "shy", "proportion": 0.9},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleStandingPose", "proportion": 0.0},
            {"name": "FemaleDancePose", "proportion": 0.2},
            {"name": "SalsaDancing", "proportion": 0.4},
            {"name": "FemaleCrouchPose", "proportion": 0.6},
            {"name": "StandingClap", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "a_young_taiwanese_gi_3_song",
        "title": "年輕台灣女孩 3",
        "filename": "A_young_Taiwanese_gi_3.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "determined", "proportion": 0.0},
            {"tag": "proud", "proportion": 0.15},
            {"tag": "excited", "proportion": 0.3},
            {"tag": "surprised", "proportion": 0.45},
            {"tag": "triumphant", "proportion": 0.6},
            {"tag": "joyful", "proportion": 0.75},
            {"tag": "happy", "proportion": 0.9},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},
            {"name": "Flair", "proportion": 0.2},
            {"name": "DancingTwerk", "proportion": 0.4},
            {"name": "Spin In Place", "proportion": 0.6},
            {"name": "jumping", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "a_young_taiwanese_gi_4_song",
        "title": "年輕台灣女孩 4",
        "filename": "A_young_Taiwanese_gi_4.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "fearful", "proportion": 0.0},
            {"tag": "worried", "proportion": 0.15},
            {"tag": "surprised", "proportion": 0.3},
            {"tag": "relieved", "proportion": 0.45},
            {"tag": "hopeful", "proportion": 0.6},
            {"tag": "content", "proportion": 0.75},
            {"tag": "serene", "proportion": 0.9},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "ProneLeftTurn", "proportion": 0.0},
            {"name": "ReachingOut", "proportion": 0.2},
            {"name": "LookAround", "proportion": 0.4},
            {"name": "Walking", "proportion": 0.6},
            {"name": "FemaleDancePose", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    }
]

# 在 murmur 時播放歌曲的機率 (0.0 至 1.0)
# 例如，0.1 代表 10% 的機率播放歌曲而不是生成一般 murmur
SONG_PLAY_PROBABILITY = 0.8 # 你可以調整這個值 