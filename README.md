# ✈️ AI Travel Planner

AI Travel Planner is an intelligent assistant that helps users design personalized travel itineraries using Large Language Models (LLMs) and a team of autonomous agents. It integrates tools like Google Maps, Google Calendar, and Airbnb search to generate real-time routes, bookings, events, and recommendations — all from a simple user prompt.

---

## 🚀 Features

- 🗺️ **Smart Route Planning**: Optimized directions, travel time estimates, and nearby points of interest using Google Maps.
- 🏨 **Accommodation Finder**: Fetches and filters Airbnb stays based on budget, preferences, and location.
- 📅 **Calendar Integration**: Automatically creates daily itineraries and adds events to Google Calendar.
- 🤖 **Agent-Orchestrated Workflow**: Modular agents (Maps, Booking, Calendar) collaborate to generate accurate and context-aware plans.
- 🔐 **Secure API Handling**: OAuth2 token-based access for calendar and secure handling of all third-party API keys.

---

## 📦 Installation

### Prerequisites

- Python 3.9 or later
- Node.js (for `mcp-server-airbnb`)
- Virtual environment (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner

# Set up a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install MCP tool runner (if using Airbnb or other MCP-based tools)
npm install -g @openbnb/mcp-server-airbnb

```

## 🔧 Configuration

Ensure the following environment variables or Streamlit sidebar inputs are provided:

- OPENAI_API_KEY

- GOOGLE_MAPS_API_KEY

- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN

- (Optional) ACCUWEATHER_API_KEY if re-enabling weather tools

You can supply these through .env, Streamlit sidebar, or export them before launching

## ▶️ Usage

Start the app using:

```bash
streamlit run app.py

```
1. Enter your source and destination.

2. Choose travel dates, budget, preferences, and constraints.

3. Click "Plan My Trip" to let the AI agents build your itinerary.

4. Review routes, booking suggestions, and calendar events.

The app automatically spins up subprocesses for MCP tools and handles inter-agent communication using the Agno SDK.

## 🤝 Contributing

We welcome contributions to improve tool integrations, agent capabilities, and UX design.