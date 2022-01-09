
import unittest
from flask_login.utils import login_user
from app import Task, User, counter, delete_task, progress_check, user_check
from flask_testing import TestCase
from app import app, db


class CompletedTest(TestCase):

    
    TESTING = True
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        return app

    def setUp(self):
        """method to set up the database after before every test
        """
        db.create_all()

    def tearDown(self):  
        """
        method to delete the tables after every test
        """      
        db.session.remove()
        db.drop_all()
# your test cases
    def test_add_user(self):
        """
        GIVEN: A user of name Test
        WHEN: the user is added to the database
        THEN: the user should be found in the database
        """
        user = User('Test')
        db.session.add(user)
        db.session.commit()
        # this works
        assert user in User.query.all()
        

    def test_tasks(self):
        """
        GIVEN: a Task of {name: python, description: test, task_owner: Test, completed: TO-DO} 
        WHEN: The task is added to the Task table
        THEN: the task should be found in the table
        """
        task = Task('python', 'test', 'Test', 'TO-DO')
        db.session.add(task)
        db.session.commit()
        assert task in Task.query.all()

    def test_delete_task(self):
        """
        GIVEN: a Task of {name: python, description: test, task_owner: Test, completed: TO-DO} 
        WHEN: The task is added to the Task table
        THEN: the delete_task route should redirect to the tasks route after successful deletion and task should not be found
        """
        # for task in database
        user = User('Test')
        db.session.add(user)
        db.session.commit()
        task = Task('python', 'test', user.id, 'TO-DO')
        db.session.add(task)
        db.session.commit()
        tester = app.test_client(self)
        response = tester.get(f'/delete_task/{task.id}')
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)
        assert task not in Task.query.all()
        
                
    def test_delete_task_2(self):
        """
        GIVEN: a Task of {name: python, description: test, task_owner: Test, completed: TO-DO} 
        WHEN: The task does not exist in the table
        THEN: the delete_task route should return a status code 404
        """
        tester = app.test_client(self)
        task = Task('python', 'test', 'Test', 'TO-DO')
        absent = tester.get(f'/delete_task/{task.id}')
        statuscode = absent.status_code
        self.assertEqual(statuscode, 404)
        
    def test_delete_task_3(self):
        """
        GIVEN: a Task of {name: python, description: test, task_owner: Test, completed: TO-DO} 
        WHEN: The task does exist in the table but the name is used instead of the id
        THEN: the delete_task route should return a status code 404
        """
        tester = app.test_client(self)
        user = User('Test')
        db.session.add(user)
        db.session.commit()
        task = Task('python', 'test', user.id, 'TO-DO')
        db.session.add(task)
        db.session.commit()
        response = tester.get(f'/delete_task/{task.name}')
        statuscode = response.status_code
        self.assertEqual(statuscode, 404)
        
    def test_edit_task(self):
        """
        GIVEN: a Task of {name: python, description: test, task_owner: Test, completed: TO-DO} and using its name on the route
        WHEN: The task exists in the table
        THEN: the edit_task route should return a statuscode of 404
        """
        tester = app.test_client(self)
        task = Task('python', 'test', 'Test', 'TO-DO')
        db.session.add(task)
        db.session.commit()
        response = tester.get(f'/edit_task/{task.name}')
        statuscode = response.status_code
        self.assertEqual(statuscode, 404)
    
    def test_edit_task(self):
        """
        GIVEN: a Task of {name: python, description: test, task_owner: Test, completed: TO-DO} 
        WHEN: The task is added to the Task table
        THEN: the edit_task route should return a statuscode of 200
        """
        tester = app.test_client(self)
        task = Task('python', 'test', 'Test', 'TO-DO')
        db.session.add(task)
        db.session.commit()
        response = tester.get(f'/edit_task/{task.id}')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        
    def test_user_check(self):
        

        user = User('Test')
        db.session.add(user)
        db.session.commit()
        #user in Database
        self.assertEqual(user_check(user.nickname),  True) 
        #None existent user
        user_2 = User('Test_2')
        self.assertEqual(user_check(user_2.nickname), False)
        
    def test_progress_check_1(self):
        """
        GIVEN: a user Test 
        WHEN: the user has a progress of 100 
        THEN: the message returned should contain congratulations
        """
        user = User('Test')
        user.progress = 100
        db.session.add(user)
        db.session.commit()
        self.assertEqual("Congratulations! You have reached your goal for the day. Call us for a free drink!", progress_check(user.id))
        
    def test_progress_check_2(self):
        """
        GIVEN: a user Test 
        WHEN: the user has a progress of 70
        THEN: the message returned should say how far along the user in achieving their goal
        """
        tester = app.test_client(self)
        user = User('Test')
        user.progress = 70
        db.session.add(user)
        db.session.commit()
        self.assertEqual("You still have 30 PERCENT left to reach your goal", progress_check(user.id))
    
    
    def test_counter(self):
        """
        GIVEN: a user Test
        WHEN: they have tasks in the database
        THEN: counter returns the number of those tasks
        """
        user = User('Test')
        db.session.add(user)
        db.session.commit()
        task = Task('python', 'test', user.id, 'TO-DO')
        db.session.add(task)
        db.session.commit()
        tasks = Task.query.filter_by(task_owner=user.id).count()
        self.assertEqual(counter(tasks), 1)
        
        
    def test_index(self):
        """
        testing if the routing works for the homepage: index.html
        """
        tester = app.test_client(self)
        response = tester.get('/')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        
    

if __name__ == '__main__':
    unittest.main()