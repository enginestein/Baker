import os
import unittest
import tempfile
import json
import uuid

from baker.trainer import Trainer


def _unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestTrainer(unittest.TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.script_dir, 'data.json')

    def _fresh_trainer(self):
        return Trainer(self.data_file)

    def test_train_single_response(self):
        bot = self._fresh_trainer()
        key = _unique("TRAIN_Q")
        bot.train_response(key, "TEST_R")
        self.assertEqual(bot.get_response(key), "TEST_R")
        bot.reset_responses(key)

    def test_get_response_exact(self):
        bot = self._fresh_trainer()
        self.assertIsNotNone(bot.get_response("Hello"))

    def test_train_many(self):
        bot = self._fresh_trainer()
        key1, key2 = _unique("MQ1"), _unique("MQ2")
        pairs = [(key1, "R1"), (key2, "R2")]
        bot.train_many(pairs)
        self.assertEqual(bot.get_response(key1), "R1")
        self.assertEqual(bot.get_response(key2), "R2")
        bot.reset_responses(key1)
        bot.reset_responses(key2)

    def test_train_from_json_file(self):
        bot = self._fresh_trainer()
        key = _unique("BULK_Q")
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            json.dump({key: ["BulkR1", "BulkR2"]}, f)
            temp_path = f.name
        try:
            bot.train_from_json(temp_path)
            self.assertIn(key, bot.list_key_questions())
            self.assertEqual(bot.count_responses(key), 2)
            bot.reset_responses(key)
        finally:
            os.unlink(temp_path)

    def test_auto_learn(self):
        bot = self._fresh_trainer()
        key = _unique("AUTO_Q")
        bot.auto_learn([(key, "AutoR")])
        self.assertEqual(bot.get_response(key), "AutoR")
        bot.reset_responses(key)

    def test_tfidf_matching_by_default(self):
        bot = self._fresh_trainer()
        response = bot.get_response("how are you today?")
        self.assertIsInstance(response, str)

    def test_list_keys(self):
        bot = self._fresh_trainer()
        keys = bot.list_key_questions()
        self.assertIn("Hello", keys)


if __name__ == '__main__':
    unittest.main()
