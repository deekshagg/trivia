import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_USER, DB_PASSWORD, DB_URI


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(active=False)
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
            DB_USER, DB_PASSWORD, DB_URI, self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {"question": "Hi", "answer": "Hello", "category": "1", "difficulty": "5"}

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'], True)
        
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_get_questions_valid_pages(self):
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_404_get_questions_beyond_valid_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
        self.assertEqual(data['message'], "Resource not found")

    def test_delete_question(self):
        with self.app.app_context():
            response = self.client().delete(f'/questions/12')
            data = json.loads(response.data)
            question = Question.query.filter(Question.id == 12).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)
        
    def test_422_delete_question(self):
        response = self.client().delete(f'/questions/300')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)
        
    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_add_question(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        
    def test_search_question(self):
        res = self.client().post('/questions/search', json={"searchTerm": "Which"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_search_question(self):
        res = self.client().post('/questions/search', json={"searchTerm": "searchTerm"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        
    def test_quizzes(self):
        res = self.client().post('/quizzes', json={"previous_questions": [9, 15], "quiz_category": {"type": "Art","id": "1"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # Giving an invalid category id which doesn't exist in the DB table so it may fail.
    
    def test_fail_quiz_with_invalid_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": [9, 15], "quiz_category": {"type": "Art","id": "10"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
