from fastapi import FastAPI

app = FastAPI(title="Test Stock Analysis System")

@app.get("/")
async def root():
    return {"message": "FastAPI is working!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

