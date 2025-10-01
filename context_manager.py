from typing import List, Dict, Optional
from datetime import datetime
import json


class ConversationContext:
    """Manages conversation context with sliding window and summarization."""
    
    def __init__(self, max_history: int = 10, max_tokens_per_msg: int = 200):
        """
        Args:
            max_history: Maximum number of message pairs to keep in full detail
            max_tokens_per_msg: Approximate token limit per message (rough estimate: 1 token ≈ 4 chars)
        """
        self.max_history = max_history
        self.max_tokens_per_msg = max_tokens_per_msg
        self.messages: List[Dict[str, str]] = []
        self.summary: Optional[str] = None
        self.metadata: Dict = {
            "created_at": datetime.now().isoformat(),
            "total_messages": 0
        }
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.metadata["total_messages"] += 1
        
        # Trim if exceeds max history
        if len(self.messages) > self.max_history * 2:  # *2 for user+assistant pairs
            self._compress_history()
    
    def _compress_history(self):
        """Compress old messages into a summary, keep recent ones."""
        # Keep last max_history pairs (user + assistant)
        messages_to_keep = self.messages[-(self.max_history * 2):]
        messages_to_compress = self.messages[:-(self.max_history * 2)]
        
        if messages_to_compress:
            # Create simple summary of older messages
            summary_parts = []
            for msg in messages_to_compress:
                role = msg["role"]
                content = msg["content"][:100]  # First 100 chars
                summary_parts.append(f"{role}: {content}...")
            
            self.summary = "Previous conversation:\n" + "\n".join(summary_parts[-6:])  # Last 6 old messages
        
        self.messages = messages_to_keep
    
    def get_context_for_llm(self, include_summary: bool = True) -> List[Dict[str, str]]:
        """
        Get formatted context for LLM with optional summary.
        Returns list of message dicts suitable for API calls.
        """
        context = []
        
        # Add summary of old messages if exists
        if include_summary and self.summary:
            context.append({
                "role": "system",
                "content": self.summary
            })
        
        # Add recent messages (already trimmed)
        for msg in self.messages:
            context.append({
                "role": msg["role"],
                "content": self._truncate_message(msg["content"])
            })
        
        return context
    
    def _truncate_message(self, content: str) -> str:
        """Truncate message if too long (rough token estimation)."""
        max_chars = self.max_tokens_per_msg * 4  # ~4 chars per token
        if len(content) > max_chars:
            return content[:max_chars] + "... [truncated]"
        return content
    
    def get_recent_messages(self, n: int = 5) -> List[Dict[str, str]]:
        """Get last N messages for display purposes."""
        return self.messages[-n:]
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []
        self.summary = None
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "total_messages": 0
        }
    
    def to_dict(self) -> Dict:
        """Serialize context to dictionary."""
        return {
            "messages": self.messages,
            "summary": self.summary,
            "metadata": self.metadata
        }
    
    def from_dict(self, data: Dict):
        """Load context from dictionary."""
        self.messages = data.get("messages", [])
        self.summary = data.get("summary")
        self.metadata = data.get("metadata", {
            "created_at": datetime.now().isoformat(),
            "total_messages": len(self.messages)
        })
    
    def get_conversation_stats(self) -> Dict:
        """Get statistics about the conversation."""
        return {
            "total_messages": self.metadata["total_messages"],
            "messages_in_memory": len(self.messages),
            "has_summary": self.summary is not None,
            "created_at": self.metadata["created_at"]
        }