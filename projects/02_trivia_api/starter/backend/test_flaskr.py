import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, jsonify
from flaskr import create_app
from models import db, setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:$u944jAk161519@localhost:5432/trivia_test"

        # binds the app to the current context
        with self.app.app_context():
            self.db = db
            setup_db(self.app, self.database_path)
            self.db.init_app(self.app)

            self.db.session.execute("TRUNCATE categories, questions RESTART IDENTITY CASCADE")
            category1 = Category(type="Science") # Create new category for DB
            if len(Category.query.all()) == 0: # Only push this category in once
                self.db.session.add(category1) # Add category to DB
                self.db.session.commit() # Commit changes
            question1 = Question(question="What did Alexander Fleming discover", answer="Penicillin", category="1", difficulty=2) # Create new category for DB
            if len(Question.query.all()) == 0: # Only push this category in once
                self.db.session.add(question1) # Add category to DB
                self.db.session.commit() # Commit changes

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    WIP
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_post_question(self):
        res = self.client().post('/api/questions', json={"question": "What was Einsteins famous equation", "answer": "E=MC2", "category": 1, "difficulty": 2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200) # Ensure successful request
        self.assertTrue(data['success']) # Ensure JSON response was successful
        # Ensure posted data persisted in DB
        questions = Question.query.all()
        self.assertEqual(len(questions), 2) # There should now be 2 questions in db      

    def test_post_question_with_bad_input(self):
        res = self.client().post('/api/questions', json={"question": "What was Einsteins famous equation"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200) # Ensure successful request
        self.assertFalse(data['success']) # Ensure JSON response was successful
        # Ensure posted data persisted in DB
        questions = Question.query.all()
        self.assertEqual(len(questions), 1) # There should still only be 1 question in db      

    def test_get_paginated_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(data['total_categories'], 0)

    def test_delete_question(self):
        res = self.client().delete('/api/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['request']['id'], 1) # Verify that question with id=1 was in fact deleted
        # Ensure posted data persisted in DB
        questions = Question.query.all()
        self.assertEqual(len(questions), 0) # There should now be 0 questions in db   

    def test_delete_invalid_question(self):
        res = self.client().delete('/api/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['success']) # Ensure that success response is False

    def test_search_questions(self):
        res = self.client().post('/api/questions/search', json={"searchTerm" : "Alexander"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 1)

    def test_search_questions_with_no_questions(self):
        res = self.client().post('/api/questions/search', json={"searchTerm" : "Doesn't Exist"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 0)

    def test_play(self):
        res = self.client().post('/api/play', json={"quizCategory" : 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['question']['id'], 1)

    def test_play_with_no_questions(self):
        res = self.client().post('/api/play', json={"quizCategory" : 2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertFalse(data['question'])

    def test_get_category_questions(self):
        res = self.client().get('/api/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 1)

    def test_get_category_questions_with_no_questions(self):
        res = self.client().get('/api/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 0) # No questions exist for category 2

        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()