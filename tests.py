import os
from app_factory import create_app
import unittest
import tempfile

app, db = create_app("DEBUG")


class HousenetBaseTestCase:

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])

    def test_add_amount(self):
        self.app.post("/profile/Person%201/", data={""})


class CliTestsCase(HousenetBaseTestCase, unittest.TestCase):

    def test_save_db(self):
        pass




if __name__ == '__main__':
    unittest.main()