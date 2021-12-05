import datetime
from flask import Flask
from flask import render_template, request
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_manager, LoginManager, current_user, login_required, login_user, logout_user, UserMixin, user_logged_in
from werkzeug.utils import redirect


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.login_message = "Login to Continue"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(256), unique=True)
    progress = db.Column(db.Integer)
    task =  db.relationship('Task', backref='user', cascade="all, delete-orphan")
        

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    description = db.Column(db.String(256))
    completed = db.Column(db.String(256))
    task_owner = db.Column(db.Integer, db.ForeignKey('user.id'))

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():           
    return render_template('index.html')


#Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("nickname") 
        user_name = User.query.filter_by(nickname=name).first()
    
        if not user_name:
            return redirect(url_for('add_user'))
        login_user(user_name)
        return redirect(url_for('tasks'))
        
    return render_template('login.html')

#add user
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = request.form.get("nickname") 
        if user_check(new_user):
            flash("You already have an account. Please log in")
            return redirect(url_for('login'))
        user = User(nickname=new_user, progress=0)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return "Failed to create new user"
    return render_template('new_user.html')

#logout
@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('index'))


#tasks
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    tasks = Task.query.filter_by(task_owner=current_user.id).all()
    if request.method == "POST" and  counter(current_user) < 10:
        name = request.form.get("name")
        description = request.form.get("description")
        new_task = Task(name=name, description=description, completed="TO-DO", task_owner=current_user.id)
        try:
            db.session.add(new_task)
            db.session.commit()
        except:
            return "Failed to add new task"
    if request.method == "POST" and  counter(current_user) >= 10:
        flash('You can not do more than 10 goals a day. You are human not a machine')
        message = progress_check(current_user.id)
        tasks = Task.query.filter_by(task_owner=current_user.id).all()
        return render_template('tasks.html', tasks=tasks, message=message)
    message = progress_check(current_user.id)
    tasks = Task.query.filter_by(task_owner=current_user.id).all()
    return render_template('tasks.html', tasks=tasks, message=message)

@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
  task = Task.query.filter_by(id=task_id).first()
  
  if task:
    db.session.delete(task)
    if counter(current_user) == 0: 
        current_user.progress = 0
    else:
        current_user.progress -= 10
    
    db.session.commit()
    if tasks == 0: 
        current_user.progress = 0
    return redirect(url_for('tasks'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "POST":
        task.name = request.form.get("name")
        task.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for('tasks'))
    return render_template('edit_task.html')


@app.route('/mark/<int:task_id>')
@login_required
def mark(task_id):
    tasks = Task.query.filter_by(task_owner=current_user.id).all()
    task = Task.query.get_or_404(task_id)
    if task and task.completed != "COMPLETED":
        task.completed = "COMPLETED"
        current_user.progress += 10
        db.session.commit()
        return redirect(url_for('tasks'))
    return render_template('tasks.html', tasks=tasks)

@app.route('/progress_check/<int:current_user_id>')
@login_required
def progress_check(current_user_id):
    current_user_id = current_user.id
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

def counter(current_user):
    tasks = Task.query.filter_by(task_owner=current_user.id).count()
    return tasks



if __name__ =="__main__":
    app.run(debug=True)