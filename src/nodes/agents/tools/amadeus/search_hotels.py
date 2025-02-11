from amadeus import ResponseError
import random
import time
from langchain_core.tools import tool
from .base import setup_amadeus_client
from datetime import datetime
from src.cache.redis_cache import RedisCache

@tool
def search_hotels(
    city_code: str,
    check_in_date: str,
    check_out_date: str,
    adults: str
) -> dict:
    """
    Search for hotel offers in a specific city with persistent caching using Redis.
    
    If an identical search (based on city_code, check-in/out dates, adults, and today's date)
    is made, the cached response is returned to avoid repetitive API calls.
    
    Args:
        city_code (str): IATA city code (e.g., 'MAD' for Madrid)
        check_in_date (str): Check-in date in YYYY-MM-DD format
        check_out_date (str): Check-out date in YYYY-MM-DD format
        adults (str): Number of adults (e.g., "2")
    
    Returns:
        dict: Dictionary containing hotel offers information.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{city_code}-{check_in_date}-{check_out_date}-{adults}-{today}"
    
    redis_cache = RedisCache(expiry_seconds=86400)
    
    cached_result = redis_cache.get(cache_key)
    if cached_result is not None:
        print(f"Hotel researcher: returning cached result for {cache_key} ...\n")
        return cached_result

    amadeus = setup_amadeus_client()

    def format_response(hotel_offers):
        formatted_response = []
        for hotel in hotel_offers:
            hotel_offer = {'hotel_name': hotel['hotel']['name'], 'offers': []}
            for offer in hotel['offers']:
                hotel_offer['offers'].append({
                    "room": offer['room'],
                    "price": offer['price']['total'],
                    "policies": offer['policies']
                })
            formatted_response.append(hotel_offer)
        return formatted_response

    try:
        hotels_response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        )
        
        hotel_offers = []

        shuffled_hotels = hotels_response.data
        random.shuffle(shuffled_hotels)
        for hotel in shuffled_hotels:
            if len(hotel_offers) >= 5:
                break
            try:
                time.sleep(1)
                hotel_offer = amadeus.shopping.hotel_offers_search.get(
                    hotelIds=hotel['hotelId'],
                    adults=adults,
                    checkInDate=check_in_date,
                    checkOutDate=check_out_date
                )
                hotel_offers.extend(hotel_offer.data)
            except ResponseError:
                continue
        
        result = {"status": "success", "hotels": format_response(hotel_offers)}
        redis_cache.set(cache_key, result)
        return result
    
    except ResponseError as error:
        result_error = {"status": "error", "message": str(error.response.body)}
        return result_error
