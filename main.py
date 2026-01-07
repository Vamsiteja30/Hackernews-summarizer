import time
import requests
from dataclasses import dataclass
from typing import List, Optional

from praval import start_agents, get_reef
from praval_agent import hn_summary_agent
from agent import prepare_text_for_agent

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

IMPORTANT_SCORE_THRESHOLD = 150
IMPORTANT_COMMENTS_THRESHOLD = 50
TRENDING_HOURS_THRESHOLD = 12


@dataclass
class Story:
    id: int
    title: str
    score: int
    by: str
    url: Optional[str]
    descendants: int
    time: int


def fetch_top_story_ids(limit: int = 10) -> List[int]:
    response = requests.get(TOP_STORIES_URL, timeout=30)
    response.raise_for_status()
    return response.json()[:limit]


def fetch_story(story_id: int) -> Optional[Story]:
    try:
        response = requests.get(ITEM_URL_TEMPLATE.format(id=story_id), timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data is None:
            return None

        return Story(
            id=data.get("id"),
            title=data.get("title", "No title"),
            score=data.get("score", 0),
            by=data.get("by", "unknown"),
            url=data.get("url"),
            descendants=data.get("descendants", 0),
            time=data.get("time", 0),
        )
    except Exception as e:
        print(f"Warning: Failed to fetch story {story_id}: {e}")
        return None


def fetch_top_stories(limit: int = 10) -> List[Story]:
    story_ids = fetch_top_story_ids(limit)
    stories = []
    
    for story_id in story_ids:
        story = fetch_story(story_id)
        if story is not None:
            stories.append(story)
    
    return stories


def is_important(story: Story) -> bool:
    return (
        story.score >= IMPORTANT_SCORE_THRESHOLD
        or story.descendants >= IMPORTANT_COMMENTS_THRESHOLD
    )


def age_in_hours(story: Story) -> float:
    current_time = time.time()
    return (current_time - story.time) / 3600


def is_trending(story: Story) -> bool:
    return age_in_hours(story) <= TRENDING_HOURS_THRESHOLD and is_important(story)


def main():
    print("Fetching top HackerNews stories...\n")
    
    try:
        stories = fetch_top_stories(limit=10)
        
        if not stories:
            print("No stories were fetched. Please check your internet connection.")
            return
        
        print(f"Successfully fetched {len(stories)} stories.\n")
        print("Praval agent integration active.\n")
        
        # Process all IMPORTANT/TRENDING stories
        for idx, story in enumerate(stories, start=1):
            link = story.url or f"https://news.ycombinator.com/item?id={story.id}"
            
            if is_trending(story):
                label = "TRENDING"
            elif is_important(story):
                label = "IMPORTANT"
            else:
                label = "NORMAL"

            print(
                f"[{label}] {idx:02d}. {story.title}\n"
                f"   Author: {story.by} | Score: {story.score} | Comments: {story.descendants}\n"
                f"   {link}"
            )
            
            if label in ["IMPORTANT", "TRENDING"]:

                agent_input_text = prepare_text_for_agent(story)
                
                try:
                    start_agents(
                        hn_summary_agent,
                        initial_data={
                            "type": "summary_request",
                            "text": agent_input_text
                        }
                    )
                    

                    get_reef().wait_for_completion()
                    print()  
                    
                except Exception as agent_error:
                    print(f"\n     Agent Error: {agent_error}")
                    print(f"   Error type: {type(agent_error).__name__}")
                    import traceback
                    traceback.print_exc()
                    print("   (Continuing with next story...)\n")
            else:
                print("   (Skipped - NORMAL posts are not sent to agent)\n")
        
        try:
            get_reef().shutdown()
        except:
            pass 
                
    except Exception as e:
        print(f"Error fetching stories: {e}")
        print("Please check your internet connection and try again.")
        try:
            get_reef().shutdown()
        except:
            pass


if __name__ == "__main__":
    main()  
