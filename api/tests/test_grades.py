import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.student import Student
from ..models.course import Course
from ..models.grade import Grade
from ..tests.test_students import StudentTestCase
from flask_jwt_extended import create_access_token

class GradeTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client =None

    

