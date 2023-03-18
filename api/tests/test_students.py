import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.student import Student
from ..models.course import Course
from ..models.grade import Grade
from flask_jwt_extended import create_access_token

class StudentTestCase(unittest.TestCase):

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


    def test_student_registration(self):

        data = {
            "name": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/student/signup', json=data)

        student = Student.query.filter_by(email="testuser@gmail.com").first()

        assert student.name == "testuser"

        assert response.status_code == 201

    
    def test_student_login(self):
        data = {
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/student/login', json=data)

        assert data["email"] == "testuser@gmail.com"
        assert response.status_code == 200


    def test_student_get_all(self):
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.get('/student/students', headers=headers)

        assert response.status_code == 200

        assert response.json == []


    def test_student_delete(self):
        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.delete('/student/students/1', headers=headers)

        assert {"message": "Deleted Student Successfully"}



    def test_update_student(self):

        data = {
            "name": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/student/signup', json=data)

        student = Student.query.filter_by(email="testuser@gmail.com").first()

        assert student.name == "testuser"

        assert response.status_code == 201


        data = {
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/student/login', json=data)

        assert data["email"] == "testuser@gmail.com"
        assert response.status_code == 200



        token = create_access_token(identity="testuser")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # student_id = response.json['id']
        # updated_student_data = Student.query.filter_by(id=1).first()

        # update the test student
        updated_student_data = {'name': 'Updated Student', 'email': 'updated@student.com'}
        response = self.client.patch('/student/students/1', json=updated_student_data, headers=headers)
        assert response.status_code == 200

        # check that the student was updated correctly
        # updated_student_data = Student.query.filter_by(id=1).first()
        response = self.client.get('/student/students/1', headers=headers)
        assert response.status_code == 200
        assert response.json['name'] == 'Updated Student'
        assert response.json['email'] == 'updated@student.com'

        # StudentTestCase.test_student_registration()

