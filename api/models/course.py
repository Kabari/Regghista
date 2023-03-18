from ..utils import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    code = db.Column(db.String(32), nullable=False, unique=True)
    teacher = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer(), nullable=False)
    grades = db.relationship('Grade', backref='course', lazy='dynamic')
    

    def __repr__(self):
        return f'<Course {self.name}>'
    

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
