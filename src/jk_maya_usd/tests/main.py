
import unittest

from jk_maya_usd.tests.utilities import compare_usd_stages, report

def test():
    """Runs all unit tests in the jk_maya_usd package."""
    unittest.main(verbosity=2, module="jk_maya_usd.testing", exit=False)

class Test(unittest.TestCase):
    def test_addition(self):
        src, taget = "", ""
        self.assertEqual(compare_usd_stages(src, taget), report)
        
class TestNotMathOperation(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 -1, 0)

