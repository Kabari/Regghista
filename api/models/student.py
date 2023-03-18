from enum import Enum
from ..utils import db
from datetime import datetime

class Role(Enum):
    STUDENT = 'student'
    ADMIN = 'admin'


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)
    courses = db.relationship('Course', secondary='enrollments', backref='students', lazy='dynamic')
    grades = db.relationship('Grade', backref='student', lazy='dynamic')
    role = db.Column(db.Enum(Role), default=Role.STUDENT)


    def __repr__(self):
        return f'<Student {self.name}>'
    

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    

def calculate_gpa(student):
    total_credits = 0
    total_weighted_grade_points = 0

    for grade in student.grades:
        course = grade.course
        credits = course.credits
        score = grade.score

        # Calculate the grade point for the score
        if score >= 90:
            grade_point = 4.0
        elif score >= 80:
            grade_point = 3.0
        elif score >= 70:
            grade_point = 2.0
        elif score >= 60:
            grade_point = 1.0
        else:
            grade_point = 0.0

        # Add the weighted grade point to the total
        weighted_grade_point = grade_point * credits
        total_weighted_grade_points += weighted_grade_point

        # Add the credits to the total
        total_credits += credits

    if total_credits == 0:
        return 0.0

    # Calculate the WGPA
    wgpa = total_weighted_grade_points / total_credits

    # Convert the WGPA to a GPA
    gpa = wgpa / 4.0

    return round(gpa, 2)

    
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    student_id = db.Column(db.Integer(), db.ForeignKey('students.id'), primary_key=True)
    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id'), primary_key=True)











































# from app.models import db

# # Define Student model
# class StudentModel(db.Model):
#     __tablename__ = 'students'
    
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(50), nullable=False)
    
#     registrations = db.relationship('RegistrationModel', backref='student', lazy=True)
    
#     # Define method to serialize student object
#     def serialize(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'email': self.email
#         }
    
#     # Define method to create a new student
#     @classmethod
#     def create(cls, name, email):
#         student = cls(name=name, email=email)
#         db.session.add(student)
#         db.session.commit()
#         return student
    
#     # Define method to update an existing student
#     def update(self, name=None, email=None):
#         if name:
#             self.name = name
#         if email:
#             self.email = email
#         db.session.commit()
    
#     # Define method to delete a student
#     def delete(self):
#         db.session.delete(self)
#         db.session.commit()
