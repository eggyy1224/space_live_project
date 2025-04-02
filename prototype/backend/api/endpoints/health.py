from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    健康檢查端點
    """
    return {"status": "ok"} 