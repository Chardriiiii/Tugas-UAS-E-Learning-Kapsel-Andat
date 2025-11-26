from flask import Blueprint
from src.controllers.student_controller import *

student_bp = Blueprint('student_bp', __name__)

student_bp.route('/students', methods=['GET'])(get_students)
student_bp.route('/students/<student_id>', methods=['GET'])(get_student_by_id)
student_bp.route('/students', methods=['POST'])(create_student)
student_bp.route('/students/<student_id>', methods=['PUT'])(update_student)
student_bp.route('/students/<student_id>', methods=['DELETE'])(delete_student)