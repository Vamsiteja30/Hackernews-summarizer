from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from main import fetch_top_stories, is_important, fetch_story, is_trending
from agent import prepare_text_for_agent
from praval_agent import summarize_with_openai, summarize_with_gemini
from typing import Optional, List

app = FastAPI()

class SummaryRequest(BaseModel):
    story_id: Optional[int] = None
    text: Optional[str] = None

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

@app.get("/stories/trending")
def get_trending_stories():
    """Fetch only trending stories (important posts within last 12 hours)"""
    try:
        stories = fetch_top_stories(limit=50)
        trending = [s for s in stories if is_trending(s)]
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
            for s in trending
        ]
        return {"stories": stories_dict}
    except Exception as e:
        return {"error": str(e), "stories": []}

@app.get("/stories/{story_id}")
def get_story_by_id(story_id: int):
    """Get a specific story by its HackerNews ID"""
    try:
        story = fetch_story(story_id)
        if story is None:
            raise HTTPException(
                status_code=404,
                detail=f"Story with ID {story_id} not found"
            )
        
        # Determine story classification
        classification = "NORMAL"
        if is_trending(story):
            classification = "TRENDING"
        elif is_important(story):
            classification = "IMPORTANT"
        
        story_dict = {
            "id": story.id,
            "title": story.title,
            "author": story.by,
            "score": story.score,
            "comments": story.descendants,
            "url": story.url,
            "time": story.time,
            "classification": classification,
            "hn_url": f"https://news.ycombinator.com/item?id={story.id}"
        }
        return story_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching story: {str(e)}"
        )

@app.get("/categories")
def get_categories():
    """Get list of available categories for filtering
    
    Note: Category detection is not yet implemented. This endpoint
    returns a list of planned categories for future use.
    """
    return {
        "categories": [
            "AI",
            "Programming",
            "Startups",
            "Science",
            "Web Development",
            "Security",
            "Hardware",
            "Open Source",
            "Business",
            "Design"
        ],
        "note": "Category-based filtering is planned but not yet implemented. Stories will be automatically categorized in a future update."
    }

@app.get("/search")
def search_stories(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """Search for stories by keyword
    
    Note: Full search functionality requires database integration.
    Currently searches through recently fetched top stories only.
    """
    try:
        if not q or not q.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )
        
        stories = fetch_top_stories(limit=100)
        
        query_lower = q.lower().strip()
        matching_stories = []
        
        for story in stories:
            if query_lower in story.title.lower():
                matching_stories.append(story)
                if len(matching_stories) >= limit:
                    break
        
        # Convert to dict format
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
            for s in matching_stories
        ]
        
        return {
            "query": q,
            "results_count": len(stories_dict),
            "stories": stories_dict,
            "note": "Search currently limited to top 100 stories. Full archive search will be available after database integration."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching stories: {str(e)}"
        )

def get_summary(text: str) -> str:
    """Generate summary using OpenAI first, Gemini as fallback"""
    try:
        # Try OpenAI first
        summary = summarize_with_openai(text)
        return summary
    except Exception as openai_error:
  
        try:
            summary = summarize_with_gemini(text)
            return summary
        except Exception as gemini_error:
            raise Exception(f"Summary generation failed: Both OpenAI and Gemini APIs are unavailable. OpenAI error: {str(openai_error)}, Gemini error: {str(gemini_error)}")

@app.post("/summarize")
def generate_summary(request: SummaryRequest):
    try:
        story_id = request.story_id
        text = request.text
        
        if not story_id and not text:
            raise HTTPException(
                status_code=400,
                detail="Either story_id or text must be provided"
            )
        
        if story_id:
            story = fetch_story(story_id)
            if story is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Story with ID {story_id} not found"
                )
            text = prepare_text_for_agent(story)

        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        # Generate summary using agent
        summary = get_summary(text)
        
        return {
            "summary": summary,
            "story_id": story_id if story_id else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

