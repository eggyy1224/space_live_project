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
            {"name": "Jumping", "proportion": 0.8},
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
    },
    {
        "id": "rap_1",
        "title": "RAP 1",
        "filename": "11L-A_Taiwanese_teenage_-1747298240041.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "excited", "proportion": 0.0},
            {"tag": "smug", "proportion": 0.25},
            {"tag": "playful", "proportion": 0.5},
            {"tag": "determined", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},
            {"name": "BreakdanceFootwork2", "proportion": 0.3},
            {"name": "MaleDynamicPose", "proportion": 0.6}, # Assuming a generally energetic pose
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "rap_2",
        "title": "RAP 2",
        "filename": "11L-A_Taiwanese_teenage_-1747298241002.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "angry", "proportion": 0.0},
            {"tag": "determined", "proportion": 0.25},
            {"tag": "excited", "proportion": 0.5},
            {"tag": "triumphant", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "breaking", "proportion": 0.0}, # Generic breakdance
            {"name": "Flair", "proportion": 0.3},
            {"name": "HipHopDancin", "proportion": 0.6},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "rap_3",
        "title": "RAP 3",
        "filename": "11L-A_Taiwanese_teenage_-1747298241942.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "angry", "proportion": 0.0},
            {"tag": "frustrated", "proportion": 0.25},
            {"tag": "smug", "proportion": 0.5},
            {"tag": "excited", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},
            {"name": "MaleDynamicPose", "proportion": 0.3},
            {"name": "Breakdance1990", "proportion": 0.6},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "rap_4",
        "title": "RAP 4",
        "filename": "11L-A_Taiwanese_teenage_-1747298242725.mp3",
        "duration": 15.0,
        "emotionalKeyframes": [
            {"tag": "joyful", "proportion": 0.0},
            {"tag": "playful", "proportion": 0.25},
            {"tag": "content", "proportion": 0.5},
            {"tag": "smug", "proportion": 0.75},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "Moonwalk", "proportion": 0.0},
            {"name": "HipHopDancin", "proportion": 0.3},
            {"name": "Flair", "proportion": 0.6},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "niaojiao_song",
        "title": "鳥叫",
        "filename": "鳥叫.mp3",
        "duration": 15.0,  # 更新時長為 15 秒
        "emotionalKeyframes": [
            {"tag": "neutral", "proportion": 0.0},
            {"tag": "surprised", "proportion": 0.2},
            {"tag": "playful", "proportion": 0.5},
            {"tag": "happy", "proportion": 0.8},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "Idle", "proportion": 0.0},
            {"name": "LookAround", "proportion": 0.1},
            {"name": "FemaleDynamicPose", "proportion": 0.4},
            {"name": "Cheering", "proportion": 0.7},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "horse_panting_song",
        "title": "馬喘息聲",
        "filename": "馬喘息聲.mp3",
        "duration": 15.0,  # 更新時長為 15 秒
        "emotionalKeyframes": [
            {"tag": "neutral", "proportion": 0.0},
            {"tag": "worried", "proportion": 0.3},
            {"tag": "worried", "proportion": 0.7},
            {"tag": "neutral", "proportion": 1.0}
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDynamicPose", "proportion": 0.0},
            {"name": "LookAround", "proportion": 0.2},
            {"name": "FemaleDynamicPose", "proportion": 0.8},
            {"name": "Idle", "proportion": 1.0}
        ]
    },
    {
        "id": "kuangxi_song",
        "title": "狂喜",
        "filename": "狂喜.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "excited", "proportion": 0.0},      # 開始就很興奮
            {"tag": "joyful", "proportion": 0.15},      # 轉為狂歡
            {"tag": "playful", "proportion": 0.3},      # 變得頑皮
            {"tag": "awe", "proportion": 0.45},         # 達到驚嘆狂喜
            {"tag": "triumphant", "proportion": 0.6},   # 勝利感
            {"tag": "amused", "proportion": 0.75},      # 被逗樂了
            {"tag": "happy", "proportion": 0.9},        # 回到開心
            {"tag": "content", "proportion": 1.0}       # 最後滿足
        ],
        "bodyAnimationSequence": [
            {"name": "Cheering", "proportion": 0.0},           # 開始歡呼
            {"name": "DancingTwerk", "proportion": 0.15},      # 扭臀舞蹈
            {"name": "Spin In Place", "proportion": 0.3},      # 原地旋轉
            {"name": "JazzDancing", "proportion": 0.45},       # 爵士舞
            {"name": "Breakdance1990", "proportion": 0.6},     # 霹靂舞頭轉
            {"name": "Flair", "proportion": 0.75},             # 花式動作
            {"name": "StandingClap", "proportion": 0.9},       # 站立鼓掌
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "electronic_music_song",
        "title": "電子音樂",
        "filename": "電子音樂.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "excited", "proportion": 0.0},      # 開始興奮
            {"tag": "determined", "proportion": 0.15},  # 堅定節拍
            {"tag": "interested", "proportion": 0.3},   # 專注律動
            {"tag": "joyful", "proportion": 0.45},      # 能量爆發
            {"tag": "smug", "proportion": 0.6},         # 自信滿滿
            {"tag": "triumphant", "proportion": 0.75},  # 勝利高潮
            {"tag": "scheming", "proportion": 0.9},     # 酷炫結尾
            {"tag": "neutral", "proportion": 1.0}       # 回歸平靜
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},       # 嘻哈舞蹈開場
            {"name": "BreakdanceFootwork2", "proportion": 0.15}, # 地板步法
            {"name": "Flair", "proportion": 0.3},              # 花式動作
            {"name": "Breakdance1990", "proportion": 0.45},    # 霹靂舞頭轉
            {"name": "Spin In Place", "proportion": 0.6},      # 原地旋轉
            {"name": "MaleDynamicPose", "proportion": 0.75},   # 動態姿勢
            {"name": "Moonwalk", "proportion": 0.9},           # 太空漫步
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "tyrannosaurus_roar_song",
        "title": "暴龍吼叫",
        "filename": "暴龍吼叫.mp3",
        "duration": 10.0,  # 實際時長約10秒
        "emotionalKeyframes": [
            {"tag": "angry", "proportion": 0.0},        # 開始憤怒
            {"tag": "frustrated", "proportion": 0.2},   # 挫折感
            {"tag": "spiteful", "proportion": 0.4},     # 惡意威嚇
            {"tag": "contemptuous", "proportion": 0.6}, # 輕蔑
            {"tag": "triumphant", "proportion": 0.8},   # 勝利咆哮
            {"tag": "neutral", "proportion": 1.0}       # 回歸平靜
        ],
        "bodyAnimationSequence": [
            {"name": "Roar", "proportion": 0.0},               # 怒吼動作
            {"name": "MaleDynamicPose", "proportion": 0.2},    # 威嚇姿勢
            {"name": "JumpAttack", "proportion": 0.4},         # 跳躍攻擊
            {"name": "BrutalAssassination", "proportion": 0.6}, # 兇狠攻擊
            {"name": "YellingWhileStanding", "proportion": 0.8}, # 站立咆哮
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "panting_song",
        "title": "喘息",
        "filename": "喘息.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "worried", "proportion": 0.0},      # 開始擔心
            {"tag": "nervous", "proportion": 0.15},     # 緊張不安
            {"tag": "pain", "proportion": 0.3},         # 痛苦表情
            {"tag": "frustrated", "proportion": 0.45},  # 挫折感
            {"tag": "relieved", "proportion": 0.6},     # 開始緩解
            {"tag": "sleepy", "proportion": 0.75},      # 疲憊想睡
            {"tag": "content", "proportion": 0.9},      # 滿足平靜
            {"tag": "neutral", "proportion": 1.0}       # 回歸正常
        ],
        "bodyAnimationSequence": [
            {"name": "InjuredWalk", "proportion": 0.0},        # 受傷行走
            {"name": "PainGesture", "proportion": 0.15},       # 痛苦手勢
            {"name": "KneelingDown", "proportion": 0.3},       # 跪下
            {"name": "KneelingIdle", "proportion": 0.45},      # 跪姿待機
            {"name": "Thinking", "proportion": 0.6},           # 思考恢復
            {"name": "LayingIdle", "proportion": 0.75},        # 躺下休息
            {"name": "FemaleLayingPose", "proportion": 0.9},   # 躺臥姿勢
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "opera_1_song",
        "title": "歌劇1",
        "filename": "歌劇1.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "serene", "proportion": 0.0},       # 寧靜開場
            {"tag": "interested", "proportion": 0.15},  # 產生興趣
            {"tag": "hopeful", "proportion": 0.3},      # 充滿希望
            {"tag": "joyful", "proportion": 0.45},      # 歡樂高潮
            {"tag": "triumphant", "proportion": 0.6},   # 勝利感
            {"tag": "grateful", "proportion": 0.75},    # 感恩
            {"tag": "content", "proportion": 0.9},      # 滿足
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleStandingPose", "proportion": 0.0},     # 優雅站姿
            {"name": "FemaleDancePose", "proportion": 0.15},       # 舞蹈姿勢
            {"name": "SalsaDancing", "proportion": 0.3},           # 莎莎舞
            {"name": "JazzDancing", "proportion": 0.45},           # 爵士舞
            {"name": "ButterflyTwirl", "proportion": 0.6},         # 蝴蝶旋轉
            {"name": "Cheering", "proportion": 0.75},              # 歡呼
            {"name": "StandingClap", "proportion": 0.9},           # 鼓掌
            {"name": "Idle", "proportion": 1.0}                    # 結束
        ]
    },
    {
        "id": "opera_2_song",
        "title": "歌劇2",
        "filename": "歌劇2.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "sad", "proportion": 0.0},          # 悲傷開場
            {"tag": "gloomy", "proportion": 0.15},      # 憂鬱
            {"tag": "worried", "proportion": 0.3},      # 擔憂
            {"tag": "pain", "proportion": 0.45},        # 痛苦
            {"tag": "regretful", "proportion": 0.6},    # 後悔
            {"tag": "relieved", "proportion": 0.75},    # 釋然
            {"tag": "hopeful", "proportion": 0.9},      # 重燃希望
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleLayingPose", "proportion": 0.0},       # 躺臥姿勢
            {"name": "PainGesture", "proportion": 0.15},           # 痛苦手勢
            {"name": "Crying", "proportion": 0.3},                 # 哭泣
            {"name": "KneelingDown", "proportion": 0.45},          # 跪下
            {"name": "Thinking", "proportion": 0.6},               # 思考
            {"name": "ReachingOut", "proportion": 0.75},           # 伸手觸及
            {"name": "FemaleDancePose", "proportion": 0.9},        # 舞蹈姿勢
            {"name": "Idle", "proportion": 1.0}                    # 結束
        ]
    },
    {
        "id": "opera_3_song",
        "title": "歌劇3",
        "filename": "歌劇3.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "angry", "proportion": 0.0},        # 憤怒開場
            {"tag": "frustrated", "proportion": 0.15},  # 挫折
            {"tag": "spiteful", "proportion": 0.3},     # 惡意
            {"tag": "contemptuous", "proportion": 0.45}, # 輕蔑
            {"tag": "determined", "proportion": 0.6},   # 決心
            {"tag": "triumphant", "proportion": 0.75},  # 勝利
            {"tag": "proud", "proportion": 0.9},        # 驕傲
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "YellingWhileStanding", "proportion": 0.0},   # 站立大喊
            {"name": "MaleDynamicPose", "proportion": 0.15},       # 動態姿勢
            {"name": "JumpAttack", "proportion": 0.3},             # 跳躍攻擊
            {"name": "Flair", "proportion": 0.45},                 # 花式動作
            {"name": "MaleDynamicPose", "proportion": 0.6},        # 動態姿勢
            {"name": "Cheering", "proportion": 0.75},              # 歡呼
            {"name": "StandingClap", "proportion": 0.9},           # 鼓掌
            {"name": "Idle", "proportion": 1.0}                    # 結束
        ]
    },
    {
        "id": "opera_4_song",
        "title": "歌劇4",
        "filename": "歌劇4.mp3",
        "duration": 20.0,  # 實際時長約20秒
        "emotionalKeyframes": [
            {"tag": "excited", "proportion": 0.0},      # 興奮開場
            {"tag": "playful", "proportion": 0.15},     # 頑皮
            {"tag": "amused", "proportion": 0.3},       # 被逗樂
            {"tag": "joyful", "proportion": 0.45},      # 歡樂
            {"tag": "affectionate", "proportion": 0.6}, # 深情
            {"tag": "grateful", "proportion": 0.75},    # 感恩
            {"tag": "serene", "proportion": 0.9},       # 寧靜
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "CanCan", "proportion": 0.0},                 # 康康舞
            {"name": "JazzDancing", "proportion": 0.15},           # 爵士舞
            {"name": "DancingTwerk", "proportion": 0.3},           # 扭臀舞
            {"name": "ButterflyTwirl", "proportion": 0.45},        # 蝴蝶旋轉
            {"name": "Kiss", "proportion": 0.6},                   # 親吻
            {"name": "StandingClap", "proportion": 0.75},          # 鼓掌
            {"name": "FemaleStandingPose", "proportion": 0.9},     # 優雅站姿
            {"name": "Idle", "proportion": 1.0}                    # 結束
        ]
    },
    # 動物叫聲系列
    {
        "id": "dog_bark_1_song",
        "title": "小狗叫1",
        "filename": "小狗叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "excited", "proportion": 0.0},      # 興奮吠叫
            {"tag": "alert", "proportion": 0.3},        # 警覺
            {"tag": "playful", "proportion": 0.6},      # 頑皮
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "JumpingJacks", "proportion": 0.0},       # 跳躍
            {"name": "Cheering", "proportion": 0.3},           # 歡呼
            {"name": "MaleDynamicPose", "proportion": 0.6},    # 動態姿勢
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "dog_bark_2_song",
        "title": "小狗叫2",
        "filename": "小狗叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "alert", "proportion": 0.0},        # 警覺
            {"tag": "curious", "proportion": 0.4},      # 好奇
            {"tag": "friendly", "proportion": 0.8},     # 友善
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "LookAround", "proportion": 0.0},         # 東張西望
            {"name": "PointingGesture", "proportion": 0.4},    # 指向手勢
            {"name": "WavingHello", "proportion": 0.8},        # 揮手問好
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "cat_meow_1_song",
        "title": "貓叫1",
        "filename": "貓叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "curious", "proportion": 0.0},      # 好奇
            {"tag": "demanding", "proportion": 0.3},    # 要求
            {"tag": "affectionate", "proportion": 0.7}, # 撒嬌
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "FemaleDancePose", "proportion": 0.0},    # 優雅姿勢
            {"name": "ReachingOut", "proportion": 0.3},        # 伸手
            {"name": "Kiss", "proportion": 0.7},               # 親吻
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "cat_meow_2_song",
        "title": "貓叫2",
        "filename": "貓叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "sleepy", "proportion": 0.0},       # 慵懶
            {"tag": "content", "proportion": 0.4},      # 滿足
            {"tag": "relaxed", "proportion": 0.8},      # 放鬆
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "LayingIdle", "proportion": 0.0},         # 躺著
            {"name": "FemaleLayingPose", "proportion": 0.4},   # 躺臥姿勢
            {"name": "Stretching", "proportion": 0.8},         # 伸懶腰
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "cow_moo_1_song",
        "title": "牛叫1",
        "filename": "牛叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "calm", "proportion": 0.0},         # 平靜
            {"tag": "content", "proportion": 0.5},      # 滿足
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "GrazeIdle", "proportion": 0.0},          # 吃草姿勢
            {"name": "FemaleStandingPose", "proportion": 0.5}, # 站立姿勢
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "cow_moo_2_song",
        "title": "牛叫2", 
        "filename": "牛叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "calling", "proportion": 0.0},      # 呼喚
            {"tag": "social", "proportion": 0.6},       # 社交
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "YellingWhileStanding", "proportion": 0.0}, # 站立呼叫
            {"name": "WavingHello", "proportion": 0.6},          # 揮手
            {"name": "Idle", "proportion": 1.0}                  # 結束
        ]
    },
    {
        "id": "snake_hiss_1_song",
        "title": "蛇叫1",
        "filename": "蛇叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "threatening", "proportion": 0.0},  # 威脅
            {"tag": "defensive", "proportion": 0.5},    # 防禦
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "Spin In Place", "proportion": 0.0},      # 盤旋
            {"name": "MaleDynamicPose", "proportion": 0.5},    # 威嚇姿勢
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "snake_hiss_2_song",
        "title": "蛇叫2",
        "filename": "蛇叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "sneaky", "proportion": 0.0},       # 潛行
            {"tag": "calculating", "proportion": 0.6},  # 計算
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "Crouching", "proportion": 0.0},          # 蹲伏
            {"name": "SlowWalk", "proportion": 0.6},           # 緩慢移動
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "rooster_crow_1_song",
        "title": "雞叫1",
        "filename": "雞叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "proud", "proportion": 0.0},        # 驕傲
            {"tag": "announcing", "proportion": 0.4},   # 宣告
            {"tag": "confident", "proportion": 0.8},    # 自信
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "Cheering", "proportion": 0.0},           # 歡呼
            {"name": "YellingWhileStanding", "proportion": 0.4}, # 站立大叫
            {"name": "MaleDynamicPose", "proportion": 0.8},    # 動態姿勢
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "rooster_crow_2_song",
        "title": "雞叫2",
        "filename": "雞叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "alert", "proportion": 0.0},        # 警覺
            {"tag": "territorial", "proportion": 0.5},  # 宣示領域
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "LookAround", "proportion": 0.0},         # 東張西望
            {"name": "Flair", "proportion": 0.5},              # 花式動作
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "monkey_chatter_1_song",
        "title": "猴子叫1",
        "filename": "猴子叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "playful", "proportion": 0.0},      # 頑皮
            {"tag": "excited", "proportion": 0.3},      # 興奮
            {"tag": "mischievous", "proportion": 0.7},  # 調皮
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "JumpingJacks", "proportion": 0.0},       # 跳躍
            {"name": "Spin In Place", "proportion": 0.3},      # 旋轉
            {"name": "DancingTwerk", "proportion": 0.7},       # 扭臀
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "monkey_chatter_2_song",
        "title": "猴子叫2",
        "filename": "猴子叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "curious", "proportion": 0.0},      # 好奇
            {"tag": "social", "proportion": 0.4},       # 社交
            {"tag": "amused", "proportion": 0.8},       # 開心
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "PointingGesture", "proportion": 0.0},    # 指向
            {"name": "WavingHello", "proportion": 0.4},        # 揮手
            {"name": "JazzDancing", "proportion": 0.8},        # 爵士舞
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "monkey_chatter_3_song",
        "title": "猴子叫3",
        "filename": "猴子叫3.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "energetic", "proportion": 0.0},    # 活力
            {"tag": "wild", "proportion": 0.4},         # 野性
            {"tag": "joyful", "proportion": 0.8},       # 歡樂
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "HipHopDancin", "proportion": 0.0},       # 嘻哈舞
            {"name": "Breakdance1990", "proportion": 0.4},     # 霹靂舞
            {"name": "Cheering", "proportion": 0.8},           # 歡呼
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "wolf_howl_1_song",
        "title": "狼叫1",
        "filename": "狼叫1.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "longing", "proportion": 0.0},      # 渴望
            {"tag": "mournful", "proportion": 0.4},     # 哀傷
            {"tag": "calling", "proportion": 0.8},      # 呼喚
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "YellingWhileStanding", "proportion": 0.0}, # 站立嚎叫
            {"name": "Thinking", "proportion": 0.4},             # 思考
            {"name": "ReachingOut", "proportion": 0.8},          # 伸手
            {"name": "Idle", "proportion": 1.0}                  # 結束
        ]
    },
    {
        "id": "wolf_howl_2_song",
        "title": "狼叫2",
        "filename": "狼叫2.mp3",
        "duration": 5.0,
        "emotionalKeyframes": [
            {"tag": "wild", "proportion": 0.0},         # 野性
            {"tag": "pack_calling", "proportion": 0.5}, # 召集同伴
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "Roar", "proportion": 0.0},               # 怒吼
            {"name": "YellingWhileStanding", "proportion": 0.5}, # 站立呼叫
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    # 小綠人語音系列
    {
        "id": "alien_speak_1_song",
        "title": "小綠人講話1",
        "filename": "小綠人講話1.mp3",
        "duration": 20.0,
        "emotionalKeyframes": [
            {"tag": "curious", "proportion": 0.0},      # 好奇
            {"tag": "mysterious", "proportion": 0.2},   # 神秘
            {"tag": "analytical", "proportion": 0.4},   # 分析
            {"tag": "friendly", "proportion": 0.6},     # 友善
            {"tag": "wise", "proportion": 0.8},         # 智慧
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "Thinking", "proportion": 0.0},           # 思考
            {"name": "PointingGesture", "proportion": 0.2},    # 指向
            {"name": "ExplainingGesture", "proportion": 0.4},  # 解釋手勢
            {"name": "WavingHello", "proportion": 0.6},        # 友善揮手
            {"name": "FemaleDancePose", "proportion": 0.8},    # 優雅姿勢
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "alien_speak_2_song",
        "title": "小綠人講話2",
        "filename": "小綠人講話2.mp3",
        "duration": 20.0,
        "emotionalKeyframes": [
            {"tag": "intrigued", "proportion": 0.0},    # 著迷
            {"tag": "scientific", "proportion": 0.25},  # 科學性
            {"tag": "explaining", "proportion": 0.5},   # 解釋
            {"tag": "patient", "proportion": 0.75},     # 耐心
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "LookAround", "proportion": 0.0},         # 觀察
            {"name": "ExplainingGesture", "proportion": 0.25}, # 解釋
            {"name": "PointingGesture", "proportion": 0.5},    # 指向
            {"name": "Thinking", "proportion": 0.75},          # 思考
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    },
    {
        "id": "alien_speak_3_song",
        "title": "小綠人講話3",
        "filename": "小綠人講話3.mp3",
        "duration": 20.0,
        "emotionalKeyframes": [
            {"tag": "telepathic", "proportion": 0.0},   # 心靈感應
            {"tag": "cosmic", "proportion": 0.2},       # 宇宙性
            {"tag": "enlightened", "proportion": 0.4},  # 開悟
            {"tag": "transcendent", "proportion": 0.6}, # 超越
            {"tag": "peaceful", "proportion": 0.8},     # 平和
            {"tag": "neutral", "proportion": 1.0}       # 結束
        ],
        "bodyAnimationSequence": [
            {"name": "LayingIdle", "proportion": 0.0},         # 冥想姿勢
            {"name": "ReachingOut", "proportion": 0.2},        # 伸展
            {"name": "FemaleDancePose", "proportion": 0.4},    # 舞蹈姿勢
            {"name": "Spin In Place", "proportion": 0.6},      # 旋轉
            {"name": "FemaleStandingPose", "proportion": 0.8}, # 站立
            {"name": "Idle", "proportion": 1.0}                # 結束
        ]
    }
]

# 在 murmur 時播放歌曲的機率 (0.0 至 1.0)
# 例如，0.1 代表 10% 的機率播放歌曲而不是生成一般 murmur
SONG_PLAY_PROBABILITY = 0.7 # 你可以調整這個值 

# Helper function to get song metadata by id (if not already present)
# def get_song_by_id(song_id):
#     for song in SONGS_METADATA:
#         if song["id"] == song_id:
#             return song
#     return None 