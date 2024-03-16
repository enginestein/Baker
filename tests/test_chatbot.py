import os
import unittest
import baker.chatbot
import baker.trainer
import baker.bparser

class TestChatbot(unittest.TestCase):
    def test_chatbot(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, 'data.json')

        traine = baker.trainer.Trainer(data_file)
        parser = baker.bparser.Parser(data_file)
        my_chatbot = baker.chatbot.Chatbot("MyChatbot")
        my_chatbot.session(traine, parser)

if __name__ == '__main__':
    unittest.main()
