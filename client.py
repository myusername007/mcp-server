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
            
            user_input = input("You: ")
            messages = [{"role": "user", "content": user_input}]

            while True:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=512,
                    tools=claude_tools,
                    messages=messages
                )
                
                if response.stop_reason == "end_turn":
                    print(f"\nClaude: {response.content[0].text}")
                    break
                
                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})
                    tool_results = []
                    
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f">>> Calling: {block.name}({block.input})")
                            result = await session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                            })
                    
                    messages.append({"role": "user", "content": tool_results})

asyncio.run(main())