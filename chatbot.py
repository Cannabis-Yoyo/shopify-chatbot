import re
from typing import Optional

from knowledge_base import RAGKnowledgeBase
from order_manager import OrderManager
from llm_client import GroqClient
from context_manager import ConversationContext


class Chatbot:
    def __init__(self, groq_key: str, pdf_folder: str = "pdfs/", data_folder: str = "data/"):
        print("\nInitializing Chatbot...")
        
        self.kb = RAGKnowledgeBase()
        self.orders = OrderManager(data_folder)
        self.llm = GroqClient(groq_key)
        self.context = ConversationContext(max_history=10)  # Keep last 10 exchanges
        
        self._load_pdfs(pdf_folder)
        
        print("Chatbot initialized successfully!\n")

    def _load_pdfs(self, pdf_folder: str):
        pdf_mapping = {
            "shopify-privacy policy.pdf": "Privacy Policy",
            "shopify-terms of services.pdf": "Terms of Service"
        }
        self.kb.load_pdf_folder(pdf_folder, pdf_mapping)

    def _extract_order_id(self, text: str) -> Optional[str]:
        patterns = [
            r'order\s*#?(\d+)',   # "order #1234" or "order 1234"
            r'#(\d+)',            # "#1234"
            r'\b(\d{4,})\b'       # Any 4+ digit number
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def chat(self, user_input: str) -> str:
        # Input validation
        if user_input is None:
            return "I didn't receive your message. Please try again."
        
        user_input = user_input.strip()
        if not user_input:
            return "Please enter a message."
        
        # Add user message to context
        self.context.add_message("user", user_input)
        
        user_input_lower = user_input.lower()
        
        # Check for order-related queries - redirect to Order Management tool
        if any(keyword in user_input_lower for keyword in ["order", "track", "status", "refund", "cancel"]):
            # Check if they're asking about order details/tracking/refund
            order_keywords = ["track", "status", "where is my", "refund", "cancel", "return"]
            if any(kw in user_input_lower for kw in order_keywords):
                response = (
                    "For order tracking, status checks, and refund requests, "
                    "please use the **Order Management** tool available in the main menu. "
                    "It will help you view your order details and process refunds efficiently."
                )
                self.context.add_message("assistant", response)
                return response

        # Search knowledge base
        results = self.kb.search(user_input)
        if results:
            context_kb = "\n".join([chunk.content for chunk, _ in results])
            # Pass conversation context to LLM
            response = self.llm.generate_with_context(
                user_input, 
                context_kb, 
                conversation_history=self.context.get_context_for_llm()
            )
            self.context.add_message("assistant", response)
            return response

        # Fallback to general response with context
        response = self.llm.generate(
            user_input,
            conversation_history=self.context.get_context_for_llm()
        )
        self.context.add_message("assistant", response)
        return response
    
    def clear_context(self):
        """Clear conversation context."""
        self.context.clear()
    
    def get_context_stats(self):
        """Get conversation statistics."""
        return self.context.get_conversation_stats()
    
    def export_context(self) -> dict:
        """Export conversation context."""
        return self.context.to_dict()
    
    def import_context(self, context_data: dict):
        """Import conversation context."""
        self.context.from_dict(context_data)
