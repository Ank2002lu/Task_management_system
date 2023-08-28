from flask_mysqldb import MySQL
from flask import Flask, request,render_template,redirect,url_for,session,abort,flash
from datetime import datetime,date
from flask_session import Session
from functools import wraps
app = Flask(__name__)

# Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'server123'
MYSQL_DB = 'taskmng'

app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_DB'] = MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL()
# Initialize the extension
mysql.init_app(app)

app.config['SECRET_KEY'] = 'thisisasecret'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

def admin_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get("id") or session.get("type") == "user":
            return abort(403)
        return func(*args, **kwargs)

    return decorated_function

@app.route('/', methods=['GET'])
def home():
    cur = mysql.connection.cursor()
    user = None
    admin = None
    if session.get("id") and session.get("type")=="user":
        uid = session.get("id")
        cur.execute(f"select * from user where U_id = {uid}")
        user = cur.fetchone()
    elif session.get("id") and session.get("type")=="admin":
        aid = session.get("id")
        cur.execute(f"select * from admin where a_id = {aid}")
        admin = cur.fetchone()
    return render_template("index.html",user=user,admin=admin,)

#admin route
@app.route("/admin",methods=["GET"])
@admin_only
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin")
    admin = cur.fetchall()
    return render_template("admin/admin.html",admin=admin)

