from amadeus import Client
import os

def setup_amadeus_client() -> Client:
    """Initialize Amadeus client with API credentials."""
    return Client(
        client_id=os.getenv('AMADEUS_API_KEY'),
        client_secret=os.getenv('AMADEUS_API_SECRET')
    )