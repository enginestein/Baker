import re


class ConversationMemory:
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history
        self.entities = {}
        self.last_topic = None

    def add(self, user_input, bot_response, entities=None):
        entry = {'user': user_input, 'bot': bot_response}
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        if entities:
            self.update_entities(entities)
        topic = self._extract_topic(user_input)
        if topic:
            self.last_topic = topic

    def update_entities(self, entities):
        for key, value in entities.items():
            if value:
                self.entities[key] = value

    def _extract_topic(self, text):
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'do', 'does',
                      'did', 'you', 'your', 'me', 'my', 'i', 'we', 'they', 'he',
                      'she', 'it', 'this', 'that', 'these', 'those', 'what', 'when',
                      'where', 'why', 'how', 'who', 'which', 'about', 'tell', 'say',
                      'know', 'think', 'want', 'need', 'can', 'will', 'would', 'could',
                      'should', 'have', 'has', 'had', 'been', 'being', 'be'}
        words = text.lower().split()
        content_words = [w for w in words if w not in stop_words and len(w) > 2]
        if content_words:
            return content_words[0]
        return None

    def get_context(self):
        recent = self.history[-3:] if len(self.history) >= 3 else self.history[:]
        return {
            'history': recent,
            'entities': dict(self.entities),
            'last_topic': self.last_topic,
            'exchange_count': len(self.history),
        }

    def get_last_user_input(self):
        if self.history:
            return self.history[-1]['user']
        return None

    def get_last_bot_response(self):
        if self.history:
            return self.history[-1]['bot']
        return None

    def has_entity(self, entity_type):
        return entity_type in self.entities and bool(self.entities[entity_type])

    def get_entity(self, entity_type):
        return self.entities.get(entity_type)

    def detect_reference(self, text):
        reference_words = {'it', 'that', 'this', 'they', 'them', 'those', 'these', 'he', 'she', 'there'}
        words = set(text.lower().split())
        return bool(words & reference_words)

    def get_conversation_summary(self):
        summary_parts = []
        if self.entities.get('name'):
            summary_parts.append(f"User name: {self.entities['name']}")
        if self.entities.get('age'):
            summary_parts.append(f"User age: {self.entities['age']}")
        topics = set()
        for entry in self.history[-5:]:
            topic = self._extract_topic(entry['user'])
            if topic:
                topics.add(topic)
        if topics:
            summary_parts.append(f"Recent topics: {', '.join(list(topics)[:3])}")
        return ' | '.join(summary_parts) if summary_parts else 'No context yet'

    def clear(self):
        self.history.clear()
        self.entities.clear()
        self.last_topic = None
