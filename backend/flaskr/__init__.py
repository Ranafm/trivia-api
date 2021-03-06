import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from models import setup_db, Category, Question
import random
from sqlalchemy.sql.expression import func
from sqlalchemy import desc
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  
  #Similar to Bookshelf exercise 
  QUESTIONS_PER_PAGE = 10
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
      return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
      #@cross_origin
  def get_categories():
      categories = Category.query.all()
      formatted_categories = {category.id : category.type for category in categories}
      if len(categories) == 0:
         abort(404)
      return jsonify({
          'success': True,
          'categories':formatted_categories
      })
        
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
      questions = Question.query.order_by(desc(Question.id)).all()
      current_questions = paginate_questions(request, questions)
      categories = Category.query.all()
      formatted_categories = {category.id : category.type for category in categories}
      if len(current_questions) == 0:
          abort(404)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'categories': formatted_categories ,
          'current_category': None
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      question = Question.query.get(question_id)
      if question is None:
        abort(422) 
      question.delete()
      return jsonify({
          'success': True,
          'deleted_id': question.id,
      })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  
  'Search and add qousetion endpoints are similar to the way used in the books exercise'
  '''
  @TODO: 
  retrive the results based on the serched term  or add qouestion.
  '''
  @app.route("/questions", methods=['POST'])
  def add_and_search_question(): 
    body = request.get_json()
    search = body.get('searchTerm', None)
    try:
      if search :
        results = Question.query.order_by(desc(Question.id)).filter(Question.question.ilike('%{}%'.format(search))).all()
        if results==[]:
           abort(404)
           
        current_questions = paginate_questions(request, results)
        return jsonify({
        'success':True,
        'questions':current_questions,
        'total_questions' : len(results)
        })
      else:
        question = Question(question = body.get('question',None), 
                            answer=body.get('answer',None), 
                            difficulty=body.get('difficulty',None), 
                            category=body.get('category',None))
        if question is None:
          abort(422)
          
        question.insert()
        return jsonify({
            'success': True,
            'created': question.id,
          })
    except:
        abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category.
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_question_by_category(category_id):
    category = Category.query.get(category_id)
    if category is None :
      abort(404)
    
    results = Question.query.order_by(desc(Question.id)).filter(Question.category == category_id ).all()
    current_questions = paginate_questions(request, results)

    return jsonify({
            'success':True,
            'questions':current_questions,
            'total_questions' : len(results),
            'current_category' : category_id
            })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_question_for_quiz():
    body = request.get_json()
    prev_questions = body.get('previous_questions')
    category = body.get('quiz_category')

    if not (prev_questions or category):
      abort(400)
    
    if int(category['id'])== 0:
      q = Question.query.filter(Question.id.notin_(prev_questions)).order_by(Question.id)
    else:
      q = Question.query.filter(Question.category == int(category['id']),  Question.id.notin_(prev_questions)).order_by(Question.id)
    #Random functin
    quiz = q.order_by(func.random()).first()
    # quiz =random.shuffle(q)

    if quiz:
      return jsonify({
      "success": True,
      "question": quiz.format()
    })

    return jsonify({
      "success": True,
      "question": 'Game is Over!'
    })
  '''
  @TODO: 
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
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
    
  return app

    