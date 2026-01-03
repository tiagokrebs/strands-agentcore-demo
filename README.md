# Strands AgentCore Demo

## Deploy to AWS

### Option 1: Python Runtime
```bash
uv run agentcore configure -e my_agent.py
uv run agentcore launch
uv run agentcore invoke '{"prompt": "what is 40 plus 4?"}'
```

### Option 2: Docker (auto-generated)
Will create a `Dockerfile` inside `.bedrock_agentcore`
```bash
uv run agentcore configure -e my_agent.py
# Edit .bedrock_agentcore.yaml: deployment_type: container
uv run agentcore launch
uv run agentcore invoke '{"prompt": "what is 40 plus 4?"}'
```

### Option 3: Docker (custom Dockerfile)
If a `Dockerfile` is present on the root directory, it will use it. But, to make sure delete the `Dockerfile` inside `.bedrock_agentcore` created by the configure command. 
```bash
uv run agentcore configure -e my_agent.py
# Edit .bedrock_agentcore.yaml: deployment_type: container
# Create Dockerfile at project root
uv run agentcore launch
uv run agentcore invoke '{"prompt": "what is 40 plus 4?"}'
```

## Test Locally

### Direct Python
```bash
# Run agent
uv run python my_agent.py

# Test in another terminal
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what is 40 plus 4?"}'
```

### With Docker
```bash
docker build -t my-agent .

# need to mount the AWS credentials directory for credentials
docker run -p 8080:8080 \
  -v ~/.aws:/home/agentuser/.aws:ro \
  -e AWS_REGION=us-east-1 \
  my-agent

# Test in another terminal
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what is 40 plus 4?"}'
```

## Agent with Gateway (MCP Server)

This example shows how to use AWS AgentCore Gateway as an MCP Server, combining local tools with remote APIs.

First, ensure `agentcore` build with local environment variables

```
set -a; source .env; set +a; env | grep -E "(GATEWAY_URL|CLIENT_ID|CLIENT_SECRET|USER_POOL_ID)"
```

### Setup Gateway and Target

```bash
# Create Gateway
uv run agentcore gateway create-mcp-gateway

# Create Target from OpenAPI spec (JSONPlaceholder API example)
uv run agentcore gateway create-mcp-gateway-target \
  --gateway-arn arn:aws:bedrock-agentcore:us-west-2:294493538673:gateway/testgatewaycc7a37b4-4eyu2uksng \
  --gateway-url https://testgatewaycc7a37b4-4eyu2uksng.gateway.bedrock-agentcore.us-west-2.amazonaws.com/mcp \
  --role-arn arn:aws:iam::294493538673:role/AgentCoreGatewayExecutionRole \
  --target-type openApiSchema \
  --credentials '{"api_key":"dummy","credential_location":"HEADER","credential_parameter_name":"X-API-Key"}' \
  --target-payload '{"inlinePayload":"{\"openapi\":\"3.0.0\",\"info\":{\"title\":\"JSONPlaceholder API\",\"version\":\"1.0.0\"},\"servers\":[{\"url\":\"https://jsonplaceholder.typicode.com\"}],\"paths\":{\"/users\":{\"get\":{\"operationId\":\"listUsers\",\"summary\":\"List users\",\"responses\":{\"200\":{\"description\":\"Success\"}}}},\"/users/{id}\":{\"get\":{\"operationId\":\"getUser\",\"summary\":\"Get user by ID\",\"parameters\":[{\"name\":\"id\",\"in\":\"path\",\"required\":true,\"schema\":{\"type\":\"integer\"}}],\"responses\":{\"200\":{\"description\":\"Success\"}}}},\"/posts\":{\"get\":{\"operationId\":\"listPosts\",\"summary\":\"List posts\",\"responses\":{\"200\":{\"description\":\"Success\"}}}}}}"}'
```

### Test Locally

```bash
# Run agent
uv run python my_agent_with_gateway.py

# Test in another terminal - calculator
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "what is 40 plus 4?"}'

# Test Gateway tools
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "list all users from the API"}'
```

### Deploy to AWS

```bash
uv run agentcore launch
uv run agentcore invoke '{"prompt": "what is 40 plus 4?"}'
uv run agentcore invoke '{"prompt": "list the users"}'
```

### Known Issues & Solutions

#### ARM64 `ruamel-yaml-clibz`

The `ruamel-yaml-clibz` dependency (from `bedrock-agentcore-starter-toolkit`/`ruamel-yaml`) doesn't have pre-built wheels for ARM64 and fails to compile without build tools.

Need to add build dependencies to Dockerfile

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*
```

This makes `ruamel-yaml-clibz` compile from source during Docker build on ARM64.

Also need to add ECR permissions to execution role for some reason (not needed for the simple agent example)

```bash
aws iam put-role-policy \
  --role-name AmazonBedrockAgentCoreSDKRuntime-us-east-1-06e76c1543 \
  --policy-name ECRAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "*"
    }]
  }'
```

