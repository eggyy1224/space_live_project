from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from services.speech_to_text import SpeechToTextService
from services.text_to_speech import TextToSpeechService
from services.ai import AIService
from core.models import SpeechToTextRequest
import logging
import base64
import os
import io
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

# 創建調試目錄
DEBUG_DIR = "debug_audio"
os.makedirs(DEBUG_DIR, exist_ok=True)

@router.post("/speech-to-text")
async def process_speech_file(request: Request):
    """
    處理語音檔案上傳請求，轉換為文字並生成回應
    """
    try:
        # 獲取 Content-Type
        content_type = request.headers.get("content-type")
        if not content_type or "audio" not in content_type: 
             # 如果沒有 content-type 或不是音頻，嘗試默認為 webm
            mime_type = "audio/webm;codecs=opus"
            logger.warning(f"缺少或無效的 Content-Type，默認為: {mime_type}")
        else:
            mime_type = content_type
            
        logger.info(f"收到語音識別請求，MIME類型: {mime_type}")
        
        # 讀取原始請求體中的音頻數據
        audio_data = await request.body()
        
        if not audio_data or len(audio_data) == 0:
            logger.warning("上傳的音頻文件為空")
            raise HTTPException(status_code=400, detail="音頻文件為空")
        
        logger.info(f"成功讀取音頻數據，大小：{len(audio_data)} 字節")
        
        # 保存音頻用於調試
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 根據MIME類型選擇合適的擴展名
        extension = "webm"
        if "ogg" in mime_type:
            extension = "ogg"
        elif "wav" in mime_type:
            extension = "wav"
        elif "mpeg" in mime_type:
             extension = "mp3"

        debug_file_path = os.path.join(DEBUG_DIR, f"audio_{timestamp}.{extension}")
        try:
            with open(debug_file_path, "wb") as f:
                f.write(audio_data)
            logger.info(f"已保存音頻文件用於調試：{debug_file_path}")
        except Exception as save_err:
             logger.error(f"保存調試音頻失敗: {save_err}")
        
        # 轉換語音為文字
        logger.info(f"開始轉換語音為文字...")
        result = await speech_service.transcribe_audio(audio_data, mime_type)
        logger.info(f"轉換結果: {result}")
        
        # 如果語音識別成功且有文字，則生成回應
        if result.get("success") and result.get("text"):
            transcribed_text = result["text"]
            logger.info(f"識別到的文字: '{transcribed_text}'，開始生成回應...")
            
            # 使用AI服務生成回應
            try:
                response_dict = await ai_service.generate_response(
                    user_text=transcribed_text 
                )
                response = response_dict.get("final_response", "嗯...我好像有點走神了。")
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
                        "audio_filename": tts_result.get("filename", ""),
                        "duration": tts_result["duration"],
                        "confidence": result.get("confidence", 0),
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
            # 如果識別失敗，返回包含錯誤信息的結果
            error_message = result.get('error', '語音識別失敗，未知錯誤')
            logger.warning(f"語音識別失敗：{error_message}")
            raise HTTPException(status_code=400, detail=error_message)
            
    except HTTPException as http_exc:
        # 直接重新拋出 HTTPException
        raise http_exc
    except Exception as e:
        logger.error(f"處理語音轉文字時發生未預期錯誤: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"處理語音轉文字失敗")

# 保留舊接口以兼容
@router.post("/speech-to-text/base64")
async def process_speech_base64(request: SpeechToTextRequest):
    """
    處理base64編碼的語音轉文字請求
    """
    try:
        # 獲取請求中的音頻數據
        logger.info(f"收到base64語音識別請求，長度：{len(request.audio_base64) if request.audio_base64 else 0}")
        
        if not request.audio_base64:
            logger.warning("請求中沒有音頻數據")
            return {"success": False, "error": "沒有提供音頻數據"}
        
        # 解碼base64音訊數據
        try:
            audio_data = base64.b64decode(request.audio_base64)
        except Exception as e:
            logger.error(f"解碼base64音頻失敗: {str(e)}")
            return {"success": False, "error": f"解碼音頻失敗: {str(e)}"}
        
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
        
        # 然後讓舊方法繼續處理...
        # 轉換語音為文字
        logger.info(f"開始轉換語音為文字，使用MIME類型: {mime_type}...")
        result = await speech_service.transcribe_audio(audio_data, mime_type)
        
        # 這裡繼續原有的處理邏輯...
        # 如果語音識別成功且有文字，則生成回應
        if result["success"] and result["text"]:
            transcribed_text = result["text"]
            
            # 使用AI服務生成回應
            try:
                response_dict = await ai_service.generate_response(
                    user_text=transcribed_text
                )
                response = response_dict.get("final_response", "嗯...我好像有點走神了。")
                
                # 生成語音回應
                tts_result = await tts_service.synthesize_speech(response)
                
                if tts_result:
                    return {
                        "text": transcribed_text,
                        "response": response,
                        "audio": tts_result["audio"],
                        "duration": tts_result["duration"],
                        "confidence": result.get("confidence", 0),
                        "success": True
                    }
                else:
                    return {
                        "text": transcribed_text,
                        "response": response,
                        "success": True,
                        "error": "無法生成語音回應"
                    }
            except Exception as e:
                return {
                    "text": transcribed_text,
                    "success": True,
                    "error": f"生成回應失敗: {str(e)}"
                }
        else:
            return result
            
    except Exception as e:
        logger.error(f"處理語音轉文字失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"處理語音轉文字失敗: {str(e)}") 