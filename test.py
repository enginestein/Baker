import unittest

import tests.test_chatbot 
import tests.test_functions
import tests.test_loop_trainer
import tests.test_parser
import tests.test_trainer

if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(tests.test_chatbot.TestChatbot))
    #test_suite.addTest(unittest.makeSuite(tests.test_functions.TestFunctions))
    #test_suite.addTest(unittest.makeSuite(tests.test_loop_trainer.TestLoopTrainer))
    #test_suite.addTest(unittest.makeSuite(tests.test_parser.TestParser))
    #test_suite.addTest(unittest.makeSuite(tests.test_trainer.TestTrainer))
    unittest.TextTestRunner().run(test_suite)
