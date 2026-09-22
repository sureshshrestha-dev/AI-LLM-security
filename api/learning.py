from fastapi import APIRouter, HTTPException
from core.learning_data import LEARNING_TOPICS

router = APIRouter(prefix="/api/learning", tags=["Learning Hub"])

@router.get("/topics")
def list_learning_topics():
    return [
        {
            "id": t["id"],
            "title": t["title"],
            "owasp_mapping": t["owasp_mapping"],
            "summary": t["summary"],
        }
        for t in LEARNING_TOPICS
    ]

@router.get("/topic/{topic_id}")
def get_learning_topic_detail(topic_id: str):
    topic = next((t for t in LEARNING_TOPICS if t["id"] == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail="Learning topic not found")
    return topic
