from fastapi import FastAPI

app = FastAPI(title="my-post")

@app.get("/")
async def root():
    return {"ok": True}