from sqlalchemy.orm import Session
from schemas.models import Place

def find_activities(db: Session, roadmap_id: int, destination: str, interests: list) -> str:
    """
    Finds activities based on user interests and saves them to the database.
    This is a mock tool.
    """
    print(f"[TOOL] find_activities called with: roadmap_id={roadmap_id}, destination={destination}, interests={interests}")
    try:
        for interest in interests:
            activity = Place(
                roadmap_id=roadmap_id,
                name=f"{interest.capitalize()} Spot",
                category=interest,
                location=destination,
                duration_min=120,
                rating=4.5,
                url=f"https://example.com/activity/{interest}"
            )
            db.add(activity)
        
        db.commit()
        return f"Found and saved {len(interests)} activities in {destination} based on your interests."
    except Exception as e:
        db.rollback()
        return f"An error occurred while finding activities: {e}" 