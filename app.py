import asyncio
import os
import streamlit as st
import streamlit.components.v1 as components
from datetime import date
from agno.agent import Agent
from agno.team.team import Team
from agno.tools.mcp import MultiMCPTools
from agno.models.openai import OpenAIChat
import nest_asyncio

# Allow nested event loops (Streamlit-specific quirk)
nest_asyncio.apply()

async def run_agent(message: str):
    # Get API keys from session state
    google_maps_key = st.session_state.get('google_maps_key')
    accuweather_key = st.session_state.get('accuweather_key')
    openai_key = st.session_state.get('openai_key')
    google_client_id = st.session_state.get('google_client_id')
    google_client_secret = st.session_state.get('google_client_secret')
    google_refresh_token = st.session_state.get('google_refresh_token')

    # Validate required keys
    if not all([google_maps_key, accuweather_key, openai_key, google_client_id, google_client_secret, google_refresh_token]):
        raise ValueError("🚨 Please make sure all API keys are entered in the sidebar.")

    # Set environment variables for subprocesses
    env = {
        **os.environ,
        "GOOGLE_MAPS_API_KEY": google_maps_key,
        "ACCUWEATHER_API_KEY": accuweather_key,
        "OPENAI_API_KEY": openai_key,
        "GOOGLE_CLIENT_ID": google_client_id,
        "GOOGLE_CLIENT_SECRET": google_client_secret,
        "GOOGLE_REFRESH_TOKEN": google_refresh_token
    }

    # MCP tools to run via subprocess
    mcp_commands = [
        "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt",
        "python3 maps_mcp.py",
        "python3 weather_mcp.py",
        "python3 calendar_mcp.py"
    ]
    os.environ["OPENAI_API_KEY"] = openai_key

    # Launch MCP tools and agents
    print("🚀 Launching with env:")
    for k in env:
        if "KEY" in k or "TOKEN" in k:
            print(f"{k} = {env[k][:5]}***")

    async with MultiMCPTools(mcp_commands, env=env) as mcp_tools:
        
        maps_agent = Agent(
            tools=[mcp_tools],
            model=OpenAIChat(id="gpt-4o-mini", api_key=openai_key),
            name="Maps Agent",
            goal="""As a Maps Agent, your responsibilities include:
            1. Finding optimal routes between locations
            2. Identifying points of interest near destinations
            3. Calculating travel times and distances
            4. Suggesting transportation options
            5. Finding nearby amenities and services
            6. Providing location-based recommendations
            
            Always consider:
            - Traffic conditions and peak hours
            - Alternative routes and transportation modes
            - Accessibility and convenience
            - Safety and well-lit areas
            - Proximity to other planned activities"""
        )

        weather_agent = Agent(
            tools=[mcp_tools],
            model=OpenAIChat(id="gpt-4o-mini", api_key=openai_key),
            name="Weather Agent",
            goal="""As a Weather Agent, your responsibilities include:
            1. Providing detailed weather forecasts for destinations
            2. Alerting about severe weather conditions
            3. Suggesting weather-appropriate activities
            4. Recommending the best travel times based on the weather conditions.
            5. Providing seasonal travel recommendations
            
            Always consider:
            - Temperature ranges and comfort levels
            - Precipitation probability
            - Wind conditions
            - UV index and sun protection
            - Seasonal variations
            - Weather alerts and warnings"""
        )

        booking_agent = Agent(
            tools=[mcp_tools],
            model=OpenAIChat(id="gpt-4o-mini", api_key=openai_key),
            name="Booking Agent",
            goal="""As a Booking Agent, your responsibilities include:
            1. Finding accommodations within budget on airbnb
            2. Comparing prices across platforms
            3. Checking availability for specific dates
            4. Verifying amenities and policies
            5. Finding last-minute deals when applicable
            
            Always consider:
            - Location convenience
            - Price competitiveness
            - Cancellation policies
            - Guest reviews and ratings
            - Amenities matching preferences
            - Special requirements or accessibility needs"""
        )
        calendar_agent = Agent(
            tools=[mcp_tools],
            model=OpenAIChat(id="gpt-4o-mini", api_key=openai_key),
            name="Calendar Agent",
            goal="""As a Calendar Agent, your responsibilities include:
            1. Creating detailed travel itineraries
            2. Setting reminders for bookings and check-ins
            3. Scheduling activities and reservations
            4. Adding reminders for booking deadlines, check-ins, and other important event.
            5. Avoiding duplicate or overlapping events
            6. Coordinating with other team members' schedules
            
            Always consider:
            - Time zone differences
            - Travel duration between activities
            - Buffer time for unexpected delays
            - Important deadlines and check-in times
            - Synchronization with other team members
            - Avoid re-scheduling the same activity more than once
            - Check existing calendar before calling `create_event()`
            """
        )

        team = Team(
            members=[maps_agent, weather_agent, booking_agent, calendar_agent],
            name="Travel Planning Team",
            markdown=True,
            show_tool_calls=True,
            instructions="""As a Travel Planning Team, coordinate to create comprehensive travel plans:
            1. Share information between agents to ensure consistency
            2. Consider dependencies between different aspects of the trip
            3. Prioritize user preferences and constraints
            4. Provide backup options when primary choices are unavailable
            5. Maintain a balance between planned activities and free time
            6. Consider local events and seasonal factors
            7. Ensure all recommendations align with the user's budget
            8. Provide a detailed breakdown of the trip, including bookings, routes, weather, and planned activities.
            """
        )

        result = await team.arun(message)

        # Collect final markdown response
        final_output = result.messages[-1].content

        # Check for tool outputs from maps_agent
        # Display tool responses from agents
        for msg in result.messages:
            

            if hasattr(msg, "tool_response") and isinstance(msg.tool_response, dict):
                tool_data = msg.tool_response
                st.markdown(f"### 🔧 Tool Response\n```json\n{json.dumps(tool_data, indent=2)}\n```")

                # 🗺️ Google Maps route summary and link
                if "map_link" in tool_data:
                    st.markdown(f"🗺️ [**View Route in Google Maps**]({tool_data['map_link']})")

                if "route_summary" in tool_data:
                    st.markdown(f"**🧭 Route Summary:** {tool_data['route_summary']}")

                # 📅 Calendar event summary
                if msg.name == "Calendar Agent":
                    if "events" in tool_data:
                        st.markdown("📅 **Calendar Events Added:**")
                        for ev in tool_data["events"]:
                            st.markdown(f"- 📌 {ev.get('summary')} – [Open]({ev.get('calendar_link', 'https://calendar.google.com/calendar/u/0/r?tab=mc')})")
                    elif "event_summary" in tool_data:
                        st.markdown(f"- 🔗 [View in Google Calendar]({tool_data.get('calendar_link', 'https://calendar.google.com/calendar/u/0/r?tab=mc')})")

        # Add the agent final markdown response
        return final_output

    
    

