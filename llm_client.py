import requests
import json
from typing import Generator, Optional, List, Dict


class GroqClient:
    """Optimized client for interacting with Groq's LLM API (streaming + auto-join)."""

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.session = requests.Session()

        # Concise system identity
        self.default_system_prompt = (
            "You are Shopify's support AI. Be helpful, brief, and friendly. "
            "Answer questions about Shopify services, orders, returns, and policies. "
            "For off-topic questions (like weather), politely redirect to Shopify topics."
        )

    def _post_request(self, messages, temperature: float, max_tokens: int, stream: bool):
        """Helper for making POST requests (streaming or non-streaming)."""
        return self.session.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            },
            stream=stream,
            timeout=15,
        )

    def _build_messages(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build messages list with optional conversation history."""
        messages = []
        
        # Add system prompt
        if system_prompt is None:
            system_prompt = self.default_system_prompt
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        return messages

    def generate_stream(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 120,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """Stream a response (yields chunks)."""
        messages = self._build_messages(user_prompt, system_prompt, conversation_history)

        try:
            with self._post_request(messages, temperature, max_tokens, stream=True) as response:
                if response.status_code != 200:
                    yield f"API Error {response.status_code}: {response.text}"
                    return

                for line in response.iter_lines():
                    if line and line.startswith(b"data: "):
                        chunk = line[len(b"data: ") :].decode("utf-8")
                        if chunk == "[DONE]":
                            break
                        try:
                            delta = json.loads(chunk)
                            content = delta["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
        except Exception as e:
            yield f"Error: {str(e)}"

    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 120,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate a full response (blocking, returns complete string)."""
        messages = self._build_messages(user_prompt, system_prompt, conversation_history)

        try:
            response = self._post_request(messages, temperature, max_tokens, stream=False)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                return f"API Error {response.status_code}: {response.text}"
        except requests.exceptions.Timeout:
            return "Request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def generate_with_context(
        self,
        query: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 150,
        stream: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate a response using RAG context. Always returns a complete string.
        
        Args:
            query: User's question
            context: Retrieved context from knowledge base
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length
            stream: If True, streams internally then joins; if False, uses non-streaming API
            conversation_history: Optional conversation history for context
        
        Returns:
            Complete response string (never a generator)
        """
        prompt = f"""You are Shopify's support AI. Answer concisely and helpfully.

Context from knowledge base:
{context}

User: {query}

Instructions:
- Use the context above to answer accurately
- Keep responses brief (2-3 sentences max unless detail needed)
- For off-topic questions, politely redirect: "I'm here to help with Shopify-related questions. How can I assist you with your store or order?"
- Be friendly but efficient

Answer:"""

        if stream:
            return "".join(self.generate_stream(
                prompt, 
                temperature=temperature, 
                max_tokens=max_tokens,
                conversation_history=conversation_history
            ))
        else:
            return self.generate(
                prompt, 
                temperature=temperature, 
                max_tokens=max_tokens,
                conversation_history=conversation_history
            )