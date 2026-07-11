# vLLM Setup for CIP

## Option 1: vLLM (Production - requires GPU)

### Prerequisites
- NVIDIA GPU with at least 24GB VRAM (for Qwen3-32B)
- CUDA 12.1+
- Python 3.10+

### Installation
```bash
pip install vllm
```

### Start vLLM Server
```bash
# For Qwen3-32B (requires ~24GB VRAM)
vllm serve Qwen/Qwen3-32B --port 8000 --api-key no-key

# For smaller model (requires ~8GB VRAM)
vllm serve Qwen/Qwen3-8B --port 8000 --api-key no-key
```

## Option 2: Ollama (Local Dev - CPU/GPU)

### Installation
```bash
# Windows: Download from https://ollama.com/download
# Or use winget:
winget install Ollama.Ollama
```

### Start Ollama
```bash
ollama serve
```

### Pull Model
```bash
# For Qwen3 (smaller quantized version)
ollama pull qwen3:8b

# Or use a different model
ollama pull llama3.2:3b
```

### Configure CIP
Update `.env`:
```
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen3:8b
```

## Option 3: OpenAI API (Cloud)

### Configuration
Update `.env`:
```
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o
```

## Testing the LLM Connection

Run this script to verify the LLM is working:

```python
import asyncio
import httpx

async def test_llm():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "qwen3-32b",
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "max_tokens": 100,
            },
        )
        print(response.json())

asyncio.run(test_llm())
```
