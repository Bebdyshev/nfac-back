from serpapi import GoogleSearch

params = {
  "engine": "google_flights",
  "departure_id": "AKX",
  "arrival_id": "NQZ",
  "outbound_date": "2025-07-01",
  "return_date": "2025-07-03",
  "currency": "KZT",
  "hl": "en",
  "api_key": "fc601d3949acd474bbe430731df10f3b124862a633a80be4d12f1afbb84fb5c4"
}

search = GoogleSearch(params)
results = search.get_dict()
print(results)

def format_duration(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h}h {m}m"

def get_flights_structured(results, top_n=5):
    best_flights = results.get('best_flights', [])[:top_n]
    structured = []
    for option in best_flights:
        flight = option['flights'][0]  # usually only one per option
        # Try to get the booking link
        link = None
        if 'ticket_info' in option and 'link' in option['ticket_info']:
            link = option['ticket_info']['link']
        elif 'link' in option:
            link = option['link']
        else:
            # Sometimes the link is inside the flight dict
            link = flight.get('ticket_info', {}).get('link', None)
        structured.append({
            "from_airport": {
                "name": flight['departure_airport']['name'],
                "code": flight['departure_airport']['id'],
                "time": flight['departure_airport']['time'],
            },
            "to_airport": {
                "name": flight['arrival_airport']['name'],
                "code": flight['arrival_airport']['id'],
                "time": flight['arrival_airport']['time'],
            },
            "airline": flight.get('airline', 'Unknown'),
            "flight_number": flight.get('flight_number', 'Unknown'),
            "travel_class": flight.get('travel_class', 'Unknown'),
            "airplane": flight.get('airplane', 'Unknown'),
            "duration": format_duration(flight.get('duration', 0)),
            "price": option.get('price', 'Unknown'),
            "currency": results.get('search_parameters', {}).get('currency', 'Unknown'),
            "type": option.get('type', 'Unknown'),
            "buy_url": link or "Not available"
        })
    return structured

print(get_flights_structured(results))