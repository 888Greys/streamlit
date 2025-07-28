from typing import TypedDict, Annotated
import os
import requests
import random

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langchain_groq import ChatGroq
from langchain.tools import Tool

from retriever import guest_info_tool

# Web Search Tool
try:
    from ddgs import DDGS
    
    def web_search(query: str) -> str:
        """Search the web for current information about people, events, or topics."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                
            if not results:
                return "No search results found for your query."
            
            # Format the results nicely
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(f"{i}. {result['title']}\n   {result['body']}\n   Source: {result['href']}")
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            return f"I apologize, but I encountered an issue while searching: {str(e)}"
    
    web_search_tool = Tool(
        name="web_search",
        func=web_search,
        description="Search the web for current information about people, events, or topics. Use this when you need up-to-date information that might not be in the guest database."
    )
except ImportError:
    # Fallback if ddgs is not available
    def web_search_fallback(query: str) -> str:
        return "Web search is currently unavailable. Please try again later."
    
    web_search_tool = Tool(
        name="web_search",
        func=web_search_fallback,
        description="Search the web for current information (currently unavailable)."
    )

# Weather Tool
WEATHER_API_KEY = "292f64290fcb8e22685c42af72a3beb1"

def get_fireworks_advice(condition: str, wind_kmh: float) -> str:
    """Generate fireworks advice based on weather conditions."""
    if condition in ["Clear", "Sunny"] and wind_kmh < 15:
        return " Perfect conditions for fireworks! 🎆"
    elif condition in ["Clouds"] and wind_kmh < 20:
        return " Good conditions for fireworks with some clouds. 🌤️"
    elif wind_kmh >= 20:
        return f" Caution advised for fireworks due to strong winds ({wind_kmh} km/h). 💨"
    elif condition in ["Rain", "Drizzle", "Thunderstorm"]:
        return " Fireworks should be postponed due to precipitation. ⛈️"
    elif condition in ["Snow", "Mist", "Fog"]:
        return " Poor visibility conditions for fireworks. 🌫️"
    else:
        return " Weather conditions are marginal for fireworks. 🌤️"

def get_realistic_dummy_weather(location: str) -> str:
    """Generate realistic dummy weather data based on location."""
    location_patterns = {
        "london": {"base_temp": 12, "conditions": ["Cloudy", "Rainy", "Partly Cloudy", "Clear"]},
        "paris": {"base_temp": 15, "conditions": ["Clear", "Cloudy", "Partly Cloudy", "Rainy"]},
        "new york": {"base_temp": 18, "conditions": ["Clear", "Cloudy", "Partly Cloudy", "Windy"]},
        "tokyo": {"base_temp": 20, "conditions": ["Clear", "Cloudy", "Humid", "Partly Cloudy"]},
        "miami": {"base_temp": 28, "conditions": ["Sunny", "Partly Cloudy", "Thunderstorm", "Clear"]},
        "seattle": {"base_temp": 14, "conditions": ["Rainy", "Cloudy", "Drizzle", "Partly Cloudy"]},
        "los angeles": {"base_temp": 24, "conditions": ["Sunny", "Clear", "Partly Cloudy", "Hazy"]},
        "chicago": {"base_temp": 16, "conditions": ["Windy", "Clear", "Cloudy", "Partly Cloudy"]},
    }
    
    default_pattern = {"base_temp": 18, "conditions": ["Clear", "Cloudy", "Partly Cloudy", "Rainy"]}
    pattern = location_patterns.get(location.lower(), default_pattern)
    
    temp_c = pattern["base_temp"] + random.randint(-8, 8)
    condition = random.choice(pattern["conditions"])
    humidity = random.randint(40, 85)
    wind_kmh = random.randint(5, 25)
    
    condition_descriptions = {
        "Clear": "Clear Sky", "Sunny": "Sunny", "Cloudy": "Overcast Clouds",
        "Partly Cloudy": "Partly Cloudy", "Rainy": "Light Rain", "Drizzle": "Light Drizzle",
        "Thunderstorm": "Thunderstorm", "Windy": "Clear and Windy", "Humid": "Clear and Humid",
        "Hazy": "Hazy", "Snow": "Light Snow", "Mist": "Misty"
    }
    
    description = condition_descriptions.get(condition, condition)
    fireworks_advice = get_fireworks_advice(condition, wind_kmh)
    
    return f"Weather in {location}: {description}, {temp_c}°C, Humidity: {humidity}%, Wind: {wind_kmh} km/h.{fireworks_advice} [Simulated data]"

def get_weather_info(location: str) -> str:
    """Fetches weather information for a given location, with fallback to realistic dummy data."""
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(base_url, params=params, timeout=5)
        
        if response.status_code == 200:
            weather_data = response.json()
            temp_c = round(weather_data["main"]["temp"])
            condition = weather_data["weather"][0]["main"]
            description = weather_data["weather"][0]["description"].title()
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data.get("wind", {}).get("speed", 0)
            wind_kmh = round(wind_speed * 3.6, 1)
            fireworks_advice = get_fireworks_advice(condition, wind_kmh)
            return f"Weather in {location}: {description}, {temp_c}°C, Humidity: {humidity}%, Wind: {wind_kmh} km/h.{fireworks_advice}"
    except Exception:
        pass
    
    return get_realistic_dummy_weather(location)

weather_info_tool = Tool(
    name="get_weather_info",
    func=get_weather_info,
    description="Fetches weather information for a given location and provides fireworks scheduling advice."
)

# Get the Groq API token from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Generate the chat interface, including the tools
chat = ChatGroq(
    model="gemma2-9b-it",
    api_key=GROQ_API_KEY,
    temperature=0.1,
)

tools = [guest_info_tool, web_search_tool, weather_info_tool]
chat_with_tools = chat.bind_tools(tools)

# Generate the AgentState and Agent graph
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def assistant(state: AgentState):
    return {
        "messages": [chat_with_tools.invoke(state["messages"])],
    }

## The graph
builder = StateGraph(AgentState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message requires a tool, route to tools
    # Otherwise, provide a direct response
    tools_condition,
)
builder.add_edge("tools", "assistant")

alfred = builder.compile()

# Add a system message to make Alfred more butler-like
system_message = HumanMessage(content="""You are Alfred, a sophisticated and polite butler assistant at an elegant gala event. You have access to:
1. A guest information system with details about gala attendees (guest_info_retriever)
2. Web search capabilities for current information (web_search)
3. Weather information for fireworks planning (get_weather_info)

Your capabilities:
- Guest inquiries: Use guest_info_retriever for attendee information
- Current events/general info: Use web_search for up-to-date information  
- Weather/fireworks: Use get_weather_info to check conditions and provide fireworks scheduling advice

Always respond in a refined, butler-like manner and maintain a professional, courteous tone befitting a distinguished butler.""")

# Demonstrate conversation memory
print("🎩 ALFRED WITH CONVERSATION MEMORY")
print("=" * 60)

# First interaction
print("\n🧪 First Interaction:")
print("Query: Tell me about 'Lady Ada Lovelace'. What's her background and how is she related to me?")
print("-" * 50)

response = alfred.invoke({"messages": [system_message, HumanMessage(content="Tell me about 'Lady Ada Lovelace'. What's her background and how is she related to me?")]})

print("🎩 Alfred's Response:")
print(response['messages'][-1].content)
print()

# Second interaction (referencing the first)
print("🧪 Second Interaction (with memory):")
print("Query: What projects is she currently working on?")
print("-" * 50)

response = alfred.invoke({"messages": response["messages"] + [HumanMessage(content="What projects is she currently working on?")]})

print("🎩 Alfred's Response:")
print(response['messages'][-1].content)