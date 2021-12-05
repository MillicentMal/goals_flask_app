import unittest
from app import Task, User, app, counter, user_check

class Tests(unittest.TestCase):
    #check for response 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
    
    #check delete_task
    # def test_delete(self, id):
    #     pass
    
    def test_user_check(self):
        name = 'David'
        name_2 = "Millie"
        
        #user in Database
        self.assertEqual(user_check(name), True)
        #None existent user
        
        self.assertEqual(user_check(name_2), False)
        
    
    def test_counter(self):
        user = "David"
        current_user = User.query.filter_by(nickname=user).first()
        tasks = Task.query.filter_by(task_owner=current_user.id).count()
        self.assertEqual(counter(current_user), tasks)
    
    
    
        
    
    
        
        
        


if __name__ == "__main__":
    unittest.main()
    
        