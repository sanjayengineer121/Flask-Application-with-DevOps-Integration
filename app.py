from flask import Flask,render_template,redirect,url_for,request,jsonify,session
import sqlite3,datetime
from pytz import utc
from time import gmtime, strftime
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import jwt
import json

app=Flask(__name__)
app.secret_key = 'flasktodotask'  
secret_key='flasktodotask'  

global tokenid

def create_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, status TEXT NOT NULL, datetime TEXT NOT NULL,auther TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()
    
def insert_task(task, status, auther):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    current_datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    c.execute("INSERT INTO tasks (task, status, datetime, auther) VALUES (?, ?, ?, ?)", (task, status, current_datetime, auther))
    conn.commit()
    conn.close()

def insert_userdata(username,email,password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    hashed_password = generate_password_hash(password)
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
    conn.commit()
    conn.close()
    
def get_tasks():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id,task,status,auther from tasks")
    tasks = c.fetchall()
    conn.close()
    return tasks
def userdata():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query="""SELECT id,username,email,
        CASE 
            WHEN EXISTS (SELECT 1 FROM tasks WHERE auther = u.username) THEN 'active' 
                ELSE 'inactive' 
            END AS status
        FROM users u;
            """
    c.execute(query)
    tasks = c.fetchall()
    conn.close()
    return tasks


def get_user_by_email(email):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

f = open('token.json','r')

data = json.load(f)
token=data['token']

f.close()

print(token)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):


        


        try:
            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
                
            expiration_time = datetime.datetime.fromtimestamp(decoded_token['exp'])
            current_time = datetime.datetime.utcnow()
            if current_time > expiration_time:
                return redirect(url_for('login', expired=True))
            else:
                print("Token is valid")
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login', expired=True))
        except jwt.InvalidTokenError:
            print("Invalid token")
            
        if 'email' not in session or 'last_activity' not in session:
            return redirect(url_for('login'))
        
        last_activity = session['last_activity']
        now = datetime.datetime.utcnow().replace(tzinfo=utc)  # Make current time timezone-aware
        if now > last_activity + datetime.timedelta(hours=4):
            session.pop('email', None)
            session.pop('last_activity', None)
            return redirect(url_for('login', expired=True))

        session['last_activity'] = now  
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
@login_required
def index():
    tasks=get_tasks()
    return render_template('Dashboard.html',tasks=tasks, username=session['email'])


@app.route('/register',methods=['GET','POST'])
def register():
    return render_template('Signup.html')

@app.route('/teammember')
@login_required
def teammember():
    team_member=userdata()
    return render_template('team_member.html',team_member=team_member,username=session['email'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('index'))  # Redirect to index if already logged in
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and check_password_hash(user[3], password):
            payload = {
                'user_id': user,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=4)  # Token expiry time (1 hour in this example)
            }
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            tokenid=token
            print("Generated JWT token:", token)
            
            import json 
            
            dict1= { 
                  "token": tokenid
                }

            # the json file where the output must be stored 
            out_file = open("token.json", "w") 

            json.dump(dict1, out_file, indent = 6) 

            out_file.close() 

            session['email'] = email
            session['last_activity'] = datetime.datetime.utcnow().replace(tzinfo=utc)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html', expired=request.args.get('expired'))

   

@app.route('/signup', methods=["POST"])
def signup():
    
    username=request.form.get('username')
    eamil=request.form.get('email')
    passw=request.form.get('password')
    passw1=request.form.get('password1')
        
    if passw == passw1:
        insert_userdata(username,eamil,passw)
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('last_activity', None)
    return redirect(url_for('login'))

@app.route('/add_task',methods=['POST'])
def add_task():
    task=request.form.get('task')
    import datetime
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    auther="sanjay"
    status='pending'
    
    if task and auther:
        insert_task(task, status, auther)
    
    print(task)
    print(now)
    
    return redirect(url_for('index'))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM tasks WHERE id=?", (todo_id,))

    conn.commit()

    conn.close()

    return redirect(url_for("index"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute("SELECT status FROM tasks WHERE id = ?", (todo_id,))
    current_status = c.fetchone()[0]
    new_status = 'completed' if current_status == 'pending' else 'pending'
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, todo_id))
    
    conn.commit()
    conn.close()

    
    return redirect(url_for("index"))

@app.route("/modify_task/<int:todo_id>",methods=['POST'])
def modify_task(todo_id):
    new_todo=request.form.get('newtask')
    
    print(new_todo)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = """UPDATE tasks
           SET task = ?
           WHERE id = ?"""
    c.execute(query, (new_todo, todo_id))
    
    conn.commit()
    conn.close()

    return redirect(url_for("index"))
   
create_table()
app.run(debug=True,host='0.0.0.0',port='8058')
