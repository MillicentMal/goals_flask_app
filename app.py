import datetime
from flask import Flask
from flask import render_template, request
from flask.helpers import url_for
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
    time_created = db.Column(db.DateTime)
    description = db.Column(db.String(256))
    completed = db.Column(db.Boolean)
    task_owner = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if user_logged_in:
        return redirect(url_for('tasks'))
    if request.method == 'POST':
        name = request.form.get("nickname") 
        
        user_name = User.query.filter_by(nickname=name).first()
        if not user_name:
            new_user = User(nickname=name, progress=0)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('tasks'))
            except:
                return "Failed to create user"
        else:
            return redirect(url_for('tasks'))
            
    return render_template('index.html')


    
    
    
    
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        time_created = datetime.datetime.today()
        
        
        new_task = Task(name=name, description=description, completed=False, time_created=time_created.date(), task_owner=current_user.id)
        try:
            db.session.add(new_task)
            db.session.commit()
        except:
            return "Failed to add new task"
    tasks = Task.query.filter_by(task_owner=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

if __name__ =="__main__":
    app.run(debug=True)