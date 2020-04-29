import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
 
  '''
  Set up CORS. Allow '*' for origins. 
  '''
  CORS(app, resource={'/': {'origins':'*'}})

  def paginate_questions(request, selection):
    '''
    Get paginated list of questions
    '''
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
  '''
  Using the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  
  An endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    '''
    Fetches a dictionary of categories in which the keys are the ids
    and the value is the corresponding string of the category
    '''
    selection = Category.query.order_by(Category.id).all()


    category_dict = {}
    for category in selection:
      category_dict[category.id] = category.type

  
    return jsonify({
      'success': True,
      'categories': category_dict

      })

  '''
  
  An endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 


  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    '''
    Fetches questions for the player, the question contains
    the id, question, category and difficulty.
    '''
    
    selection = Question.query.all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'total_questions': len(selection),
      'questions': current_questions,
      'current_category': None,
      'categories': categories_dict
      })

  '''
  An endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):

    '''
    This deletes selected question from the database
    '''

    try:
      #question = Question.query.filter(Question.id == question_id).one_or_none()
      question = Question.query.get(question_id)
      if question is None:
        abort(404)

      question.delete()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success':True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())      
        })

    except:
      abort(422)


    

  '''
  An endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods = ['POST'])
  def add_questions():

    '''this function enable one add questions to the database'''

    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    if body == {}:
      abort(422)


    try:
      question = Question(new_question, new_answer, new_category,new_difficulty)

      question.insert()
      print(question)
      
      return jsonify ({
        'success': True,
        'created': question.id,
        'total_questions':len(Question.query.all())
        })

    except:
      abort(422)

  '''
  A POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():

    '''this function retrieves question by a search on a string''' 
    body = request.get_json()
    print(body)

    search_term = body.get('searchTerm')
    print(search_term)

    try:

      if len(search_term) != 0:
          search_results = Question.query.filter(
              Question.question.ilike('%' + search_term + '%')).all()

          if len(search_results) == 0:
            abort(404)


      return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
          'total_questions': len(search_results),
          'current_category': None
          })
    except:
      abort(404)


  ''' 
  A GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:id>/questions', methods = ['GET'])

  def get_question_by_category(id):

    '''this function get questions based on category'''

    try:

      
      #retreive paginate question for the category
      category = Category.query.filter_by(id=id).one_or_none()

      selection = Question.query.filter_by(category=category.id).all()

      paginated_question = paginate_questions(request, selection)


      return jsonify({
        'success': True, 
        'questions': paginated_question, 
        'current_category': category.type
        })

    except:
      abort(404)


  '''
  
  A POST endpoint to get questions to play the quiz. 
  This endpoint would take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzez', methods = ['POST'])

  def play_quiz():

    ''' this endpint gets random quiz question not previously displayed'''    

    try:

      body = request.get_json()

      if not ('quiz_category' in body and 'previous_questions' in body):
        abort(400)


      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      print(category)
   
      if (category['id'] == 0):
        questions = Question.query.all()

      else:
        questions = Question.query.filter_by(category = category['id']).all()

      

      total = len(questions)

      

      #get random question
      def get_random_question():
        return questions[random.randrange(0, total, 1)]


      #check if it has been shown before
      def check_if_shownbefore(question):
        
        shownbefore=False
        for i in previous_questions:
          if (i == question.id):
            shownbefore = True

        return shownbefore

      question = get_random_question()

      print(question.format())

      while(check_if_shownbefore(question)):
        question = get_random_question()


        if (len(previous_questions) == total):
          return jsonify({
            'success': True
            })


      return jsonify({
        'success': True,
        'question': question.format()

      })


    except:
      abort(400)


  '''
  
  Error handlers for all expected errors 
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





    