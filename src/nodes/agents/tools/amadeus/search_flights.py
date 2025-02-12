from .base import setup_amadeus_client
from langchain_core.tools import tool
from amadeus import ResponseError
from datetime import datetime
from src.cache.redis_cache import RedisCache

@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1
) -> dict:
    """
    Search for flight availabilities between two locations using the flight_offers_search endpoint.
    Uses a persistent Redis-based caching mechanism: if an identical API call (with the same parameters)
    is performed on the same day, the cached response is returned.
    
    Args:
        origin (str): IATA code of origin airport.
        destination (str): IATA code of destination airport.
        departure_date (str): Departure date in YYYY-MM-DD format.
        adults (int): Number of adult travelers (default: 1).
    
    Returns:
        dict: Dictionary containing flight availability information.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{origin}-{destination}-{departure_date}-{adults}-{today}"
    
    redis_cache = RedisCache(expiry_seconds=86400)
    
    cached_result = redis_cache.get(cache_key)
    if cached_result is not None:
        print(f"Flight researcher: returning cached result for {cache_key} ...\n")
        return cached_result

    amadeus = setup_amadeus_client()

    def format_response(flights):
        flight_infos = []
        for flight in flights:
            itinerary = flight.get('itineraries', [{}])[0]
            num_changes = len(itinerary.get('segments', [])) - 1
            segments = []
            for segment in itinerary.get('segments', []):
                segments.append({
                    'departure': segment['departure']['iataCode'],
                    'arrival': segment['arrival']['iataCode'],
                    'at': segment['departure']['at']
                })
            price = float(flight.get('price', {}).get('total', 'unknown'))
            flight_infos.append({
                'number_of_changes': num_changes,
                'segments': segments,
                'price': price,
                'currency': flight.get('price', {}).get('currency', 'unknown')
            })

        if not flight_infos:
            return []

        min_changes = min(f['number_of_changes'] for f in flight_infos)
        group_min = [f for f in flight_infos if f['number_of_changes'] == min_changes]
        group_next = [f for f in flight_infos if f['number_of_changes'] == (min_changes + 1)]
        group_min = sorted(group_min, key=lambda f: f['price'])[:5]
        group_next = sorted(group_next, key=lambda f: f['price'])[:5]
        return group_min + group_next

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=adults
        )
        result = {"status": "success", "flights": format_response(response.data)}
        
        redis_cache.set(cache_key, result)
        return result

    except ResponseError as error:
        result_error = {"status": "error", "message": str(error.response.body)}
        return result_error