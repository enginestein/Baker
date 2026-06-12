import json
import random
import os
import yaml
import xml.etree.ElementTree as ET

from baker.nlp import (
    Matcher, SemanticMatcher, EntityExtractor, SentimentAnalyzer, TextProcessor,
    IntentClassifier, ResponseSelector, TemplateEngine,
)


TEMPLATE_FALLBACKS = {
    'name': 'there',
    'last_topic': 'that',
    'sentiment': '',
}


class Parser:
    def __init__(self, response_file_name, backend='tfidf', threshold=0.3, model_name=None,
                 intent_threshold=0.3):
        self.file_path = response_file_name
        self.backend_name = backend
        self.responses = self.load_responses(self.file_path)
        self._rebuild_key_map()
        self.processor = TextProcessor()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.intent_classifier = IntentClassifier(threshold=intent_threshold)
        self.response_selector = ResponseSelector()
        self.template_engine = TemplateEngine()
        self._init_matcher(backend, threshold, model_name)

    def _init_matcher(self, backend, threshold, model_name):
        keys = list(self.responses.keys())
        if backend == 'semantic':
            try:
                self.matcher = SemanticMatcher(
                    model_name=model_name or 'all-MiniLM-L6-v2',
                    threshold=threshold
                )
                if keys:
                    self.matcher.fit(keys)
            except ImportError:
                self.matcher = Matcher(threshold=threshold)
                if keys:
                    self.matcher.fit(keys)
                self.backend_name = 'tfidf (semantic unavailable)'
        else:
            self.matcher = Matcher(threshold=threshold)
            if keys:
                self.matcher.fit(keys)

    def add_intent(self, name, examples, responses, negative_examples=None):
        self.intent_classifier.add_intent(name, examples, responses, negative_examples)

    def remove_intent(self, name):
        self.intent_classifier.remove_intent(name)

    def list_intents(self):
        return self.intent_classifier.intents_list()

    def load_responses(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        with open(file_path, 'r') as file:
            if file_extension == '.json':
                responses = json.load(file)
            elif file_extension in ('.yaml', '.yml'):
                responses = yaml.safe_load(file)
            elif file_extension == '.xml':
                root = ET.parse(file).getroot()
                responses = {}
                for item in root:
                    key = item.tag
                    value = [child.text for child in item]
                    responses[key] = value
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        return responses or {}

    def save_responses(self):
        _, file_extension = os.path.splitext(self.file_path)
        with open(self.file_path, 'w') as file:
            if file_extension == '.json':
                json.dump(self.responses, file, indent=4)
            elif file_extension in ('.yaml', '.yml'):
                yaml.dump(self.responses, file, default_flow_style=False)
            elif file_extension == '.xml':
                root = ET.Element('responses')
                for key, values in self.responses.items():
                    item = ET.SubElement(root, key)
                    for value in values:
                        ET.SubElement(item, 'response').text = value
                tree = ET.ElementTree(root)
                tree.write(file, encoding="utf-8", xml_declaration=True)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

    def _rebuild_key_map(self):
        proc = TextProcessor()
        self._key_map = {proc.normalize(k): k for k in self.responses}

    def train_response(self, user_input, new_response):
        normalized = self.processor.normalize(user_input)
        is_new = normalized not in self._key_map
        if not is_new:
            original_key = self._key_map[normalized]
            self.responses[original_key].append(new_response)
        else:
            self.responses[user_input] = [new_response]
            self._key_map[normalized] = user_input
            self.matcher.add_key(user_input)
        self.save_responses()

    def get_response(self, user_input, context=None, return_confidence=False):
        if not self.responses and not self.intent_classifier._examples:
            msg = "I don't have any training data yet. Teach me something!"
            return (msg, 0.0) if return_confidence else msg

        entities = self.entity_extractor.extract(user_input)
        sentiment = self.sentiment_analyzer.analyze(user_input)

        template_ctx = dict(context or {})
        template_ctx['sentiment'] = sentiment
        for k, v in entities.items():
            template_ctx[k] = v

        normalized = self.processor.normalize(user_input)

        if normalized in self._key_map:
            original_key = self._key_map[normalized]
            raw = self._select_response(self.responses[original_key], entities)
            rendered = self._render_template(raw, template_ctx)
            return (rendered, 1.0) if return_confidence else rendered

        matched_key, confidence = self.matcher.best_match(user_input)
        if matched_key:
            raw = self._select_response(self.responses[matched_key], entities)
            rendered = self._render_template(raw, template_ctx)
            return (rendered, confidence) if return_confidence else rendered

        intent_name, intent_conf = self.intent_classifier.classify(user_input)
        if intent_name:
            responses = self.intent_classifier.get_responses(intent_name)
            raw = self._select_response(responses, entities)
            template_ctx['intent'] = intent_name
            rendered = self._render_template(raw, template_ctx)
            return (rendered, intent_conf) if return_confidence else rendered

        response = self._generate_fallback(user_input, sentiment)
        if return_confidence:
            return response, 0.0
        return response

    def _select_response(self, responses, entities=None):
        return self.response_selector.select(responses, entities=entities)

    def _render_template(self, text, context):
        ctx = dict(context)
        for key, fallback in TEMPLATE_FALLBACKS.items():
            if key not in ctx or not ctx[key]:
                ctx[key] = fallback
        return self.template_engine.render(text, ctx)

    def _generate_fallback(self, text, sentiment=None):
        if sentiment is None:
            sentiment = self.sentiment_analyzer.analyze(text)
        if sentiment == 'positive':
            return random.choice([
                "That's great to hear!",
                "Awesome! I'm glad things are going well.",
                "Wonderful! Thanks for sharing.",
                "That makes me happy too!",
            ])
        elif sentiment == 'negative':
            return random.choice([
                "I'm sorry to hear that.",
                "That's too bad. I hope things get better.",
                "Sorry you feel that way. I'm here if you need to talk.",
            ])
        if '?' in text:
            return random.choice([
                "I'm not sure about that yet. You can teach me using train()!",
                "Good question! I haven't learned about that yet.",
                "Hmm, I don't know. What would you like the answer to be?",
                "I'm still learning. Could you help me out?",
            ])
        return random.choice([
            "I'm not sure how to respond to that. Could you rephrase?",
            "Interesting! Tell me more.",
            "I see. Go on...",
            "Thanks for sharing! I'm still learning.",
        ])

    def remove_response(self, user_input, response):
        normalized = self.processor.normalize(user_input)
        if normalized in self._key_map:
            key = self._key_map[normalized]
            if response in self.responses[key]:
                self.responses[key].remove(response)
                if not self.responses[key]:
                    del self.responses[key]
                    del self._key_map[normalized]
                    self.matcher.remove_key(key)
                self.save_responses()

    def list_key_questions(self):
        return list(self.responses.keys())

    def count_responses(self, user_input):
        normalized = self.processor.normalize(user_input)
        if normalized in self._key_map:
            key = self._key_map[normalized]
            return len(self.responses[key])
        return 0

    def reset_responses(self, user_input):
        normalized = self.processor.normalize(user_input)
        if normalized in self._key_map:
            key = self._key_map[normalized]
            del self.responses[key]
            del self._key_map[normalized]
            self.matcher.remove_key(key)
            self.save_responses()

    def export_responses(self, export_file_name):
        export_extension = os.path.splitext(export_file_name)[1]
        with open(export_file_name, 'w') as export_file:
            if export_extension == '.json':
                json.dump(self.responses, export_file, indent=4)
            elif export_extension in ('.yaml', '.yml'):
                yaml.dump(self.responses, export_file, default_flow_style=False)
            elif export_extension == '.xml':
                root = ET.Element('responses')
                for key, values in self.responses.items():
                    item = ET.SubElement(root, key)
                    for value in values:
                        ET.SubElement(item, 'response').text = value
                tree = ET.ElementTree(root)
                tree.write(export_file, encoding="utf-8", xml_declaration=True)
            else:
                raise ValueError(f"Unsupported export file format: {file_extension}")
