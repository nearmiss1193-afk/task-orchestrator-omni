
import os
import json
import glob

class Librarian:
    """
    The 'Librarian' manages Long-Term Memory (The Archive).
    It stores vast amounts of knowledge in JSON files and retrieves ONLY what is needed.
    This prevents 'Model Overload' by keeping the active Context Window small.
    """
    
    def __init__(self):
        self.memory_path = os.path.join(os.path.dirname(__file__), "archive")
        if not os.path.exists(self.memory_path):
            os.makedirs(self.memory_path)
            
    def store_knowledge(self, topic, content, source="User"):
        """Saves knowledge to The Archive (Does not consume RAM/Context)"""
        filename = f"{topic.lower().replace(' ', '_')}.json"
        path = os.path.join(self.memory_path, filename)
        
        entry = {
            "topic": topic,
            "content": content,
            "source": source,
            "timestamp": os.environ.get('DATE', 'Unknown')
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
            
        return f"✅ Saved '{topic}' to The Archive."

    def retrieve_knowledge(self, query):
        """Searches The Archive for relevant info (Simple Keyword Match)"""
        results = []
        query = query.lower()
        
        # Scan all memories (In production, use a Vector DB like Chroma/Pinecone)
        files = glob.glob(os.path.join(self.memory_path, "*.json"))
        
        for path in files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Check if query matches topic or content
                    if query in data['topic'].lower() or query in str(data['content']).lower():
                        results.append(data)
            except:
                continue
                
        if not results:
            return f"🤷 The Archive has no records for '{query}'."
            
        return results

if __name__ == "__main__":
    lib = Librarian()
    # Test Storage
    lib.store_knowledge("HVAC Pricing", "Standard service call is $99. Emergency is $149.", "SOP Manual")
    # Test Retrieval
    print(lib.retrieve_knowledge("Pricing"))
