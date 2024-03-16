import unittest
import baker.trainer

class TestLoopTrainer(unittest.TestCase):
    def test_loop_training(self):
        trainer = baker.trainer.Trainer('data.json')
        trainer.loop_training()

if __name__ == '__main__':
    unittest.main()
