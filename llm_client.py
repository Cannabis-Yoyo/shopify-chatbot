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

        # Enhanced system identity with clear boundaries
        self.default_system_prompt = (
            "You are Shopify's expert support AI assistant. Your role:\n"
            "- Provide detailed, accurate answers about Shopify services, policies, features, and general e-commerce topics\n"
            "- Use the knowledge base context when provided, but also supplement with your general Shopify knowledge\n"
            "- Give complete, helpful answers - don't just refer users to official documentation\n"
            "- For order tracking, refunds, or order status questions, politely redirect: 'For order-specific actions like tracking or refunds, please use our Order Management tool available in the main menu.'\n"
            "- For completely off-topic questions (weather, sports, etc.), politely redirect to Shopify topics\n"
            "- Be conversational, friendly, and thorough in your responses"
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
        max_tokens: int = 1000,
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
        max_tokens: int = 1000,
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
        max_tokens: int = 1000,
        stream: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate a response using RAG context with enhanced instructions.
        
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
        prompt = f"""You are Shopify's expert support AI. Answer the user's question thoroughly and accurately.

Knowledge Base Context:
{context}

User Question: {query}

Instructions:
- Use the context above as your primary source, but supplement with your general Shopify knowledge
- Provide complete, detailed answers - explain policies, features, and processes clearly
- DO NOT just refer users to "official documentation" or "Shopify's website" - give them the actual answer
- If the question is about order tracking, order status, or processing refunds, respond: "For order-specific actions like tracking details or processing refunds, please use our Order Management tool available in the main menu. I'm here to answer general questions about Shopify policies and services!"
- For off-topic questions (weather, sports, etc.), politely redirect: "I'm here to help with Shopify-related questions. How can I assist you with your store, policies, or services?"
- Be friendly, conversational, and helpful
- Provide actionable information when possible

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
