import httpx
from typing import Dict, Any
from app.core.config import settings
from app.core.logging_config import logger

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def check_health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    models_data = response.json().get("models", [])
                    model_names = [m.get("name") for m in models_data]
                    model_found = any(self.model in name for name in model_names)
                    return {
                        "available": True,
                        "model_found": model_found,
                        "available_models": model_names
                    }
                return {"available": False, "model_found": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            return {"available": False, "model_found": False, "error": str(e)}

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic, grounded QA
                "top_p": 0.9
            }
        }

        logger.info(f"Sending request to Ollama model '{self.model}' at {url}...")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    error_msg = f"Ollama HTTP error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                data = response.json()
                answer = data.get("response", "").strip()
                logger.info("Received response from Ollama successfully.")
                return answer
        except httpx.ConnectError:
            msg = f"Could not connect to Ollama service at {self.base_url}. Please ensure Ollama is running (`ollama serve`)."
            logger.error(msg)
            raise RuntimeError(msg)
        except httpx.TimeoutException:
            msg = f"Ollama generation request timed out after 60 seconds."
            logger.error(msg)
            raise RuntimeError(msg)
        except Exception as e:
            logger.error(f"Error during Ollama generation: {str(e)}")
            raise RuntimeError(f"Ollama generation error: {str(e)}")
