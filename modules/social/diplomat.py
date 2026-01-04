
import os
import sys

# Connect to the Brain (Librarian)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knowledge.librarian import Librarian

class Diplomat:
    """
    The Diplomat: Omni-Channel Social Manager.
    "Sovereignty Through Automation"
    
    Capabilities:
    1.  Ingests Webhooks from Instagram/FB/YouTube.
    2.  Uses 'Librarian' to find the correct answer.
    3.  Auto-Drafts replies (Human Review or Auto-Send).
    """

    def __init__(self):
        print("🕊️ Initializing The Diplomat (Social Omni-Channel)...")
        self.memory = Librarian()
        self.pending_replies = []

    def handle_inbound(self, platform, user, message):
        print(f"   📨 [Incoming {platform}] from {user}: '{message}'")
        
        # 1. Consult The Archive (RAG)
        context = self.memory.retrieve_knowledge(message)
        
        # 2. Formulate Reply (Simulation)
        # In prod, this calls LLM with the context found above.
        reply = self._generate_response(user, message, context)
        
        # 3. Queue or Send
        self.pending_replies.append({
            "platform": platform,
            "to": user,
            "reply": reply,
            "status": "DRAFT"
        })
        
        return reply

    def _generate_response(self, user, message, context):
        """Simulates LLM Thinking using RAG Context"""
        if "pricing" in message.lower():
            # The Librarian found pricing info
            return f"Hey {user}! Thanks for asking. {context[0] if context else 'Our standard rate is $99/mo.'} link: aiserviceco.com/pricing"
        elif "hate" in message.lower() or "sucks" in message.lower():
            return f"Hey {user}, sorry to hear that. Fixing it specifically for you."
        else:
            return f"Thanks for the comment, {user}! (Auto-Reply)"

    def flush_queue(self):
        print("\n🚀 FLUSHING DIPLOMAT QUEUE (Posting Replies)...")
        for item in self.pending_replies:
            print(f"   ✅ [POST {item['platform']}] @{item['to']}: \"{item['reply']}\"")
        self.pending_replies = []

if __name__ == "__main__":
    d = Diplomat()
    # Test Interaction
    d.handle_inbound("Instagram", "cool_guy_123", "How much is the pricing?")
    d.handle_inbound("YouTube", "hater_x", "Your service sucks")
    
    d.flush_queue()
