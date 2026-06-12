from baker.trainer import Trainer
from baker.bparser import Parser
from baker.memory import ConversationMemory


class Chatbot:
    def __init__(self, name, data_file=None, backend='tfidf', memory=True,
                 threshold=0.3, model_name=None, intent_threshold=0.3):
        self.name = name
        self.backend = backend
        self.threshold = threshold
        if data_file:
            self._data = Trainer(
                data_file,
                backend=backend,
                threshold=threshold,
                model_name=model_name,
            )
            self.parser = self._data
            self.trainer = self._data
        else:
            self._data = None
            self.parser = None
            self.trainer = None
        self.memory = ConversationMemory() if memory else None

    def add_intent(self, name, examples, responses, negative_examples=None):
        if not self.parser:
            raise RuntimeError("Initialize with a data file before adding intents.")
        self.parser.add_intent(name, examples, responses, negative_examples)

    def remove_intent(self, name):
        if self.parser:
            self.parser.remove_intent(name)

    def list_intents(self):
        if self.parser:
            return self.parser.list_intents()
        return []

    def respond(self, text):
        if not self.parser:
            return "Please initialize with a data file to respond."
        context = self.memory.get_context() if self.memory else None
        entities = self.parser.entity_extractor.extract(text)
        response = self.parser.get_response(text, context=context)
        if self.memory:
            self.memory.add(text, response, entities=entities)
        return response

    def respond_detailed(self, text):
        if not self.parser:
            return None
        context = self.memory.get_context() if self.memory else None
        entities = self.parser.entity_extractor.extract(text)
        sentiment = self.parser.sentiment_analyzer.analyze(text)
        response, confidence = self.parser.get_response(text, context=context, return_confidence=True)
        matched_key, _ = self.parser.matcher.best_match(text)
        if self.memory:
            self.memory.add(text, response, entities=entities)
        return {
            'response': response,
            'confidence': confidence,
            'matched_key': matched_key,
            'sentiment': sentiment,
            'entities': entities,
            'backend': self.backend,
            'intents': self.parser.list_intents(),
        }

    def train(self, question, response):
        if not self.trainer:
            return False
        self.trainer.train_response(question, response)
        return True

    def train_many(self, pairs):
        if not self.trainer:
            return False
        self.trainer.train_many(pairs)
        return True

    def session(self, trainer=None, parser=None):
        actual_trainer = trainer or self.trainer
        actual_parser = parser or self.parser
        if not actual_parser:
            print("Error: No data file loaded.")
            return
        print(f"Welcome to {self.name} Chatbot! (backend: {self.backend})")
        print("Type 'exit' to quit, 'teach' to train me.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Session ended.")
                break
            if user_input.lower() == "teach":
                self._teach_mode(actual_trainer or actual_parser)
                continue
            context = self.memory.get_context() if self.memory else None
            response = actual_parser.get_response(user_input, context=context)
            if self.memory:
                entities = actual_parser.entity_extractor.extract(user_input)
                self.memory.add(user_input, response, entities=entities)
            print("Bot:", response)

    def _teach_mode(self, trainer_obj):
        print("Teach me! Use: question | response")
        while True:
            line = input("Teach: ")
            if line.lower() == 'done':
                break
            if '|' in line:
                parts = line.split('|', 1)
                question, response = parts[0].strip(), parts[1].strip()
                if question and response:
                    trainer_obj.train_response(question, response)
                    print(f"  Learned: '{question}'")
                else:
                    print("  Use: question | response")
            else:
                print("  Use '|' to separate question and response")

    def get_context(self):
        if self.memory:
            return self.memory.get_context()
        return {}

    def get_last_response(self):
        if self.memory:
            return self.memory.get_last_bot_response()
        return None
