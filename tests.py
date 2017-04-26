from app_factory import create_app
import unittest


"""
To be implemented... probably
"""
app, db = create_app("DEBUG")
app.testing = True


class HousenetBaseTestCase:

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_add_amount(self):
        self.app.post("/profile/Person%201/", data={"t": 1})


class CliTestsCase(HousenetBaseTestCase, unittest.TestCase):

    def test_save_db(self):
        pass


class TestHousenetInit(unittest.TestCase):

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()