from ..utils import db

class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer(), primary_key=True)
    student_id = db.Column(db.Integer(), db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer(), db.ForeignKey('courses.id'), nullable=False)
    score = db.Column(db.Float(), nullable=False)
    

    def __repr__(self):
        return f"<Grade {self.grade}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
