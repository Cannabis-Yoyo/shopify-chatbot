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

    def _is_order_action_request(self, text: str) -> bool:
        """
        Detect if user wants to PERFORM an order action (not just ask about policies).
        Returns True only for actual order lookup/tracking/refund requests.
        """
        text_lower = text.lower()
        
        # Action phrases that indicate wanting to DO something with an order
        action_phrases = [
            "track my order",
            "where is my order",
            "check my order",
            "order status",
            "my order #",
            "order number",
            "process refund",
            "get refund",
            "request refund",
            "cancel my order",
            "cancel order",
            "view my order",
            "look up order",
            "find my order"
        ]
        
        # Check if any action phrase is present
        if any(phrase in text_lower for phrase in action_phrases):
            return True
        
        # Check if they mentioned a specific order ID (indicates they want to check it)
        if re.search(r'order\s*#?\d+', text_lower) or re.search(r'#\d{4,}', text_lower):
            return True
        
        return False

    def chat(self, user_input: str) -> str:
        # Input validation
        if user_input is None:
            return "I didn't receive your message. Please try again."
        
        user_input = user_input.strip()
        if not user_input:
            return "Please enter a message."
        
        # Add user message to context
        self.context.add_message("user", user_input)
        
        # Check if this is an order ACTION request (not just a policy question)
        if self._is_order_action_request(user_input):
            response = (
                "For order tracking, status checks, and refund requests, "
                "please use the **Order Management** tool available in the main menu. "
                "It will help you view your order details and process refunds efficiently."
            )
            self.context.add_message("assistant", response)
            return response

        # Search knowledge base (for policy questions, terms, etc.)
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
