from flask import request
from flask_restx import Namespace, Resource, fields, abort
from ..courses.views import course_namespace
from ..grades.views import grade_namespace
from ..models.student import Student, calculate_gpa
from ..models.grade import Grade
from ..models.course import Course
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity


student_namespace = Namespace('student', description='namespace for student')

signup_model = student_namespace.model(
    'SignUp', {
        'id': fields.Integer(),
        'name': fields.String(required=True, description='The Students Full name'),
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password'),
        'role': fields.String(description='The role of the user', required=True,
            enum = ['admin','student'])

    }
)

login_model = student_namespace.model(
    'Login', {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password'),
    }
)

get_student_model = student_namespace.model(
    'GetStudent', {
        'id': fields.Integer(description='An ID'),
        'name': fields.String(description='Name of student', required=True),
        'email': fields.String(description='Email of student', required=True)
    }
)


update_student_model = student_namespace.model(
    'UpdateStudent', {
        'name': fields.String(description='Name of student'),
        'email': fields.String(description='Email of student')
    }
)


student_model = student_namespace.model(
    'Student', {
        'id': fields.Integer(),
        'name': fields.String(required=True, description='The students Full name'),
        'email': fields.String(required=True, description='An email'),
        'password_hash': fields.String(required=True, description='A password'),
        'role': fields.String(description='The role of the user', required=True,
            enum = ['admin','student'])
    }
)

get_students_grade_model = course_namespace.model(
    'GetCourse', {
        'id': fields.Integer(description='An ID'),
        'name': fields.String(description='Name of course', required=True),
        'code': fields.String(description='Code of course', required=True),
        'teacher': fields.String(description='Teacher of course', required=True),
        'credits': fields.Integer(description='Credits of course', required=True),
        'grades': fields.String(description='The grades of all students')
    }
)

grade_model = grade_namespace.model('Grade', {
    'student_name': fields.String(required=True, description='The name of the student'),
    'score': fields.Float(required=True, description='The grade score')
})

grades_response_model = grade_namespace.model('GradesResponse', {
    'course_name': fields.String(required=True, description='The name of the course'),
    'grades': fields.List(fields.Nested(grade_model), required=True, description='The list of grades')
})



@student_namespace.route('/signup')
class SignUp(Resource):
    
    @student_namespace.expect(signup_model)
    @student_namespace.marshal_with(student_model)
    def post(self):
        """
        Sign up a user
        """
        data = request.get_json()
        new_student = Student(
            name = data.get('name'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password'))
        )

        new_student.save()


        return new_student, HTTPStatus.CREATED

@student_namespace.route('/login')
class Login(Resource):
    @student_namespace.expect(login_model)
    def post(self):
        """
        Generate JWT Token
        """
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        
        student = Student.query.filter_by(email=email).first()

        if (student is not None) and check_password_hash(student.password_hash, password):
            access_token = create_access_token(identity=student.email)
            refresh_token = create_refresh_token(identity=student.email)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.OK
        
            


@student_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        email = get_jwt_identity()

        access_token = create_access_token(identity=email)

        return {'access_token': access_token}, HTTPStatus.OK



@student_namespace.route('/students')
class StudentGetAll(Resource):
    @student_namespace.marshal_list_with(get_student_model)
    @student_namespace.doc(description='Get all students')
    @jwt_required()
    def get(self):
        """
        Get all students
        """

        students = Student.query.all()

        return students, HTTPStatus.OK



@student_namespace.route('/students/<int:student_id>')
class StudentUpdateDelete(Resource):
    @student_namespace.doc(description='Update a student by id',
                            params={'student_id': 'An ID'})
    @student_namespace.marshal_with(update_student_model)
    @student_namespace.expect(update_student_model)
    @jwt_required()
    def put(self, student_id):
        """
        Update a student by id
        """

        student_to_update = Student.get_by_id(student_id)
        if not student_to_update:
            return {"message": "Student not found"}, HTTPStatus.NOT_FOUND

        data = request.get_json()

        student_to_update.name = data.get('name')
        student_to_update.email = data.get('email')

        db.session.commit()

        return student_to_update, HTTPStatus.OK


    @student_namespace.doc(description='Delete a student by id')
    @jwt_required()
    def delete(self, student_id):
        """
        Delete a student by id
        """
        student_to_delete = Student.get_by_id(student_id)

        student_to_delete.delete()

        return {"message": "Deleted Student Successfully"}, HTTPStatus.OK


"""
Get all students that are enrolled in a course
"""
@student_namespace.route('/courses/<int:course_id>/students')
class CourseStudents(Resource):
    @student_namespace.marshal_list_with(get_student_model)
    @student_namespace.doc(description='Get all students in a course')
    @jwt_required()
    def get(self, course_id):
        """
        Get all students in a course
        """
        course = Course.get_by_id(course_id)

        students = course.students

        return students, HTTPStatus.OK


"""
Get the GPA of a student
"""
@student_namespace.route('/students/<int:student_id>/gpa')
class StudentGPA(Resource):
    @student_namespace.doc(description='Get the GPA of a student',
                        responses={200: 'Success',
                                404: 'Student not found'},
                        params={'student_id': 'The student id'})
    @jwt_required()
    def get(self, student_id):
        """
        Get the GPA of a student
        """
        student = Student.get_by_id(student_id)

        if not student:
            return {"message": "Student not found"}, HTTPStatus.NOT_FOUND

        gpa = calculate_gpa(student)

        return {"gpa": gpa}, HTTPStatus.OK  


"""
Retrieve the grade for each student in a course
"""
@student_namespace.route('/courses/<int:course_id>/grades')
class CourseGrades(Resource):
    @student_namespace.marshal_list_with(grades_response_model)
    @student_namespace.doc(description='Get the grades of all students in a course',
                        responses={200: 'Success',
                                404: 'Course not found'},
                        params={'course_id': 'The course id'})
    @jwt_required()
    def get(self, course_id):
        """
        Get the grades of all students in a course
        """
        course = Course.get_by_id(course_id)

        if not course:
            return {"message": "Course not found"}, HTTPStatus.NOT_FOUND
        
        grades = Grade.query.filter_by(id=course_id).all()

        # if not grades:

        return {
            'course_name': course.name,
            'grades': [{'student_name': g.student.name, 'score': g.score} for g in grades]
        }, HTTPStatus.OK