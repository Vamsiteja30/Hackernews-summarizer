import time
import requests
from dataclasses import dataclass
from typing import List, Optional

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
    response = requests.get(TOP_STORIES_URL, timeout=10)
    response.raise_for_status()
    return response.json()[:limit]


def fetch_story(story_id: int) -> Story:
    response = requests.get(ITEM_URL_TEMPLATE.format(id=story_id), timeout=10)
    response.raise_for_status()
    data = response.json()

    return Story(
        id=data.get("id"),
        title=data.get("title", "No title"),
        score=data.get("score", 0),
        by=data.get("by", "unknown"),
        url=data.get("url"),
        descendants=data.get("descendants", 0),
        time=data.get("time", 0),
    )


def fetch_top_stories(limit: int = 10) -> List[Story]:
    story_ids = fetch_top_story_ids(limit)
    return [fetch_story(story_id) for story_id in story_ids]


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
    stories = fetch_top_stories(limit=10)

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
            f"   {link}\n"
        )


if __name__ == "__main__":
    main()
    
