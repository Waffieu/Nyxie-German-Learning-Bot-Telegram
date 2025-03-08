import json
import os
import numpy as np
import faiss
from datetime import datetime
import time
from config import CHAT_HISTORY_DIR, VECTOR_STORE_DIR, EMBEDDING_DIM

class ChatMemory:
    def __init__(self, user_id, groq_client):
        self.user_id = str(user_id)
        self.groq_client = groq_client
        self.json_file = os.path.join(CHAT_HISTORY_DIR, f"{self.user_id}.json")
        self.faiss_index_file = os.path.join(VECTOR_STORE_DIR, f"{self.user_id}.index")
        
        # Initialize chat history
        self.chat_history = self._load_chat_history()
        
        # Initialize FAISS index
        self.index, self.messages = self._load_or_create_index()
        
    def _load_chat_history(self):
        """Load chat history from JSON file or create a new one."""
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def _save_chat_history(self):
        """Save chat history to JSON file."""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            
    def _get_embedding(self, text):
        """Get embedding for text using Groq."""
        try:
            # Simplified for demonstration - using random embeddings
            # In production, use a proper embedding model API
            embedding = np.random.rand(EMBEDDING_DIM).astype('float32')
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return np.random.rand(EMBEDDING_DIM).astype('float32')
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one."""
        if os.path.exists(self.faiss_index_file):
            index = faiss.read_index(self.faiss_index_file)
            messages = self._load_stored_messages()
            return index, messages
            
        # Create a new index
        index = faiss.IndexFlatL2(EMBEDDING_DIM)
        return index, []
        
    def _load_stored_messages(self):
        """Load stored messages associated with the FAISS index."""
        messages_file = self.faiss_index_file + ".messages.json"
        if os.path.exists(messages_file):
            with open(messages_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def _save_stored_messages(self):
        """Save messages associated with the FAISS index."""
        messages_file = self.faiss_index_file + ".messages.json"
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
            
    def add_message(self, role, content):
        """Add a message to the chat history and update the FAISS index."""
        # Create message record
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to chat history
        self.chat_history.append(message)
        self._save_chat_history()
        
        # Add to FAISS index
        text_to_embed = f"{role}: {content}"
        embedding = self._get_embedding(text_to_embed)
        
        # Add to index
        faiss.normalize_L2(embedding.reshape(1, -1))
        self.index.add(embedding.reshape(1, -1))
        
        # Store message text
        self.messages.append(text_to_embed)
        
        # Save index and messages
        faiss.write_index(self.index, self.faiss_index_file)
        self._save_stored_messages()
        
    def get_relevant_history(self, query, k=25):
        """Retrieve relevant messages from history based on query."""
        # Updated default to 25 messages for better context tracking
        query_embedding = self._get_embedding(query)
        faiss.normalize_L2(query_embedding.reshape(1, -1))
        
        if self.index.ntotal == 0:  # If index is empty
            return []
            
        distances, indices = self.index.search(query_embedding.reshape(1, -1), min(k, self.index.ntotal))
        
        # Add the distance score for better sorting/filtering
        relevant_messages = [(self.messages[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
        
        # Sort by relevance (lower distance is more relevant)
        relevant_messages.sort(key=lambda x: x[1])
        
        # Return just the messages
        return [msg for msg, _ in relevant_messages]
        
    def get_context_for_model(self, query, max_messages=25):
        """Build context for the model using relevant history."""
        # Default increased to 25 messages
        # Get the most relevant messages using FAISS
        relevant_history = self.get_relevant_history(query, k=max_messages)
        
        # Format the context in a more structured way for the model
        if not relevant_history:
            return "No previous conversation history available."
            
        context = "Here are the most relevant previous exchanges from this conversation:\n\n"
        for i, msg in enumerate(relevant_history, 1):
            context += f"{i}. {msg}\n"
        
        context += "\nUse this relevant context to provide a coherent and informed response to the user's current query."
        return context
        
    def get_full_history(self, max_messages=10):
        """Get the most recent messages from chat history."""
        return self.chat_history[-max_messages:] if self.chat_history else []