# -------------------- Streamlit App --------------------

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")
st.title("✈️ AI Travel Planner")

# Sidebar for API keys
with st.sidebar:
    st.header("🔑 API Keys")
    st.session_state.google_maps_key = st.text_input("Google Maps API Key", type="password")
    st.session_state.accuweather_key = st.text_input("AccuWeather API Key", type="password")
    st.session_state.openai_key = st.text_input("OpenAI API Key", type="password")
    st.session_state.google_client_id = st.text_input("Google Client ID", type="password")
    st.session_state.google_client_secret = st.text_input("Google Client Secret", type="password")
    st.session_state.google_refresh_token = st.text_input("Google Refresh Token", type="password")

    all_keys_filled = all([
        st.session_state.google_maps_key,
        st.session_state.accuweather_key,
        st.session_state.openai_key,
        st.session_state.google_client_id,
        st.session_state.google_client_secret,
        st.session_state.google_refresh_token
    ])
    if not all_keys_filled:
        st.warning("Please fill in all API keys.")
    else:
        st.success("✅ API keys loaded!")

col1, col2 = st.columns(2)

with col1:
    # Source and Destination
    source = st.text_input("Source", placeholder="Enter your departure city")
    destination = st.text_input("Destination", placeholder= "Enter your destination city")
    
    # Travel Dates
    travel_dates = st.date_input(
        "Travel Dates",
        [date.today(), date.today()],
        min_value=date.today(),
        help="Select your travel dates"
    )

