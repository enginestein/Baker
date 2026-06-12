import os
import unittest
import uuid

from baker import Chatbot


def _unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.script_dir, 'data.json')

    def _fresh_bot(self):
        return Chatbot("TestBot", data_file=self.data_file)

    def test_responds_to_exact_match(self):
        bot = self._fresh_bot()
        response = bot.respond("Hello")
        self.assertIsInstance(response, str)

    def test_responds_to_variant(self):
        bot = self._fresh_bot()
        response = bot.respond("HELLO")
        self.assertIsInstance(response, str)

    def test_responds_to_unknown(self):
        bot = self._fresh_bot()
        response = bot.respond("xyzzy_nobody_knows_this")
        self.assertIsInstance(response, str)

    def test_train(self):
        bot = self._fresh_bot()
        key = _unique("TRAIN")
        bot.train(key, "Test response")
        response = bot.respond(key)
        self.assertEqual(response, "Test response")

    def test_train_many(self):
        bot = self._fresh_bot()
        k1, k2 = _unique("Q1"), _unique("Q2")
        bot.train_many([(k1, "R1"), (k2, "R2")])
        self.assertEqual(bot.respond(k1), "R1")
        self.assertEqual(bot.respond(k2), "R2")

    def test_memory(self):
        bot = self._fresh_bot()
        bot.respond("Hello")
        context = bot.get_context()
        self.assertIn('exchange_count', context)
        self.assertGreaterEqual(context['exchange_count'], 1)

    def test_name_extraction(self):
        bot = self._fresh_bot()
        bot.respond("My name is Alice")
        self.assertEqual(bot.memory.get_entity('name'), 'Alice')

    def test_detailed_response(self):
        bot = self._fresh_bot()
        details = bot.respond_detailed("Hello")
        self.assertIn('response', details)
        self.assertIn('confidence', details)
        self.assertIn('matched_key', details)


if __name__ == '__main__':
    unittest.main()
