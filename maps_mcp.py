import os 
from fastmcp import FastMCP
from dotenv import load_dotenv
from aiohttp import ClientSession
import logging
import sys

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="DEBUG: %(asctime)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


mcp = FastMCP("Google Maps MCP", dependencies=["python-dotenv", "aiohttp"])

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@mcp.tool()
async def get_route_summary(origin: str, destination: str) -> dict:

    """
    Get a route summary and Google Maps link between two locations.
    Args:
        origin: Starting location (e.g., "Portland")
        destination: Destination location (e.g., "Dallas")
    Returns:
        dict with route summary and Google Maps link
    """

    logger.debug(f"Getting route summary from {origin} to {destination}")

    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
    
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_MAPS_API_KEY
    }

    async with ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            
            data = await response.json()

    logger.debug(f"Directions API response: {data}")

    if data["status"] != "OK":
        raise Exception(f"Error fetching route data: {data['status']}")
    
    leg = data["routes"][0]["legs"][0]
    summary = f"{leg['distance']['text']} in approximately {leg['duration']['text']}"
    link = f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{destination.replace(' ', '+')}"

    logger.debug(f"Returning route summary: {summary}, link: {link}")

    return {
        "route_summary": summary,
        "map_link": link,
        "map_embed": f'<iframe width="100%" height="300" frameborder="0" style="border:0" '
                 f'src="https://www.google.com/maps/embed/v1/directions?key={GOOGLE_MAPS_API_KEY}&origin={origin}&destination={destination}" '
                 f'allowfullscreen></iframe>' 
    }
    print("✅ Sent maps tool response:", {"route_summary": summary, "map_link": link})


def main():

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise

if __name__ == "__main__":
    main()


