import requests
from dataclasses import dataclass
from typing import List, Optional

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


@dataclass
class Story:
    id: int
    title: str
    score: int
    by: str
    url: Optional[str]
    descendants: int


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
    )


def fetch_top_stories(limit: int = 10) -> List[Story]:
    story_ids = fetch_top_story_ids(limit)
    return [fetch_story(story_id) for story_id in story_ids]


def main():
    print("Fetching top HackerNews stories...\n")
    stories = fetch_top_stories(limit=10)

    for idx, story in enumerate(stories, start=1):
        link = story.url or f"https://news.ycombinator.com/item?id={story.id}"
        print(
            f"{idx:02d}. {story.title}\n"
            f"   Author: {story.by} | Score: {story.score} | Comments: {story.descendants}\n"
            f"   {link}\n"
        )


if __name__ == "__main__":
    main()
