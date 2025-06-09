from sqlalchemy.orm import Session
from schemas.models import Ticket, RoadmapInDB
from datetime import datetime, date
import os

def find_tickets(db: Session, roadmap_id: int, departure_id: str, destination_id: str, start_date: str, end_date: str) -> str:
    """
    Finds flight tickets for the given departure and destination and dates and saves them to the database.
    Returns a list of up to 8 best round-trip flight options, each with both outbound and return segments if possible.
    Each segment includes a 'direction' field: 'outbound' or 'return'.
    Each flight includes number of stops and stop airport codes.
    """
    print(f"[TOOL] find_tickets called with: roadmap_id={roadmap_id}, departure_id={departure_id}, destination_id={destination_id}, start_date={start_date}, end_date={end_date}")
    try:
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": destination_id,
            "outbound_date": start_date,
            "return_date": end_date,
            "currency": "KZT",
            "hl": "en",
            "api_key": os.environ.get("SERPAPI_API_KEY")
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        print(results)

        flights_list = results.get('best_flights') or results.get('other_flights') or []
        flights_list = flights_list[:20]  # get more to allow pairing

        # Separate all flights into outbound and return
        outbound = []
        returns = []
        for option in flights_list:
            if 'flights' in option and option['flights']:
                seg = option['flights'][0]
                dep_date = seg['departure_airport']['time'].split(' ')[0]
                if dep_date == start_date:
                    outbound.append((option, seg))
                elif dep_date == end_date:
                    returns.append((option, seg))
                else:
                    # fallback: treat as outbound if before end_date, else return
                    if dep_date < end_date:
                        outbound.append((option, seg))
                    else:
                        returns.append((option, seg))

        # Pair outbound and return flights
        paired = []
        for out_opt, out_seg in outbound:
            for ret_opt, ret_seg in returns:
                # Match by airports: outbound arrival == return departure
                if out_seg['arrival_airport']['id'] == ret_seg['departure_airport']['id']:
                    # Build segments
                    segments = []
                    for seg, direction in [(out_seg, 'outbound'), (ret_seg, 'return')]:
                        segments.append({
                            "from_airport": {
                                "name": seg['departure_airport']['name'],
                                "code": seg['departure_airport']['id'],
                                "time": seg['departure_airport']['time'],
                            },
                            "to_airport": {
                                "name": seg['arrival_airport']['name'],
                                "code": seg['arrival_airport']['id'],
                                "time": seg['arrival_airport']['time'],
                            },
                            "airline": seg.get('airline', 'Unknown'),
                            "flight_number": seg.get('flight_number', 'Unknown'),
                            "travel_class": seg.get('travel_class', 'Unknown'),
                            "airplane": seg.get('airplane', 'Unknown'),
                            "duration": int(seg.get('duration', 0)),
                            "direction": direction
                        })
                    # Price: sum if both, else just outbound
                    price = out_opt.get('price', 0)
                    if ret_opt.get('price'):
                        try:
                            price = int(price) + int(ret_opt.get('price', 0))
                        except Exception:
                            pass
                    paired.append({
                        "segments": segments,
                        "price": price,
                        "currency": results.get('search_parameters', {}).get('currency', 'Unknown'),
                        "type": out_opt.get('type', 'Unknown'),
                        "buy_url": out_opt.get('link') or ret_opt.get('link') or "Not available",
                        "num_stops": 0,  # single segment each way
                        "stop_airports": []
                    })
        # If no pairs found, fallback to original logic (single direction per option)
        if paired:
            structured_flights = paired[:8]
        else:
            structured_flights = []
            for option in flights_list[:8]:
                if 'flights' in option and option['flights']:
                    seg = option['flights'][0]
                else:
                    continue
                dep_time = seg['departure_airport']['time']
                direction = None
                try:
                    dep_date = dep_time.split(' ')[0]
                    if dep_date == start_date:
                        direction = 'outbound'
                    elif dep_date == end_date:
                        direction = 'return'
                    else:
                        direction = 'outbound' if dep_date < end_date else 'return'
                except Exception:
                    direction = 'unknown'
                structured_flights.append({
                    "segments": [{
                        "from_airport": {
                            "name": seg['departure_airport']['name'],
                            "code": seg['departure_airport']['id'],
                            "time": seg['departure_airport']['time'],
                        },
                        "to_airport": {
                            "name": seg['arrival_airport']['name'],
                            "code": seg['arrival_airport']['id'],
                            "time": seg['arrival_airport']['time'],
                        },
                        "airline": seg.get('airline', 'Unknown'),
                        "flight_number": seg.get('flight_number', 'Unknown'),
                        "travel_class": seg.get('travel_class', 'Unknown'),
                        "airplane": seg.get('airplane', 'Unknown'),
                        "duration": int(seg.get('duration', 0)),
                        "direction": direction
                    }],
                    "price": option.get('price', 'Unknown'),
                    "currency": results.get('search_parameters', {}).get('currency', 'Unknown'),
                    "type": option.get('type', 'Unknown'),
                    "buy_url": option.get('link') or "Not available",
                    "num_stops": 0,
                    "stop_airports": []
                })
        print(structured_flights)
        return structured_flights
    except Exception as e:
        db.rollback()
        return f"An error occurred while finding tickets: {e}" 