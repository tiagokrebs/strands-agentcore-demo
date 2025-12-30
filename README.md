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
