from fastapi import APIRouter, HTTPException
from services.speech_to_text import SpeechToTextService
from services.text_to_speech import TextToSpeechService
from services.ai import AIService
from services.emotion import EmotionAnalyzer
from core.models import SpeechToTextRequest
import logging
import base64
import os
from datetime import datetime

# 設置日誌
logger = logging.getLogger("speech_api")
logger.setLevel(logging.DEBUG)

# 創建路由
router = APIRouter()

# 初始化服務
speech_service = SpeechToTextService()
tts_service = TextToSpeechService()
ai_service = AIService()
emotion_analyzer = EmotionAnalyzer()

# 創建調試目錄
DEBUG_DIR = "debug_audio"
os.makedirs(DEBUG_DIR, exist_ok=True)

@router.post("/speech-to-text")
async def process_speech(request: SpeechToTextRequest):
    """
    處理語音轉文字請求，分析情緒，並生成AI回應
    """
    try:
        # 獲取請求中的音頻數據
        logger.info(f"收到語音識別請求，base64長度：{len(request.audio_base64) if request.audio_base64 else 0}")
        
        if not request.audio_base64:
            logger.warning("請求中沒有音頻數據")
            return {"success": False, "error": "沒有提供音頻數據"}
        
        # 解碼base64音訊數據
        try:
            audio_data = base64.b64decode(request.audio_base64)
            logger.info(f"成功解碼base64數據，大小：{len(audio_data)} 字節")
            
            # 保存音頻用於調試
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mime_type = request.mime_type or "audio/webm;codecs=opus"
            
            # 根據MIME類型選擇合適的擴展名
            extension = "webm"
            if "ogg" in mime_type:
                extension = "ogg"
            
            debug_file_path = os.path.join(DEBUG_DIR, f"audio_{timestamp}.{extension}")
            with open(debug_file_path, "wb") as f:
                f.write(audio_data)
            logger.info(f"已保存音頻文件用於調試：{debug_file_path}，MIME類型：{mime_type}")
            
        except Exception as e:
            logger.error(f"解碼base64音頻失敗: {str(e)}")
            return {"success": False, "error": f"解碼音頻失敗: {str(e)}"}
        
        # 轉換語音為文字
        logger.info(f"開始轉換語音為文字，使用MIME類型: {mime_type}...")
        result = await speech_service.transcribe_audio(audio_data, mime_type)
        logger.info(f"轉換結果: {result}")
        
        # 如果語音識別成功且有文字，則生成回應
        if result["success"] and result["text"]:
            transcribed_text = result["text"]
            logger.info(f"識別到的文字: '{transcribed_text}'，開始分析情緒和生成回應...")
            
            # 分析情緒
            detected_emotion, confidence = emotion_analyzer.analyze(transcribed_text)
            logger.info(f"分析情緒結果: {detected_emotion}, 置信度: {confidence}")
            
            # 使用AI服務生成回應
            try:
                response = await ai_service.generate_response(
                    user_text=transcribed_text, 
                    current_emotion=detected_emotion
                )
                logger.info(f"AI回應: '{response}'")
                
                # 生成語音回應
                logger.info("開始生成語音回應...")
                tts_result = await tts_service.synthesize_speech(response)
                
                if tts_result:
                    logger.info(f"成功生成語音回應，音頻長度：{len(tts_result['audio'])}，持續時間：{tts_result['duration']}秒")
                    # 返回完整結果
                    return {
                        "text": transcribed_text,
                        "response": response,
                        "audio": tts_result["audio"],
                        "duration": tts_result["duration"],
                        "confidence": result.get("confidence", 0),
                        "detected_emotion": detected_emotion,
                        "emotion_confidence": confidence,
                        "success": True
                    }
                else:
                    logger.warning("無法生成語音回應")
                    # 只返回文字結果
                    return {
                        "text": transcribed_text,
                        "response": response,
                        "success": True,
                        "error": "無法生成語音回應"
                    }
            except Exception as e:
                logger.error(f"生成AI回應失敗: {str(e)}")
                # 至少返回語音識別結果
                return {
                    "text": transcribed_text,
                    "success": True,
                    "error": f"生成回應失敗: {str(e)}"
                }
        else:
            logger.warning(f"語音識別失敗：{result.get('error', '未知錯誤')}")
            return result
            
    except Exception as e:
        logger.error(f"處理語音轉文字失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"處理語音轉文字失敗: {str(e)}") 