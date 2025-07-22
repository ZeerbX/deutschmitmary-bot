from fastapi import FastAPI

app = FastAPI()

@app.get("/trigger")
async def trigger_post():
    return {"status": "✅ Test erfolgreich!"}
