from flask_restx import Namespace, Resource, fields, abort
from ..models.course import Course
from ..models.student import Student, Enrollment
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import db

course_namespace = Namespace('course', description='namespace for course')

course_model = course_namespace.model(
    'Course', {
        'id': fields.Integer(description='An ID'),
        'name': fields.String(description='Name of course', required=True),
        'code': fields.String(description='Code of course', required=True),
        'teacher': fields.String(description='Teacher of course', required=True),
        'credits': fields.Integer(description='Credits of course', required=True)
    }
)

get_course_model = course_namespace.model(
    'GetCourse', {
        'id': fields.Integer(description='An ID'),
        'name': fields.String(description='Name of course', required=True),
        'code': fields.String(description='Code of course', required=True),
        'teacher': fields.String(description='Teacher of course', required=True),
        'credits': fields.Integer(description='Credits of course', required=True)
    }
)


@course_namespace.route('/courses')
class CourseGetCreate(Resource):
    @course_namespace.marshal_with(get_course_model)
    @course_namespace.doc(description='Get all courses')
    @jwt_required()
    def get(self):
        """
        Get all courses
        """

        courses = Course.query.all()

        return courses, HTTPStatus.OK


    @jwt_required()
    @course_namespace.expect(get_course_model)
    @course_namespace.marshal_with(get_course_model)
    @course_namespace.doc(description='Create a course',)
    def post(self):
        """
        Create a course
        """

        name = get_jwt_identity()

        current_user = Student.query.filter_by(name=name).first()

        data = course_namespace.payload

        if current_user.role != 'admin':
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED

        course = Course(name=data['name'], 
                        code=data['code'], 
                        teacher=data['teacher'],
                        credits=data['credits'],

        )

        course.save()

        return course, HTTPStatus.CREATED
    

"""
Register a student to a course
"""
@course_namespace.route("/courses/<int:course_id>/register/<int:student_id>")
class CourseRegistration(Resource):
    @course_namespace.marshal_with(course_model)
    @course_namespace.doc(description='Register a student to a course')
    @jwt_required()
    def post(self, course_id, student_id):
        """
        Register a student to a course
        """

        name = get_jwt_identity()

        current_user = Student.query.filter_by(name=name).first()

        if current_user.role != 'admin':
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED

        course = Course.query.filter_by(id=course_id).first()

        student = Student.query.filter_by(id=student_id).first()

        if student in course.students:
            return {'message': 'Student is already registered in this course'}, HTTPStatus.BAD_REQUEST

        if Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first():
            return {'message': 'Student is already enrolled in this course'}, HTTPStatus.BAD_REQUEST

        course.students.append(student)


        db.session.commit()

        return course, HTTPStatus.OK

    


"""
Get all courses that a student registered for
"""
@course_namespace.route("/courses/<int:student_id>")
class CourseGetAll(Resource):
    @course_namespace.marshal_with(course_model)
    @course_namespace.doc(description='Get all courses that a student registered for')
    @jwt_required()
    def get(self, student_id):
        """
        Get all courses that a student registered for
        """

        name = get_jwt_identity()

        current_user = Student.query.filter_by(name=name).first()

        # if current_user.role != 'admin':
        #     return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED

        courses = Course.query.filter_by(id=student_id).all()

        return courses, HTTPStatus.OK

