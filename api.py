from fastapi import FastAPI
from main import fetch_top_stories, is_important

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/stories")
def get_stories(limit: int = 10):
    """Fetch top stories from HackerNews"""
    try:
        stories = fetch_top_stories(limit)
        # Convert Story dataclass to dict for JSON response
        stories_dict = [
            {
                "id": s.id,
                "title": s.title,
                "author": s.by,
                "score": s.score,
                "comments": s.descendants,
                "url": s.url,
                "time": s.time
            }
            for s in stories
        ]
        return {"stories": stories_dict}
    except Exception as e:
        return {"error": str(e), "stories": []}

@app.get("/stories/important")
def get_important_stories():
    """Fetch only important stories"""
    try:
        stories = fetch_top_stories(limit=50)
        important = [s for s in stories if is_important(s)]
        # Convert Story dataclass to dict for JSON response
        stories_dict = [
            {
                "id": s.id,
                "title": s.title,
                "author": s.by,
                "score": s.score,
                "comments": s.descendants,
                "url": s.url,
                "time": s.time
            }
            for s in important
        ]
        return {"stories": stories_dict}
    except Exception as e:
        return {"error": str(e), "stories": []}

