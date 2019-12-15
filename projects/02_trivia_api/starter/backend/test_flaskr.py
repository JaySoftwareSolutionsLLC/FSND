import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, jsonify
from flaskr import create_app
from models import setup_db, Question, Category


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
            
            setup_db(self.app, self.database_path)
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            Category.query.delete()
            Question.query.delete()

            category1 = Category(type="Science") # Create new category for DB
            self.db.session.add(category1) # Add category to DB
            self.db.session.commit() # Commit changes
            question1 = Question(question="What year was seal & Design founded", answer="1987", category=4, difficulty=2) # Create new category for DB
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
        res = self.client().post('/api/questions', json={"question": "What year did the Titanic Sink", "answer": "1912", "category": 4, "difficulty": 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200) # Ensure successful request
        self.assertTrue(data['success']) # Ensure JSON response was successful
        # Ensure posted data persisted in DB

    def test_get_paginated_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(data['total_questions'], 1000)

    def test_get_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(data['total_categories'], 0)

    def test_delete_question(self):
        res = self.client().delete('/api/questions/11')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_invalid_question(self):
        res = self.client().delete('/api/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['success'])

    def test_search_questions(self):
        res = self.client().post('/api/questions/search', json={"searchTerm" : "Seal"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 3)

        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()