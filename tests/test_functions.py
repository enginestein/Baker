import unittest
import baker.bparser

class TestFunctions(unittest.TestCase):
    def test_export_responses(self):
        response_file_name = "data.json"
        parser_instance = baker.bparser.Parser(response_file_name)
        parser_instance.export_responses(export_file_name="data2.json")

    def test_reset_responses(self):
        baker.bparser.Parser.reset_responses("A_User_Question")

    def test_remove_response(self):
        parser_instance2 = baker.bparser.Parser("data.json")
        user_input = "Hello"
        response_to_remove = "Heyy"
        parser_instance2.remove_response(user_input, response_to_remove)

    def test_count_responses(self):
        parser_instance3 = baker.bparser.Parser("data.json")
        user_input = "Hello"
        count = parser_instance3.count_responses(user_input)
        self.assertTrue(isinstance(count, int))

if __name__ == '__main__':
    unittest.main()
