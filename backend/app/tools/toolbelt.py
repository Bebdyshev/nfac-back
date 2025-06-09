from langchain.tools import tool
from sqlalchemy.orm import Session
from .ticket_parser import find_tickets
from .hotel_parser import find_hotels
from .activity_parser import find_activities

class TravelToolBelt:
    def __init__(self, db: Session, roadmap_id: int):
        self.db = db
        self.roadmap_id = roadmap_id

    @tool
    def find_tickets_tool(self, destination: str, start_date: str, end_date: str) -> str:
        """Finds flight tickets for the given destination and dates."""
        return find_tickets(self.db, self.roadmap_id, destination, start_date, end_date)

    @tool
    def find_hotels_tool(self, destination: str, check_in_date: str, check_out_date: str, preference: str) -> str:
        """Finds a hotel based on user preference."""
        return find_hotels(self.db, self.roadmap_id, destination, check_in_date, check_out_date, preference)

    @tool
    def find_activities_tool(self, destination: str, interests: list) -> str:
        """Finds activities based on user interests."""
        return find_activities(self.db, self.roadmap_id, destination, interests) 