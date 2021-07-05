import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import false

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "example1"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '123','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        self.new_question = {
            'question': 'From where the sun rise?',
            'answer': 'East',
            'category': '1',
            'difficulty': 1,
            }
        self.bad_new_question = {
            'question': 'From where the sun rise?',
            'answer': 'East',
            'difficulty': 1,
            }
        self.quiz = {
            'previous_questions':[3, 7],
            'quiz_category': 1,
            'id': 5,
            'type': 'Entertainment'
        }
        self.bad_quiz={
           'previous_questions': []
        }
     
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        # ----------------
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        
    def test_404_sent_requesting_no_category(self):
        res = self.client().get('/categories/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
#        # ----------------
    def test_get_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm':'whats'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['total_questions']),8)
    
    def test_404_get_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm':''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
#          # ----------------
    def test_create_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'])
    
    def test_422_questions_creation_fails(self):
        res = self.client().post('/questions', json=self.bad_new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
#     # --------------
    def test_delete_question(self):
        q_id = 5
        res = self.client().delete('/questions/{q_id}')
        data = json.loads(res.data)
        q = Question.query.filter(Question.id == q_id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'],str(q_id))
        self.assertEqual(q, None)

    def test_422_delete_question(self):
        res = self.client().delete('/questions/888888')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
    
#    # ----------------
    def test_play_quiz(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_404_play_quiz(self):
        quiz_round = {'previous_questions': []}
        response = self.client().post('/quizzes', json=self.bad_quiz)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()