import unittest

import tests.test_chatbot
import tests.test_functions
import tests.test_parser
import tests.test_trainer

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTest(loader.loadTestsFromModule(tests.test_chatbot))
    suite.addTest(loader.loadTestsFromModule(tests.test_functions))
    suite.addTest(loader.loadTestsFromModule(tests.test_parser))
    suite.addTest(loader.loadTestsFromModule(tests.test_trainer))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
