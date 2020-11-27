import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'password', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Who is the author of the painting "Morning in a Pine Forest"',
            'answer': 'Shishkin',
            'category': 2,
            'difficulty': 2
        }

        self.search_term = {
            'searchTerm': 'bird'
        }

        self.quiz_questions = {
            'previous_questions': [],
            'quiz_category': {'id': 1}
        }

    #{'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}}

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_paginate_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['total_questions'], True)
        self.assertTrue(data['categories'], True)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'], True)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['total_questions'], True)
        self.assertEqual(data['current_category'], '1')

    def test_search_questions(self):
        res = self.client().post('/questions/search', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['total_questions'], True)
        self.assertTrue(data['categories'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_create_question(self):
        res = self.client().post('/add', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_delete_question(self):
        questions_before_delete = Question.query.all()

        res = self.client().delete('/questions/27')
        data = json.loads(res.data)

        questions_after_delete = Question.query.all()

        deleted_question = Question.query.filter_by(id=27).first()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(len(questions_before_delete), len(questions_after_delete)+1)
        self.assertEqual(deleted_question, None)

    def test_404_delete_question(self):

        res = self.client().delete('/questions/1000')

        self.assertEqual(res.status_code, 404)

    def test_play(self):
        res = self.client().post('/play', json=self.quiz_questions)
        data = json.loads(res.data)

        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['question'], True)
        self.assertTrue(data['current_category'], True)





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()