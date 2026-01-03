from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
import os
import httpx
from mcp.client.streamable_http import streamable_http_client
from strands.tools.mcp.mcp_client import MCPClient
from strands_tools import calculator

# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful assistant with access to:
1. Calculator for math problems
2. JSONPlaceholder API for user and post data (listUsers, getUser, listPosts)"""

# Model configuration from environment variable
MODEL_ID = os.getenv("MODEL_ID", "us.anthropic.claude-3-5-haiku-20241022-v1:0")

# Gateway configuration
GATEWAY_URL = ""
USER_POOL_ID = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

# Global agent and MCP client for reuse across invocations
agent = None
mcp_client = None

def get_cognito_token():
    """Get OAuth2 token from Cognito using client credentials flow"""
    token_url = "https://agentcore-c8c43165.auth.us-west-2.amazoncognito.com/oauth2/token"

    response = httpx.post(
        token_url,
        data=f"grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_mcp_client():
    """Create and start MCP client"""
    global mcp_client
    if mcp_client is not None:
        return mcp_client

    token = get_cognito_token()

    # Create httpx client with auth header
    http_client = httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    )

    # Create MCP transport
    def create_transport():
        return streamable_http_client(GATEWAY_URL, http_client=http_client)

    mcp_client = MCPClient(create_transport)
    mcp_client.start()
    return mcp_client

def create_agent(tools):
    """Create agent with lazy loading pattern for performance"""
    global agent
    if agent is None:
        agent = Agent(
            model=MODEL_ID,
            tools=tools,
            system_prompt=SYSTEM_PROMPT
        )
    return agent

# Initialize the Bedrock Agent Core application
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entry point"""
    # Get MCP client and its tools
    client = get_mcp_client()
    mcp_tools = client.list_tools_sync()

    # Combine local calculator with Gateway tools
    all_tools = [calculator] + list(mcp_tools)

    agent = create_agent(all_tools)
    prompt = payload.get("prompt", "Hello!")
    result = agent(prompt)

    return {
        "response": result.message.get('content', [{}])[0].get('text', str(result))
    }

if __name__ == "__main__":
    app.run()
