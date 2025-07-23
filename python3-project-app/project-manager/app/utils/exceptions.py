from fastapi import HTTPException, status
from starlette.responses import JSONResponse


class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def http_exception_handler(request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

def validation_exception_handler(request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )