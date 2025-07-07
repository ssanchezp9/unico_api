import uuid

class ConversationManager:
    def __init__(self):
        self.conversations = {}

    def get_history(self, conversation_id):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        return self.conversations[conversation_id]

    def add_message(self, conversation_id, role, content):
        history = self.get_history(conversation_id)
        history.append({"role": role, "content": content})
