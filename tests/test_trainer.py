import unittest
import baker.trainer

class TestTrainer(unittest.TestCase):
    def test_trainer(self):
        bot = baker.trainer.Trainer('data.json')
        user_input = input("You: ")
        response = bot.get_response(user_input)
        self.assertIsNotNone(response)

        new_response = input("New response: ")
        bot.train_response(user_input, new_response)
        self.assertIn(new_response, bot.get_response(user_input))

if __name__ == '__main__':
    unittest.main()
