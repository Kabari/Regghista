from flask import Flask
from flask_restx import Api
from .students.views import student_namespace
from .grades.views import grade_namespace
from .courses.views import course_namespace
from .config.config import config_dict
from .utils import db
from .models.grade import Grade
from .models.course import Course
from .models.student import Student
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed


def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt; JWT &gt; token to authorize **"
        }
    }

    api = Api(app, 
        version='1.0', 
        title='Regghi', 
        description='A Student Management REST API service',
        authorizations=authorizations,
        security='Bearer Auth')

    api.add_namespace(student_namespace, path='/student')
    api.add_namespace(grade_namespace, path='/grade')
    api.add_namespace(course_namespace, path='/course')
    # api.add_namespace(...) 

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404
    
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Student': Student,
            'Course': Course,
            'Grade': Grade
        }

    return app
