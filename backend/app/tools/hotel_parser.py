from sqlalchemy.orm import Session
from schemas.models import AccommodationInDB
from datetime import datetime

def find_hotels(db: Session, roadmap_id: int, destination: str, check_in_date: str, check_out_date: str, preference: str) -> str:
    """
    Finds a hotel based on user preference and saves it to the database.
    This is a mock tool.
    """
    print(f"[TOOL] find_hotels called with: roadmap_id={roadmap_id}, destination={destination}, check_in_date={check_in_date}, check_out_date={check_out_date}, preference={preference}")
    try:
        hotel_name = f"{preference.capitalize()} Hotel in {destination}"
        
        hotel = AccommodationInDB(
            roadmap_id=roadmap_id,
            name=hotel_name,
            check_in=datetime.strptime(check_in_date, "%Y-%m-%d"),
            check_out=datetime.strptime(check_out_date, "%Y-%m-%d"),
            price_total=500,
            location=destination,
            provider_url="https://example.com/hotel"
        )

        db.add(hotel)
        db.commit()
        
        return f"Found and saved a '{preference}' hotel in {destination}."
    except Exception as e:
        db.rollback()
        return f"An error occurred while finding hotels: {e}" 