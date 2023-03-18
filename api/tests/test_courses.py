import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.student import Student
from ..models.course import Course
from ..models.grade import Grade
from flask_jwt_extended import create_access_token

class CourseTestCase(unittest.TestCase):

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


    def test_course_registration(self):
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }
            
        data = {
            "name": "testcourse",
            "code": "testcode",
            "teacher": "testteacher",
            "credits": 3
        }

        response = self.client.post('/course/courses', json=data, headers=headers)

        course = Course.query.filter_by(name="testcourse").first()

        assert course.name == "testcourse"

        assert response.status_code == 201



    def test_course_get_all(self):
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.get('/course/courses', headers=headers)

        assert response.status_code == 200
        

    def test_course_create(self):

        
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        


        data = {
            "name": "testcourse",
            "code": "testcode",
            "teacher": "testteacher",
            "credits": 3
        }

        response = self.client.post('/course/courses', json=data, headers=headers)

        assert response.status_code == 201


    def test_course_registration(self):
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        data = {
            "name": "testcourse",
            "code": "testcode",
            "teacher": "testteacher",
            "credits": 3
        }

        response = self.client.post('/course/courses', json=data, headers=headers)

        assert response.status_code == 201


        



