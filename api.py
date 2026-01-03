from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/stories")
def get_stories():
    # Return top stories
    return {"stories": []}

