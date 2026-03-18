import anthropic
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
load_dotenv()

async def main():
    client = anthropic.Anthropic()
    
    server_params = StdioServerParameters(
    command="/Users/root7/mcp_server/.venv/bin/python",
    args=["server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Отримуємо tools з MCP сервера
            mcp_tools = await session.list_tools()
            
            # Конвертуємо в формат Claude
            claude_tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                }
                for t in mcp_tools.tools
            ]
            
            # Передаємо tools в Claude
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                tools=claude_tools,  # <-- ось це було відсутнє
                messages=[{"role": "user", "content": "What's the weather in Kyiv and what is 25 * 4?"}]
            )
            
            # Якщо Claude хоче викликати tool
            if response.stop_reason == "tool_use":
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"Calling: {block.name}({block.input})")
                        # Викликаємо через MCP сесію
                        result = await session.call_tool(block.name, block.input)
                        print(f"Result: {result.content[0].text}")

asyncio.run(main())