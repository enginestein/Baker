import os
import unittest
import tempfile
import json
import uuid

from baker.bparser import Parser


def _unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.script_dir, 'data.json')

    def _fresh_parser(self):
        return Parser(self.data_file)

    def test_export_responses_json(self):
        parser = self._fresh_parser()
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            temp_path = f.name
        try:
            parser.export_responses(temp_path)
            with open(temp_path, 'r') as f:
                exported = json.load(f)
            self.assertEqual(exported, parser.responses)
        finally:
            os.unlink(temp_path)

    def test_reset_responses(self):
        parser = self._fresh_parser()
        key = _unique("RESET_KEY")
        parser.train_response(key, "test")
        self.assertIn(key, parser.list_key_questions())
        parser.reset_responses(key)
        self.assertNotIn(key, parser.list_key_questions())

    def test_remove_response(self):
        parser = self._fresh_parser()
        key = _unique("RM_KEY")
        parser.train_response(key, "response1")
        parser.train_response(key, "response2")
        self.assertEqual(parser.count_responses(key), 2)
        parser.remove_response(key, "response1")
        self.assertEqual(parser.count_responses(key), 1)
        self.assertIn("response2", parser.responses[key])
        parser.reset_responses(key)

    def test_count_responses(self):
        parser = self._fresh_parser()
        count = parser.count_responses("Hello")
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)

    def test_count_responses_unknown(self):
        parser = self._fresh_parser()
        count = parser.count_responses("NONEXISTENT_KEY_XYZ")
        self.assertEqual(count, 0)

    def test_list_key_questions(self):
        parser = self._fresh_parser()
        keys = parser.list_key_questions()
        self.assertIsInstance(keys, list)
        self.assertIn("Hello", keys)

    def test_export_to_different_format(self):
        parser = self._fresh_parser()
        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False) as f:
            temp_path = f.name
        try:
            parser.export_responses(temp_path)
            imported = Parser(temp_path)
            self.assertEqual(imported.responses, parser.responses)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
