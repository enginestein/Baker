import unittest
import baker.bparser

class TestParser(unittest.TestCase):
    def test_chatbot(self):
        def test_chatbot(bot):
            pass

        bot = baker.bparser.Parser('data.json')
        test_chatbot(bot)

if __name__ == '__main__':
    unittest.main()
