import asyncio
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools

from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

stdio_server_params = StdioServerParameters(
    command="uv",
    args=["run", "servers/math_server.py"],
)

async def main():
    async with stdio_client(stdio_server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            
            await session.initialize()
            print("Session initialized with MCP Math Server!")

            tools = await load_mcp_tools(session)

            agent = create_react_agent(llm, tools)

            result = await agent.ainvoke(
                {"messages": [HumanMessage(content="What is 54 + 2 * 3?")]}
            )  
            
            print("\n--- Agent Answer ---")
            content = result["messages"][-1].content
            if isinstance(content, list):
                print(content[0]['text'])
            else:
                print(content)

if __name__ == "__main__":
    asyncio.run(main())
    