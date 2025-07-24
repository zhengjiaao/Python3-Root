# swagger-ui：http://127.0.0.1:8000/docs
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='app.main:app', host="0.0.0.0", port=8000, reload=False, workers=1)