from fastapi import HTTPException

class ServiceException(Exception):
    """服務層異常基類"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class SpeechServiceException(ServiceException):
    """語音服務異常"""
    pass

class AIServiceException(ServiceException):
    """AI服務異常"""
    pass 