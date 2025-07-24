# Swagger UI: http://localhost:8000/docs
#
# 前端测试页: http://localhost:8000/templates/index.html
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='app.main:app', host="0.0.0.0", port=8000, reload=False)