with col2:
    # Budget
    budget = st.number_input(
        "Budget (in USD)",
        min_value=0,
        max_value=10000,
        step=100,
        help="Enter your total budget for the trip"
    )
    
    # Travel Preferences
    travel_preferences = st.multiselect(
        "Travel Preferences",
        ["Adventure", "Relaxation", "Sightseeing", "Cultural Experiences", 
         "Beach", "Mountain", "Luxury", "Budget-Friendly", "Food & Dining",
         "Shopping", "Nightlife", "Family-Friendly"],
        help="Select your travel preferences"
    )

# Additional preferences
st.subheader("Additional Preferences")
col3, col4 = st.columns(2)

with col3:
    accommodation_type = st.selectbox(
        "Preferred Accommodation",
        ["Any", "Hotel", "Hostel", "Apartment", "Resort"],
        help="Select your preferred type of accommodation"
    )
    
    transportation_mode = st.multiselect(
        "Preferred Transportation",
        ["Train", "Bus", "Flight", "Rental Car"],
        help="Select your preferred modes of transportation"
    )

with col4:
    dietary_restrictions = st.multiselect(
        "Dietary Restrictions",
        ["None", "Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher"],
        help="Select any dietary restrictions"
    )

# Submit Button
if st.button("Plan My Trip", type="primary", disabled=not all_keys_filled):
    if not source or not destination:
        st.error("Please enter both source and destination cities.")
    elif not travel_preferences:
        st.warning("Consider selecting some travel preferences for better recommendations.")
    else:
        # Create a loading spinner
        with st.spinner("🤖 AI Agents are planning your perfect trip..."):
            try:
                # Construct the message for the agents
                message = f"""
                Plan a travel itinerary with the following details:

                - From: {source}
                - To: {destination}
                - Dates: {travel_dates[0]} to {travel_dates[1]}
                - Budget in USD: ${budget}
                - Preferences: {', '.join(travel_preferences)}
                - Accommodation: {accommodation_type}
                - Transportation: {', '.join(transportation_mode)}
                - Dietary Restrictions: {', '.join(dietary_restrictions)}

                You are a team of 4 agents (Maps, Weather, Booking, Calendar). Please coordinate to complete the following tasks:

                1. **Maps Agent**:
                - Use `get_route_summary()` to get a route from {source} to {destination}.
                - Include a Google Maps `map_link`.
                - Suggest local transit options or alternatives for in-city travel based on {transportation_mode} in {destination}

                2. **Weather Agent**:
                - Use `get_hourly_weather()` to fetch weather forecasts for each day of the trip at both {source} and {destination}.
                - Summarize the expected daily weather (temperature, rain chance, recommendations).

                3. **Booking Agent**:
                - Recommend at least 3 accommodations within budget using Airbnb tools.
                - Show prices, amenities, and links.
                - Accommodations should be relevant to {accommodation_type} and {travel_preferences}.


                4. **Calendar Agent**:
                - For each travel day from {travel_dates[0]} to {travel_dates[1]}, schedule:
                    - Departure and return travel
                    - Check-ins/check-outs
                    - Generate 2-3 **unique** activities per day based on {destination}, {travel_preferences}, {dietary_restrictions} and {budget}
                    - Ensure no time overlaps with travel or check-in/out
                    - Use `create_event()` to add events to the calendar
                    - **Before calling `create_event()`, check if a similar event is already scheduled**
                    - Avoid duplicate names, times, or activities across the same day
                    

                Make sure:
                - All activities and events are visible in the output.
                - Agents use tool calls directly.
                - Avoid unnecessary filler or vague language.
                """

                
                # Run the agents
                response = asyncio.run(run_agent(message))
                
                # Display the response
                st.success("✅ Your travel plan is ready!")
                st.markdown(response)
                
            except Exception as e:
                st.error(f"An error occurred while planning your trip: {str(e)}")
                st.info("Please try again or contact support if the issue persists.")

# Add a footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Powered by AI Travel Planning Agents</p>
    <p>Your personal travel assistant for creating memorable experiences</p>
</div>
""", unsafe_allow_html=True)