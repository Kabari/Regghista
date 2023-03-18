from flask_restx import Namespace, Resource, fields, abort
from ..models.grade import Grade
from ..models.student import Student
from ..models.course import Course
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import db

grade_namespace = Namespace('grades', description='namespace for students grades')

grade_model = grade_namespace.model(
    'Grade', {
        'id': fields.Integer(description='An ID'),
        'course_id': fields.Integer(description='The course ID', required=True),
        'student_id': fields.Integer(description='The student ID', required=True),
        'score': fields.Float(description='The score of the student in the course', required=True, default=0.0)
    }
)

add_grade_model = grade_namespace.model(
    'AddGrade', {
        'score': fields.Float(description='The score of the student in the course', required=True, default=0.0)
    }
)

"""
retrieve the grade of a student in a course
"""
@grade_namespace.route('/grades/<int:course_id>/<int:student_id>')
class GradeResource(Resource):
    @grade_namespace.doc(description='Get a grade of a student in a course',
                        params={'course_id': 'The course ID',
                                'student_id': 'The student ID'})
    @grade_namespace.marshal_with(grade_model)
    @jwt_required()
    def get(self, course_id, student_id):
        """Get a grade of a student in a course"""
        grade = Grade.query.filter_by(course_id=course_id, student_id=student_id).first()
        if not grade:
            grade_namespace.abort(HTTPStatus.NOT_FOUND, 'Grade not found')
        return grade, HTTPStatus.OK


"""
the endpoint to add a score to a student in a course
"""
@grade_namespace.route('/grades/students/<int:student_id>/courses/<int:course_id>')
class GradeResource(Resource):
    @grade_namespace.doc(description='Add a score to a student in a course',
                        params={'student_id': 'The student ID',
                                'course_id': 'The course ID'})
    @grade_namespace.expect(add_grade_model)
    @grade_namespace.marshal_with(grade_model)
    @jwt_required()
    def post(self, student_id, course_id):
        """Add a score to a student in a course"""
        name = get_jwt_identity()

        student = Student.query.filter_by(id=student_id).first()

        if not student:
            grade_namespace.abort(HTTPStatus.NOT_FOUND, 'Student not found')

        course = Course.query.filter_by(id=course_id).first()

        if not course:
            grade_namespace.abort(HTTPStatus.NOT_FOUND, 'Course not found')
        
        grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()

        if grade:
            grade_namespace.abort(HTTPStatus.CONFLICT, 'Grade already exists')
        
        new_grade = Grade(
            score=grade_namespace.payload['score']
        )

        new_grade.save()

        return new_grade, HTTPStatus.CREATED