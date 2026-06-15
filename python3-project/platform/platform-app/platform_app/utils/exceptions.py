from fastapi import HTTPException, status


class AppException(HTTPException):
    """应用基础异常。"""

    def __init__(self, status_code: int = 400, message: str = "请求错误"):
        super().__init__(status_code=status_code, detail=message)


class BadRequestException(AppException):
    """业务规则违反异常 (400)。"""
    def __init__(self, message: str = "请求错误"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "需要认证"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class ConflictException(AppException):
    def __init__(self, message: str = "资源已存在"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message)
