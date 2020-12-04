from flask import Flask, request, abort, jsonify
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from flasgger import Swagger

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10  # also hardcoded in QuestionView.js


def create_app():

    app = Flask(__name__)
    setup_db(app)
    swagger = Swagger(app)

    # Set up CORS. Allow '*' for origins
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # endpoint to handle GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    @cross_origin()
    def get_categories():

        categories_query = Category.query.all()
        categories = {cat.id: cat.type for cat in categories_query}

        if len(categories) == 0:
            abort(404)
        return jsonify({
            'categories': categories
        })

    # endpoint to handle GET requests for questions with pagination
    @app.route('/questions/<int:page>', methods=['GET'])
    def get_paginated_questions(page=1):

        current_index = page - 1

        # quesry questions from DB for current page
        questions = \
            Question.query.order_by(
                Question.id
            ).limit(QUESTIONS_PER_PAGE).offset(current_index * QUESTIONS_PER_PAGE).all()

        # get total number of questions in DB
        total_questions = Question.query.count()

        current_questions = [question.format() for question in questions]

        # get all the categories from DB (required for front end)
        categories_query = Category.query.all()
        # format categories into a dictionary
        categories = {cat.id: cat.type for cat in categories_query}

        # if no questions returned from DB, throw non found error
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories,
            'current_categories': None
        })

    # endpoint to DELETE question using a question ID
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Example endpoint returning a list of colors by palette
        This is using docstrings for specifications.
        ---
        parameters:
            -   name: question_id
                in: path
                type: integer
                required: true
                description: Numeric ID of the question to delete
        responses:
            200:
                description: The question with the specified ID deleted.


        """
        try:
            question = Question.query.filter_by(id=question_id).first_or_404()
            db.session.delete(question)
            db.session.commit()
        except ValueError:
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify({
            'success': True
        })

    # endpoint to POST a new question
    @app.route('/add', methods=['POST'])
    def create_question():
        # request front end values to save into DB
        body = request.get_json()
        question_text = body.get("question")
        answer_text = body.get("answer")
        category = body.get("category")
        difficulty_score = body.get("difficulty")
        try:
            question = Question(question=question_text, answer=answer_text, category=category,
                                difficulty=difficulty_score)
            db.session.add(question)
            db.session.commit()
        except ValueError:
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify({
            'success': True
        })

    # endpoint to get questions based on a search term by substring
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # get search string from the form
        body = request.get_json()
        search_string = body.get('searchTerm')
        categories_query = Category.query.all()
        categories = {cat.id: cat.type for cat in categories_query}

        # query all the questions from DB that contain search string in lowercase
        questions = Question.query.filter(Question.question.ilike('%' + f'%{search_string}%' + '%')).all()

        if len(questions) == 0:
            abort(404)

        found_questions = [question.format() for question in questions]

        return jsonify({
            'questions': found_questions,
            'total_questions': len(found_questions),
            'categories': categories,
            'current_categories': None
        })

    # endpoint to get questions based on category
    @app.route('/categories/<category_id>/questions', methods=['GET'])
    def search_questions_by_category(category_id):

        # query all the questions from DB that have selected category
        questions_query = Question.query.filter_by(category=category_id).all()
        questions = [question.format() for question in questions_query]

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category_id
        })

    # endpoint to get questions to play the quiz
    # takes a category and previous questions and returns a random question in selected category
    @app.route('/play', methods=['POST'])
    def play():

        try:
            # get previous questions and category from front end
            body = request.get_json()
            # print(body)
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            # if category is not selected, get all the questions that were not played
            # before(not in the previous_questions)
            if quiz_category['id'] == 0:
                quiz = Question.query.filter(Question.id.notin_(previous_questions)).all()
            # filter by category
            else:
                quiz = Question.query.filter(Question.category == quiz_category['id'],
                                             Question.id.notin_(previous_questions)).all()

            # format questions into a list of dictionaries
            unanswered_questions = [question.format() for question in quiz]

            # get a random question
            next_question = random.choice(unanswered_questions)

            return jsonify({
                'success': True,
                'question': next_question,
                'current_category': quiz_category
            })
        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
            }), 400

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
            }), 422

    # def paginate_questions(request, selection):
        # page = request.args.get('page', 1, type=int)
        # print(page)
        # items_limit = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
        # print(items_limit)
        # start = (page - 1) * QUESTIONS_PER_PAGE
        # end = start + QUESTIONS_PER_PAGE
        #
        # questions = [question.format() for question in selection]
        # print(questions)
        # current_questions = questions[start:end]

        # current_questions = [question.format() for question in questions]

        # return current_questions

    return app


# # run the app
# if __name__ == '__main__':
#     app.run(debug=True)
