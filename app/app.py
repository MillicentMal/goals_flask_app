from flask import Flask, abort
from flask import render_template, request
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_manager, LoginManager, current_user, login_required, login_user, logout_user, UserMixin, user_logged_in
from werkzeug.utils import redirect

# app creation adn configuration
app = Flask(__name__)
# failing to deploy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Lethabo2016.@localhost:3306/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
db = SQLAlchemy(app)

# handling logins
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# login_manager.login_message = "Login to Continue"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    
# classes to be used
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(256), unique=True, nullable=False)
    progress = db.Column(db.Integer)
    task =  db.relationship('Task', backref='user', cascade="all, delete-orphan")
    
    def __init__(self, nickname, progress=0):
        """[summary]
        Args:
            nickname ([str]): [Nickname of the user]
            progress (int, optional): [Shows how far the user has gone on their goals for the day]. Defaults to 0.
        """
        self.nickname = nickname
        self.progress = progress 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(256))
    completed = db.Column(db.String(256))
    task_owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, name, description, task_owner, completed):
        """[summary]
        Args:
            name ([str]): [Name of task]
            description ([str]): [Task description]
            task_owner ([int]): [User who created the task]
            completed ([str]): [Shows whether the task has been completed or not]
        """
        self.name  = name
        self.description = description
        self.completed = completed
        self.task_owner = task_owner
        
        
# Home page

@app.route('/', methods=['GET', 'POST'])
def index():           
    return render_template('index.html')


#Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("nickname") 
        try:
            user_name = User.query.filter_by(nickname=name).first()

# check first if user is not in the database. If the user is not then they are redirected to register
            if not user_name:
                flash("You have to be registered first")
                return redirect(url_for('add_user'))
            login_user(user_name)
            return redirect(url_for('tasks'))
        except:
            abort(400)
            
    return render_template('login.html')

#add user
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = request.form.get("nickname") 
        if new_user != "":  # checks if the user did not submit an empty input
            if user_check(new_user) == True:
                flash("You already have an account. Please log in")
                return redirect(url_for('login'))
            user = User(new_user)
            try:
                db.session.add(user)
                db.session.commit()
                flash("Account successfully created")
                return redirect(url_for('login'))
            except:
               abort(500)
        else:  # gives a user a message to say that their input is blank
            flash("You know you cant have a blank nickname.") 
    return render_template('new_user.html')

#logout
@app.route('/logout')
@login_required
def logout():
   logout_user()
   flash("Logged out")
   return redirect(url_for('index'))


#tasks
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    
    if request.method == "POST" and  counter(current_user.id) < 10:
        name = request.form.get("name")
        if name != "":
            try:
                description = request.form.get("description")
                new_task = Task(name, description, task_owner=current_user.id, completed="TO-DO")
                db.session.add(new_task)
                db.session.commit()
            except:
                abort(500)
                
        # if user entered a blank name
        
        elif name == "":
            flash("You can not have a blank name")
        return all_tasks()
        #     return "Failed to add new task"
        
    if request.method == "POST" and  counter(current_user.id) >= 10:
        flash('You can not do more than 10 goals a day. You are human not a machine')
        return all_tasks()
    return all_tasks()


# deleting task
@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    if isinstance(task_id, int):
        try:
            task = Task.query.filter_by(id=task_id).first()
            user = User.query.filter_by(id=task.task_owner).first()
            if task:
                db.session.delete(task)    
                if user.progress == 0: 
                    user.progress += 0  # updates user progress as the user proceeds
                elif user.progress > 0:
                    user.progress -= 10
            db.session.commit()
            if tasks == 0: 
                user.progress = 0
        except:
            abort(400)
    else:
       flash("Something went wrong")
    return redirect(url_for('tasks'))


# editing the task
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if request.method == 'GET' and not task:
        abort(404)
    elif request.method == 'GET' and task:
        return render_template('edit_task.html')
    else:
        task.name = request.form.get("name")
        task.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for('tasks'))
    

# changing the status of the task from to-do to completed
@app.route('/mark/<int:task_id>')
@login_required
def mark(task_id):
    # tasks = Task.query.filter_by(task_owner=current_user.id).all()
    # all_tasks()
    task = Task.query.get(task_id)
    if task and task.completed != "COMPLETED":
        task.completed = "COMPLETED"
        current_user.progress += 10
        db.session.commit()
    elif task and task.completed == "COMPLETED":
        return redirect(url_for('tasks'))
    return all_tasks()
    # progress = progress_check(current_user.id)
    # tasks = Task.query.filter_by(task_owner=current_user.id).all()
    # return render_template('tasks.html', tasks=tasks, progress=progress)
    

# checks the progress of the user
@app.route('/progress_check/<int:current_user_id>')
@login_required
def progress_check(current_user_id):
    user  = User.query.filter_by(id=current_user_id).first()
    message = ""
    progression = 100 - user.progress
    if user.progress < 80:
        message += "You still have {} PERCENT left to reach your goal".format(progression)
    elif user.progress >= 80:
            message += "Congratulations! You have reached your goal for the day. Call us for a free drink!"
    return message 


#HELPER METHODS
def user_check(name):
    user_name = User.query.filter_by(nickname=name).first()
    if user_name:
        return True
    return False

def counter(current_user_id):
    try:
        return Task.query.filter_by(task_owner=current_user_id).count()
    except:
        return 0

# this code repeated a lot in the different routes so it was made into a helper function
def all_tasks():
    progress = progress_check(current_user.id)
    tasks = Task.query.filter_by(task_owner=current_user.id).all()
    return render_template('tasks.html', tasks=tasks, progress=progress)



# Handling errors 404, 500, 405, 400 and redirecting to the history.html page
@app.errorhandler(404)
def page_not_found(e):
  
    return render_template('history.html'), 404
    
@app.errorhandler(500)
def page_not_found(e):
  
    return render_template('history.html'), 500

@app.errorhandler(405)
def page_not_found(e):

    return render_template('history.html'), 405

@app.errorhandler(400)
def page_not_found(e):

    return render_template('history.html'), 400


if __name__ =="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