@app.route("/admin/update/<int:admin_id>",methods=["GET","POST"])
def update_admin(admin_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        a_name = request.form.get("name")
        a_email = request.form.get("email")
        a_status = request.form.get("status")
        a_gender = request.form.get("gender")
        cur.execute("UPDATE admin SET a_name = %s,a_email = %s,a_status =%s,a_gender=%s WHERE a_id = %s",(a_name,a_email,a_status,a_gender,admin_id))
        mysql.connection.commit()
        return redirect(url_for("users"))
    cur.execute(f"SELECT * FROM admin where a_id = {admin_id}")
    admin = cur.fetchone()   
    return render_template("admin/update_admin.html",admin = admin)

#admin/users
@app.route("/admin/user",methods=["GET"])
def users():
    admin_id=session.get("id")
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM user WHERE U_a_id={admin_id}")
    users = cur.fetchall()
    return render_template("admin/admin_user.html",users=users,admin_id=admin_id)


@app.route("/admin/user/add",methods=["GET","POST"])
def add_user():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        U_name = request.form.get("name")
        U_email = request.form.get("email")
        U_password = request.form.get("password")
        U_status = request.form.get("status")
        U_gender = request.form.get("gender")
        admin_id = session.get("id")
        cur.execute("INSERT INTO user (U_name,U_email,U_password,U_status,U_gender,U_a_id) VALUES (%s,%s,%s,%s,%s,%s)",(U_name,U_email,U_password,U_status,U_gender,admin_id))
        mysql.connection.commit()
        return redirect(url_for("users",admin_id=admin_id))
    return render_template("admin/user_add.html")

@app.route("/admin/<int:admin_id>/user/update/<int:user_id>",methods=["GET","POST"])
def update_user(user_id,admin_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        U_name = request.form.get("name")
        U_email = request.form.get("email")
        U_status = request.form.get("status")
        U_gender = request.form.get("gender")
        cur.execute("UPDATE user SET U_name = %s,U_email = %s,U_status =%s,U_gender=%s WHERE U_id = %s AND U_a_id=%s",(U_name,U_email,U_status,U_gender,user_id,admin_id))
        mysql.connection.commit()
        return redirect(url_for("users",admin_id=admin_id))
    cur.execute(f"SELECT * FROM user where U_id = {user_id}")
    user = cur.fetchone()   
    return render_template("admin/user_update.html",user = user,admin_id=admin_id) 

@app.route("/admin/<int:admin_id>/user/delete/<int:user_id>",methods=["GET"])
def delete_user(user_id,admin_id):
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE from user where U_id ={user_id} AND U_a_id={admin_id}")
    mysql.connection.commit()
    return redirect(url_for("users",admin_id=admin_id,user_id=user_id))

@app.route("/admin/project",methods=["GET"])
def project():
    cur = mysql.connection.cursor()
    admin_id = session.get("id")
    cur.execute(f"SELECT * from project WHERE a_id={admin_id}")
    projects=cur.fetchall()
    return render_template("admin/projects_disp.html",projects=projects)
#ADMIN PROJECT
@app.route("/admin/project/add/",methods=["GET","POST"])
def add_project():
    cur = mysql.connection.cursor()
    admin_id = session.get("id")
    if request.method == "POST":
        P_name = request.form.get("name")
        P_status = request.form.get("status")
        P_desc = request.form.get("desc")
        cur.execute("INSERT INTO project (P_name,P_status,P_desc,a_id) VALUES (%s,%s,%s,%s)",(P_name,P_status,P_desc,admin_id))
        mysql.connection.commit()
        return redirect(url_for("project"))
    return render_template("admin/admin_projects.html",admin_id=admin_id)

@app.route("/admin/project/update/<int:project_id>",methods=["GET","POST"])
def update_project(project_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        P_name = request.form.get("P_name")
        P_status = request.form.get("P_status")
        P_desc = request.form.get("P_desc")
        cur.execute("UPDATE project SET P_name = %s,P_status = %s,P_desc =%s WHERE P_id = %s",(P_name,P_status,P_desc,project_id))      
        mysql.connection.commit()
        return redirect(url_for("project"))
    cur.execute(f"SELECT * FROM project where P_id = {project_id}")
    proj = cur.fetchone()   
    return render_template("admin/admin_update_proj.html",proj = proj)  

@app.route("/admin/project/delete/<int:project_id>",methods=["GET"])
def delete_project(project_id):
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE from project where P_id ={project_id}")
    mysql.connection.commit()
    return redirect(url_for("project"))

#admin/project/task

@app.route("/admin/project/<int:project_id>/task",methods=["GET"])
def task(project_id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM task WHERE T_P_id= {project_id }")
    task = cur.fetchall()
    return render_template("admin/tasks_disp.html",task=task)

@app.route("/admin/<int:admin_id>/project/<int:project_id>/task/add",methods=["GET","POST"])
def add_task(admin_id,project_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        T_name = request.form.get("name")
        T_deadline = request.form.get("deadline")
        T_status = request.form.get("status")
        deadlineDate = datetime.strptime(T_deadline,"%Y-%m-%d").date()
        startDate = date.today()
        if deadlineDate>=startDate:
            cur.execute("INSERT INTO task (T_name,T_deadline,T_status,T_P_id,a_id) VALUES (%s,%s,%s,%s,%s)",(T_name,T_deadline,T_status,project_id,admin_id))
            mysql.connection.commit()
            return redirect(url_for("project"))
        else:
            flash("<DEADLINE MSG>")
    return render_template("admin/add_task.html",project_id=project_id,admin_id=admin_id)

@app.route("/admin/assign/<int:task_id>",methods=["GET","POST"])
def assign_task(task_id):
    cur = mysql.connection.cursor()
    admin_id = session.get("id")
    if request.method == "POST":
        users = request.form.getlist('users')
        for user in users:
            cur.execute(f"INSERT into user_task values ({user},{task_id})")
        mysql.connection.commit()
        cur.execute(f"select Task_id, T_P_id from task where Task_id={task_id}")
        task = cur.fetchone()
        project_id = task["T_P_id"]
        return redirect(url_for("task",project_id=project_id))
    cur.execute(f"SELECT * from user where U_a_id={admin_id}")
    users = cur.fetchall()
    return render_template("admin/add_user_task.html",users = users,task_id=task_id,admin_id=admin_id)


@app.route("/admin/project/<int:project_id>/update/task/<int:task_id>",methods=["GET","POST"])
def update_task(project_id,task_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        T_name = request.form.get("T_name")
        T_date = request.form.get("T_date")
        T_deadline = request.form.get("T_deadline")
        T_status = request.form.get("status")
        deadlineDate = datetime.strptime(T_deadline,"%Y-%m-%d").date()
        startDate = date.today()
        if deadlineDate>=startDate:
            cur.execute("UPDATE task SET T_name = %s,T_date = %s,T_deadline =%s,T_status=%s WHERE T_P_id = %s AND Task_id = %s",(T_name,T_date,T_deadline,T_status,project_id,task_id))
            mysql.connection.commit()
            return redirect(url_for("task",project_id=project_id))
        else:
            flash("Dealine Date cannot be before the Start Date")
    cur.execute(f"SELECT * FROM task where Task_id = {task_id} AND T_P_id = {project_id}")
    tsk = cur.fetchone()   
    return render_template("admin/task_update.html",tsk=tsk)


@app.route("/admin/project/<int:project_id>/delete/task/<int:task_id>",methods=["GET"])
def delete_task(project_id,task_id):
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE from task where T_P_id= {project_id} AND Task_id ={task_id}")
    mysql.connection.commit()
    return redirect(url_for("project"))


@app.route("/admin/<int:admin_id>/projects/tasks/<int:task_id>/comment",methods=["GET"])
def comment(admin_id, task_id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM comments WHERE Task_id={task_id}")
    comment = cur.fetchall()
    return render_template("admin/cmt_disp.html",comment=comment,admin_id=admin_id,task_id=task_id)

@app.route("/admin/projects/tasks/<task_id>/comment/add",methods=["GET","POST"])
def add_comment(task_id):
    cur = mysql.connection.cursor()
    admin_id = session.get("id")
    if request.method == "POST":
        cur.execute(f"SELECT a_name from admin where a_id = {admin_id}")
        name = cur.fetchone()["a_name"]
        C_by = name
        C_to = request.form.get("C_to")
        C_time = request.form.get("C_time")
        C_text = request.form.get("C_text")
        admin_id = session.get("id")
        cur.execute("INSERT INTO comments (C_by,C_to,C_time,C_text,Task_id,a_id) VALUES (%s,%s,%s,%s,%s,%s)",(C_by,C_to,C_time,C_text,task_id,admin_id))
        mysql.connection.commit()
        return redirect(url_for("comment",admin_id=admin_id,task_id=task_id))
    return render_template("admin/task_cmt.html",task_id = task_id)

@app.route("/admin/projects/tasks/<task_id>/delete/comment/<int:Comment_id>",methods=["GET"])
def delete_comment(task_id,Comment_id):
    cur = mysql.connection.cursor()
    admin_id = session.get("id")
    cur.execute(f"DELETE from comments where Task_id= {task_id} AND C_id ={Comment_id} AND a_id={admin_id}")
    mysql.connection.commit()
    return redirect(url_for("comment",task_id=task_id,admin_id=admin_id))

#User

@app.route("/user/project/",methods=["GET"])
def user_project():
    cur = mysql.connection.cursor()
    user_id = session.get("id")
    cur.execute(f'''select * 
 from user_task,task,project 
 where user_task.U_id = {user_id} 
 and user_task.Task_id = task.Task_id
 and project.P_id = task.T_P_id;
''')
    projects = cur.fetchall()
    for project in projects:
        print(project) 
    return render_template("User/user_project.html",projects=projects)

@app.route("/user/project/tasks",methods=["GET"])
def user_task():
    cur = mysql.connection.cursor()
    user_id = session.get("id")
    cur.execute(f"SELECT * FROM task,user_task,user WHERE task.Task_id = user_task.Task_id AND user.U_id=user_task.U_id AND user.U_id={user_id}")
    project = cur.fetchall()
    return render_template("User/user_tasks.html",project=project)
#user_task_update

@app.route("/user/project/task/update/<int:task_id>",methods=["GET","POST"])
def user_update_task(task_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        T_status = request.form.get("T_status")
        cur.execute(f"UPDATE task SET T_status = %s WHERE Task_id = %s",(T_status,task_id) )
        mysql.connection.commit()
        return redirect(url_for("user_task"))
    cur.execute(f"SELECT * FROM task where Task_id = {task_id}")
    tsk=cur.fetchone()
    return render_template("user/user_task_update.html",task_id=task_id,tsk=tsk)

@app.route("/user/<int:user_id>/projects/tasks/<int:task_id>/comment",methods=["GET"])
def user_comment(task_id,user_id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM comments WHERE Task_id={task_id}")
    comments = cur.fetchall()
    return render_template("User/user_comment_disp.html",comments=comments,task_id=task_id,user_id=user_id)

@app.route("/user/projects/tasks/<task_id>/comment/add",methods=["GET","POST"])
def user_add_comment(task_id):
    cur = mysql.connection.cursor()
    user_id = session.get("id")
    if request.method == "POST":
        cur.execute(f"SELECT U_name from user where U_id = {user_id}")
        name = cur.fetchone()["U_name"]
        C_by = name
        C_to = request.form.get("C_to")
        C_time = request.form.get("C_time")
        C_text = request.form.get("C_text")
        cur.execute("INSERT INTO comments (C_by,C_to,C_time,C_text,Task_id,U_id) VALUES (%s,%s,%s,%s,%s,%s)",(C_by,C_to,C_time,C_text,task_id,user_id))
        mysql.connection.commit()
        return redirect(url_for("user_comment",user_id=user_id,task_id=task_id))
    return render_template("user/user_comment.html",task_id=task_id)

@app.route("/user/projects/tasks/<task_id>/delete/comment/<int:Comment_id>",methods=["GET"])
def user_delete_comment(task_id,Comment_id):
    cur = mysql.connection.cursor()
    user_id = session.get("id")
    cur.execute(f"DELETE from comments where Task_id= {task_id} AND C_id ={Comment_id} AND U_id={user_id}")
    mysql.connection.commit()
    return redirect(url_for("user_comment",task_id=task_id,Comment_id=Comment_id,user_id=user_id))

#login-Register-logout
@app.route('/login', methods=["GET", "POST"])
def login():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cur.execute(f"select * from user where U_email = '{email}'")
        user = cur.fetchone()
        if user and user["U_password"] == password:
            session["id"] = user["U_id"]
            session["type"] = "user"
            return redirect(url_for("home"))
    return render_template("auth/login.html")

@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email)
        print(password)
        cur.execute(f"select * from admin where A_email = '{email}'")
        admin = cur.fetchone()
        if admin and admin["a_password"] == password:
            session["id"] = admin["a_id"]
            session["type"] = "admin"
            return redirect(url_for("home"))
    return render_template("auth/admin_login.html")

@app.route("/logout")
def logout():
    session["id"] =None
    session["type"] =None
    return redirect(url_for('home'))

@app.route("/admin/register",methods=["GET","POST"])
def admin_register():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        a_name = request.form.get("name")
        a_email = request.form.get("email")
        a_password = request.form.get("password")
        a_status = request.form.get("status")
        a_gender = request.form.get("gender")


        cur.execute("INSERT INTO admin (a_name,a_email,a_password,a_status,a_gender) VALUES (%s,%s,%s,%s,%s)",(a_name,a_email,a_password,a_status,a_gender))
        mysql.connection.commit()
        return redirect(url_for("home"))
    return render_template("auth/admin_register.html")


@app.route("/tasklist")
def tasklist():
    cur = mysql.connection.cursor()
    user_id = request.args.get("user_id")
    if not user_id:
        user_id = session.get("id")
    cur.execute(f"SELECT * from task,user_task where T_Status = 'Completed' and task.Task_id=user_task.Task_id  and user_task.U_id={user_id}")
    completed_tasks = cur.fetchall()
    cur.execute(f"SELECT * from task,user_task where T_Status = 'In Progress' and task.Task_id=user_task.Task_id  and user_task.U_id={user_id}")
    inprogress_tasks = cur.fetchall()
    cur.execute(f"SELECT * from task,user_task where T_Status = 'Assigned' and task.Task_id=user_task.Task_id  and user_task.U_id={user_id} ")
    assigned_tasks = cur.fetchall()
    return render_template("User/user_task_list.html",completed_tasks=completed_tasks,inprogress_tasks=inprogress_tasks,assigned_tasks=assigned_tasks)

if __name__ == '__main__':
    app.run(debug=True)