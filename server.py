from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My First MCP Server")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    weather_data = {
        "Kyiv": "Rainy, 12°C",
        "London": "Cloudy, 15°C",
        "Lviv": "Sunny, 18°C"
    }
    return weather_data.get(city, "Unknown city")

@mcp.tool()
def calculate(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Invalid expression"

if __name__ == "__main__":
    mcp.run()