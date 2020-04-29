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
        self.database_name = "trivia_app"
        self.database_path = self.database_path = "postgres://{}:{}@{}/{}".format('tomiwa', 'student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

 
    def test_get_paginated_questions(self):
        '''test response for getting question'''
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    def test_get_paginated_questions_beyond_valid_pages(self):
        '''test error response for getting question'''
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

#------------------------

    def test_get_categories(self):
        '''test response for getting categories of question'''

        res = self.client().get('/categories')
        data = json.loads(res.data)        

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))


    def test_404_for_non_existing_categories(self):
        '''test error response for getting non existing categories of question'''
        res = self.client().get('/categories/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')        

#----------------------

    def test_delete_questions(self):
        '''test response for deleting question'''
        question = Question(question='Would I soon be deleted', answer='Yes, I would',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete('/questions/'+ str(question_id))
        data = json.loads(res.data)        

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],question_id)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)


    def test_422_sent_deleting_non_existing_question(self):
        '''test error response for deleting question'''

        res = self.client().delete('/questions/a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        
#----------------------

    def test_posting_a_new_question(self):
        '''test response for posting a new question'''
        new_question = {
            'question': 'what is the square root of 225',
            'answer': '15',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        print(res)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(['total_questions']))

    def test_error_posting_a_new_question(self):
        '''test error response for posting a new question'''

        questions_before = Question.query.all()
        questions_after = Question.query.all()

        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(len(questions_after), len(questions_before))



#------------------

        

    def test_search_for_a_question(self):
        '''Test search for a question by a given string'''
        res = self.client().post('/questions/search', json={'searchTerm': 'What'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])



    def test_error_searching_for_a_question(self):
        '''Test display error in search for a question by a given string'''
        res = self.client().post('/questions/search', json={'searchTerm': 'zxcvb'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')


#-----------------------------------


    def test_get_question_by_category(self):
        '''Test getting question by category'''
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 'Science')

    def test_404_if_questions_by_category_fails(self):
        """Tests getting questions by category failure 400"""

        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

#-----------------------------------

    def test_get_random_quiz_question_not_previous_diplayed(self):
        '''Test getting random quiz question not previously displayed'''

        res = self.client().post('/quizzez', json={'quiz_category': {'type': 'Entertainment', 'id': '5'}, 'previous_questions': [2] })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 5)

        self.assertNotEqual(data['question']['id'], 2)
        #self.assertNotEqual(data['question']['id'], 21)

    def test_error_get_random_quiz_question_not_previous_diplayed(self):
        '''Test error in getting random quiz question not previously displayed'''

        res = self.client().post('/quizzez', json={'quiz_category': [19],
                                                        'previous_questions': {'type': 'Entertainment', 'id': '5'}})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()