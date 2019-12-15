import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app, 'postgres://postgres:$u944jAk161519@localhost:5432/trivia')

  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TO-DOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
    return response

  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/api/categories', methods=['GET'])
  # @cross_origin()
  def retrieve_categories():
    # page = request.args.get('page', 1, type=int) # Retrieve page argument from request to specify which plants to return
    # pageSize = 10
    # start = (page - 1) * pageSize
    # end = start + pageSize

    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    return jsonify({
      "success":True,
      "categories":formatted_categories,
      "total_categories":len(formatted_categories)
    })

  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories.

  @TODO TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/api/questions', methods=['GET'])
  # @cross_origin()
  def retrieve_questions():
    page = request.args.get('page', 1, type=int) # Retrieve page argument from request to specify which plants to return
    pageSize = 10
    start = (page - 1) * pageSize
    end = start + pageSize

    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]

    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      "success":True,
      "questions":formatted_questions[start:end],
      "categories":formatted_categories,
      "total_questions":len(formatted_questions),

    })

  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  @TODO TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    response = {}
    question_to_delete = Question.query.get(question_id)
    response['request'] = question_to_delete.format()
    try:
      question_to_delete.delete()
      db.session.commit()
      response['success'] = True
    except:
      db.session.rollback()
      response['success'] = False
    finally:
      db.session.close()
      return jsonify(response)

  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  @TODO TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/api/questions', methods=['POST'])
  def create_question():
    response = {}
    question = request.json['question']
    answer = request.json['answer']
    category = request.json['category']
    difficulty = request.json['difficulty']
    new_question = Question(question = question, answer = answer, category = category, difficulty = difficulty)
    response['request'] = new_question.format()
    try:
      db.session.add(new_question)
      db.session.commit()
      response['success'] = True
    except:
      db.session.rollback()
      response['success'] = False
    finally:
      db.session.close()
      return jsonify(response)

  '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  @TODO TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/questions/search', methods=['POST'])
  # @cross_origin()
  def search_questions():
    search_term = request.json['searchTerm']
    relevant_questions = db.session.query(Question).filter(Question.question.ilike('%' + search_term + '%')).all()
    formatted_questions = [question.format() for question in relevant_questions]
    return jsonify({
      "success":True,
      "questions":formatted_questions,
      "total_questions":len(formatted_questions)
    })

  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  @TODO TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
  # @cross_origin()
  def retrieve_category_questions(category_id):

    relevant_questions = Question.query.filter_by(category = category_id).all()
    formatted_questions = [question.format() for question in relevant_questions]
    return jsonify({
      "success":True,
      "questions":formatted_questions,
      "total_questions":len(formatted_questions),
      "currentCategory":category_id
    })


  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  @TODO TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/api/play', methods = ['POST'])
  def play():
    if 'quizCategory' in request.json:
      category_id = request.json['quizCategory']
    else:
      category_id = None
    if 'previousQuestions' in request.json:
      previous_question_ids = request.json['previousQuestions'] 
    else:
      previous_question_ids = None
    if category_id:
      relevant_questions = db.session.query(Question).filter(Question.id.notin_(previous_question_ids)).filter(Question.category == category_id).all()
    else:
      relevant_questions = db.session.query(Question).filter(Question.id.notin_(previous_question_ids)).all()
    # return jsonify({
    #   "questions":relevant_questions
    # })

    if len(relevant_questions) > 0:
      chosen_question = random.choice(relevant_questions)
      formatted_question = chosen_question.format()
      return jsonify({
        "success":True,
        "question":formatted_question,
      })
    else:
      return jsonify({
        "success":True,
        "question":False,
        # "requestData":request # This causes a fatal error. Something in request is not json serialized
      })

  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422

  return app