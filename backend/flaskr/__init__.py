import os
from flask import Flask, request, abort, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(active=True, test_config=None):
    # create and configure the app
    app = Flask(__name__)
    with app.app_context():
        if active:
            setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()

            categories_list = {
                category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'categories': categories_list
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'error': 'An error occurred while fetching categories.'
            })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        try:
            category = session.get(category_id)

            if not category:
                return jsonify({
                    'success': False,
                    'error': 'Category not found',
                }), 404

            questions = Question.query.filter(
                Question.category == category_id).all()

            total_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': total_questions,
                'totalQuestions': len(total_questions),
                'currentCategory': category.type
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'error': 'An error occurred while retrieving questions by category',
            })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions_per_page = 10

        page = request.args.get('page', 1, type=int)

        start_index = (page - 1) * questions_per_page

        questions = Question.query.limit(
            questions_per_page).offset(start_index).all()

        questions_list = [{'id': question.id,
                           'question': question.question,
                           'answer': question.answer,
                           'category': question.category,
                           'difficulty': question.difficulty} for question in questions]

        total_questions = Question.query.count()
        if len(questions) == 0:
            abort(404)
        categories = Category.query.all()
        categories_list = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'questions': questions_list,
            'total_questions': total_questions,
            'current_category': 'Science',
            'categories': categories_list
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(422)
            else:
                question.delete()
                total_questions = Question.query.count()

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': Question.query.all(),
                'totalQuestions': total_questions
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'error': 'An error occurred while deleting the question'
            })

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            data = request.get_json()

            new_question = Question(
                question=data.get('question', ''),
                answer=data.get('answer', ''),
                category=data.get('category', ''),
                difficulty=data.get('difficulty', 1)
            )

            new_question.insert()

            return jsonify({
                'success': True
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'error': 'An error occurred while creating the question'
            })

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            search_term = request.get_json().get('searchTerm', '')

            questions = Question.query.filter(
                Question.question.ilike(
                    f'%{search_term}%')).all()

            questions_list = [question.format() for question in questions]

            if len(questions_list) == 0:
                abort(422)

            return jsonify({
                'success': True,
                'questions': questions_list,
                'totalQuestions': len(questions)
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'error': 'An error occurred while searching for questions'
            })

    @app.route('/questions/category/<int:category_id>', methods=['GET'])
    def get_questions_by_category(category_id):
        try:

            questions = Question.query.filter(
                Question.category == category_id).all()

            if not questions:
                return jsonify({
                    'success': False,
                    'error': 'No questions found for the specified category'
                }), 404

            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions
            })

        except Exception as e:
            print(e)

            return jsonify({
                'success': False,
                'error': 'An error occurred while retrieving questions by category'
            })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        try:
            data = request.get_json()
            category = data.get('quiz_category')
            cate_id = category.get('id') if category else None
            previous_questions = data.get('previous_questions', [])
            question = None

            if cate_id == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == cate_id
                ).all()

            if len(questions) == 0:
                abort(422)

            if questions:
                question = random.choice(questions)

            formatted_question = question.format()

            return jsonify({
                'success': True,
                'question': formatted_question
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'error': 'An error occurred while getting a quiz question'
            })

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        return jsonify({
            'success': False,
            'error': 'Unprocessable Entity',
            'message': 'Unable to process the request'
        }), 422

    @app.errorhandler(405)
    def not_found(error):
        return (jsonify({"success": False, "error": 405,
                         "message": "method not allowed"}), 405, )

    @app.errorhandler(500)
    def server_error(error):
        return (jsonify({"success": False, "error": 500,
                         "message": "Internal Server Error"}), 500, )

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
