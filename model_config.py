import os
from dotenv import load_dotenv

load_dotenv()

def load_model(provider: str):
    """
    Returns a Strands-compatible model based on selected provider.
    Swap provider string and everything else stays the same.
    """

    if provider == "Ollama (Local)":
        from strands.models.ollama import OllamaModel
        return OllamaModel(
            model_id="qwen2.5:7b",
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            params={
                "temperature": 0.2,
                "num_ctx": 16384,
            }
        )

    elif provider == "Anthropic API":
        from strands.models import AnthropicModel
        return AnthropicModel(
            model_id="claude-3-5-haiku-20241022",  # fast + cheap
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            params={
                "temperature": 0.2,
                "max_tokens": 4096,
            }
        )

    elif provider == "AWS Bedrock":
        from strands.models.bedrock import BedrockModel
        return BedrockModel(
            model_id="anthropic.claude-3-5-haiku-20241022-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            params={
                "temperature": 0.2,
                "max_tokens": 4096,
            }
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")