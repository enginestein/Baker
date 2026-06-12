import os
import unittest
import tempfile
import json
import uuid

from baker import Parser, Chatbot
from baker.nlp import IntentClassifier, ResponseSelector, TemplateEngine, EntityExtractor


def _unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestIntentClassifier(unittest.TestCase):
    def setUp(self):
        self.ic = IntentClassifier(threshold=0.2)

    def test_classify_exact_match(self):
        self.ic.add_intent("greeting", ["Hello", "Hi", "Hey"], ["Hello!", "Hi there!"])
        self.ic.add_intent("farewell", ["Bye", "Goodbye"], ["See you!"])
        intent, conf = self.ic.classify("Hello")
        self.assertEqual(intent, "greeting")
        self.assertGreaterEqual(conf, 0.2)

    def test_classify_similar(self):
        self.ic.add_intent("greeting", ["Good morning", "Hello there"], ["Morning!"])
        self.ic.add_intent("farewell", ["See you later", "Goodbye"], ["Bye!"])
        intent, conf = self.ic.classify("good morning")
        self.assertEqual(intent, "greeting")

    def test_classify_unknown(self):
        self.ic.add_intent("greeting", ["Hello"], ["Hi"])
        intent, conf = self.ic.classify("quantum physics")
        self.assertIsNone(intent)

    def test_multiple_examples_per_intent(self):
        self.ic.add_intent("greeting", ["Hello", "Hi", "Hey", "Good day"], ["Hi!"])
        self.ic.add_intent("farewell", ["Bye", "Goodbye", "See ya"], ["Bye!"])
        for text in ["Hello", "Hi", "Hey", "Good day"]:
            intent, conf = self.ic.classify(text)
            self.assertEqual(intent, "greeting", f"Failed for '{text}'")

    def test_remove_intent(self):
        self.ic.add_intent("greeting", ["Hello"], ["Hi"])
        self.ic.add_intent("farewell", ["Bye"], ["Bye"])
        self.ic.remove_intent("greeting")
        self.assertNotIn("greeting", self.ic.intents_list())

    def test_get_responses(self):
        self.ic.add_intent("greeting", ["Hello"], ["Hi", "Hello", "Hey"])
        self.assertEqual(len(self.ic.get_responses("greeting")), 3)

    def test_empty_classifier(self):
        intent, conf = self.ic.classify("Hello")
        self.assertIsNone(intent)
        self.assertEqual(conf, 0.0)


class TestResponseSelector(unittest.TestCase):
    def setUp(self):
        self.rs = ResponseSelector(recency_penalty=0.5, diversity_window=3)

    def test_select_basic(self):
        result = self.rs.select(["a", "b", "c"])
        self.assertIn(result, ["a", "b", "c"])

    def test_avoids_repetition(self):
        results = []
        for _ in range(6):
            results.append(self.rs.select(["a", "b"]))
        self.assertTrue(len(set(results)) > 1)

    def test_reset(self):
        self.rs.select(["a", "b"])
        self.rs.reset()
        self.assertEqual(len(self.rs._recent), 0)

    def test_single_response(self):
        result = self.rs.select(["only choice"])
        self.assertEqual(result, "only choice")

    def test_entity_bonus(self):
        result = self.rs.select(["Hello John", "Hi there"], entities={"name": "John"})
        self.assertEqual(result, "Hello John")

    def test_none_for_empty(self):
        result = self.rs.select([], entities={})
        self.assertIsNone(result)


class TestTemplateEngine(unittest.TestCase):
    def setUp(self):
        self.te = TemplateEngine()

    def test_no_template(self):
        result = self.te.render("Hello there!", {"name": "Bob"})
        self.assertEqual(result, "Hello there!")

    def test_basic_substitution(self):
        result = self.te.render("Hello {name}!", {"name": "Bob"})
        self.assertEqual(result, "Hello Bob!")

    def test_multiple_variables(self):
        result = self.te.render("{greeting} {name}!", {"greeting": "Hi", "name": "Alice"})
        self.assertEqual(result, "Hi Alice!")

    def test_unknown_variable(self):
        result = self.te.render("Hello {unknown}!", {"name": "Bob"})
        self.assertEqual(result, "Hello {unknown}!")

    def test_empty_context(self):
        result = self.te.render("Hello {name}!", {})
        self.assertEqual(result, "Hello {name}!")

    def test_numeric_value(self):
        result = self.te.render("You are {age} years old.", {"age": 30})
        self.assertEqual(result, "You are 30 years old.")

    def test_list_value(self):
        result = self.te.render("Your numbers: {nums}", {"nums": [1, 2, 3]})
        self.assertEqual(result, "Your numbers: 1")


class TestBotWithIntents(unittest.TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.script_dir, 'data.json')

    def test_bot_add_intent(self):
        bot = Chatbot("TestBot", data_file=self.data_file)
        bot.add_intent("greeting", ["Hello", "Hi", "Hey"], ["Greetings!", "Hello there!"])
        self.assertIn("greeting", bot.list_intents())

    def test_bot_responds_via_intent(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            tmp = f.name
        try:
            bot = Chatbot("TestBot", data_file=tmp, threshold=0.1)
            bot.add_intent("greeting", ["greetings", "salutations"], ["Hey there!"])
            response = bot.respond("greetings and salutations")
            self.assertEqual(response, "Hey there!")
        finally:
            os.unlink(tmp)

    def test_bot_responds_via_key_before_intent(self):
        bot = Chatbot("TestBot", data_file=self.data_file)
        bot.add_intent("greeting", ["Hello"], ["Greetings!"])
        response = bot.respond("Hello")
        self.assertIn(response, ["Hi", "Hello", "Hey mister, how are you?"])

    def test_intent_with_templates(self):
        bot = Chatbot("TestBot", data_file=self.data_file, memory=True)
        bot.add_intent("introduce", ["my name is", "i am", "call me"], ["Nice to meet you {name}!"])
        response = bot.respond("call me Alice")
        self.assertIn("Alice", response)

    def test_remove_intent(self):
        bot = Chatbot("TestBot", data_file=self.data_file)
        bot.add_intent("test", ["hello"], ["hi"])
        bot.remove_intent("test")
        self.assertNotIn("test", bot.list_intents())


if __name__ == '__main__':
    unittest.main()
