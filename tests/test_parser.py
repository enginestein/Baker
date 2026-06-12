import os
import unittest
import uuid

from baker.bparser import Parser


def _unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestParser(unittest.TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.script_dir, 'data.json')

    def _fresh_parser(self):
        return Parser(self.data_file)

    def test_get_response_exact_match(self):
        bot = self._fresh_parser()
        response = bot.get_response("Hello")
        self.assertIn(response, ["Hi", "Hello", "Hey mister, how are you?"])

    def test_get_response_unknown(self):
        bot = self._fresh_parser()
        response = bot.get_response("XYZZYX_UNKNOWN")
        self.assertIsInstance(response, str)

    def test_get_response_empty_data(self):
        empty_file = os.path.join(self.script_dir, 'data-empty.json')
        bot = Parser(empty_file)
        response = bot.get_response("Anything")
        self.assertIsInstance(response, str)

    def test_train_and_get(self):
        bot = self._fresh_parser()
        key = _unique("TRAIN_Q")
        bot.train_response(key, "TEST_RESPONSE")
        response = bot.get_response(key)
        self.assertEqual(response, "TEST_RESPONSE")
        bot.reset_responses(key)

    def test_get_response_with_confidence(self):
        bot = self._fresh_parser()
        response, confidence = bot.get_response("Hello", return_confidence=True)
        self.assertIsInstance(response, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)

    def test_tfidf_matches_variants(self):
        bot = self._fresh_parser()
        response = bot.get_response("hello there")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_char_ngram_handles_typos(self):
        bot = Parser(self.data_file, threshold=0.2)
        response = bot.get_response("helloo")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_matcher_confidence_known(self):
        bot = self._fresh_parser()
        matched, score = bot.matcher.best_match("Hello")
        self.assertIsNotNone(matched)
        self.assertGreaterEqual(score, 0.0)

    def test_matcher_confidence_unknown(self):
        bot = self._fresh_parser()
        matched, score = bot.matcher.best_match("totally_unknown_xyz")
        self.assertIsNone(matched)
        self.assertIsInstance(score, float)

    def test_semantic_backend_fallback(self):
        bot = Parser(self.data_file, backend='semantic')
        response = bot.get_response("Hello")
        self.assertIsInstance(response, str)


if __name__ == '__main__':
    unittest.main()
