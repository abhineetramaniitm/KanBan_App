from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
from datetime import date
from matplotlib import use
from os import path

use("Agg")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban_database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

global cur_user


class User(db.Model):
    __tablename__ = "User"
    sl_no = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Card(db.Model):
    __tablename__ = "Card"
    ID = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Name = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, db.ForeignKey("User.username"), nullable=False)


class Task(db.Model):
    __tablename__ = "Task"
    Title = db.Column(db.String, primary_key=True)
    Content = db.Column(db.String, nullable=False)
    Deadline = db.Column(db.String, nullable=False)
    C_Flag = db.Column(db.String, nullable=False)
    C_Date = db.Column(db.String, nullable=False)
    Card_id = db.Column(db.Integer, db.ForeignKey("Card.ID"), nullable=False)


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    global cur_user
    if request.method == "GET":
        return render_template("login_page.html", error=None)

    if request.method == "POST":
        cur_user = request.form["username"]
        password = request.form["pd"]
        login_detail = User.query.all()

        for i in login_detail:
            if i.username == cur_user and i.password == password:
                return redirect("/home")
        error = "Username or Password is incorrect."
        return render_template("login_page.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    global cur_user
    if request.method == "GET":
        return render_template("signup_page.html")
    if request.method == "POST":
        cur_user = request.form["username"]
        password = request.form["pd"]
        login_id = User(username=cur_user, password=password)
        db.session.add(login_id)
        db.session.commit()
        return redirect("/login")


@app.route("/home", methods=["GET"])
def home():
    global cur_user
    user = cur_user
    card_task = Card.query.filter_by(username=user).all()
    card_name, card_id, count,c_task = [], [], 1, 0
    ctask = Task.query.all()
    for i in card_task:
        card_name.append(i.Name)
        card_id.append(i.ID)
        count += 1
        tmp_task = Task.query.filter_by(Card_id=i.ID).all()
        c_task = 0
        for j in tmp_task:
            c_task += 1
    if c_task > 0:
        return render_template("home.html", clist=ctask, card_list=card_task, card_name=card_name, username=user)
    elif c_task == 0 and count > 1:
        return render_template("home_noList.html", card_list=card_task, username=user)
    else:
        if request.method == "GET":
            return render_template("home_noCard.html", username=user)


@app.route("/home/create_Task", methods=["GET", "POST"])
def create_task():
    global cur_user
    user = cur_user
    if request.method == "GET":
        card = Card.query.filter_by(username=user).all()
        return render_template("Create_list.html", card=card, username=user)
    elif request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        deadline = request.form["deadline"]
        c_flag = request.form.getlist("c_flag")
        card_id = request.form.__getitem__("card")
        flag = "no"
        C_date = ""
        for cf in c_flag:
            if cf == "C_1":
                flag = "yes"
                C_date = str(date.today())
        tmp_Task = Task(Title=title, Content=content, Deadline=deadline, C_Flag=flag, Card_id=card_id, C_Date=C_date)
        db.session.add(tmp_Task)
        db.session.commit()
        return redirect("/home")


@app.route("/home/create_card", methods=["GET", "POST"])
def create_Card():
    global cur_user
    username = cur_user
    if request.method == "GET":
        return render_template("Create_card.html", username=username)
    elif request.method == "POST":
        name = request.form["name"]
        tmp_id = request.form["id"]
        card = Card(Name=name, ID=int(tmp_id), username=username)
        db.session.add(card)
        db.session.commit()
        return redirect("/home")


@app.route("/home/<int:card_id>/delete_card", methods=["GET", "POST"])
def delete_card(card_id):
    global cur_user
    user = cur_user
    tmp_card = Card.query.filter_by(ID=card_id, username=user).first()
    if tmp_card is not None:
        tmp_Task = Task.query.filter_by(Card_id=card_id).all()
        for obj in tmp_Task:
            db.session.delete(obj)
    card = Card.query.filter_by(ID=card_id, username=user).one()
    db.session.delete(card)
    db.session.commit()
    return redirect("/home")


@app.route("/home/<int:card_id>/update_card", methods=["GET", "POST"])
def update_card(card_id):
    global cur_user
    user = cur_user
    if request.method == "GET":
        return render_template("Update_card.html", card_id=card_id, username=user)
    if request.method == "POST":
        name = request.form["name"]
        tmp_card = Card.query.filter_by(ID=card_id, username=user).one()
        tmp_card.Name = name
        db.session.commit()
        return redirect("/home")


@app.route("/home/update_card/update_list", methods=["GET", "POST"])
def update_Task():
    global cur_user
    user = cur_user
    card = Card.query.filter_by(username=user).all()
    if request.method == "GET":
        return render_template("Update_list.html", card=card, error=None)
    if request.method == "POST":
        card_id = request.form.__getitem__("card")
        title = request.form["title"]
        content = request.form["content"]
        c_flag = request.form.getlist("c_flag")
        flag="no"
        C_date=""
        for cf in c_flag:
            if cf == "C_1":
                flag = "yes"
                C_date = str(date.today())
        tmp_Task = Task.query.filter_by(Card_id=card_id, Title=title).one()
        if tmp_Task is not None:
            tmp_Task.Content = content
            tmp_Task.C_flag = flag
            tmp_Task.C_Date = C_date
            db.session.commit()
            return redirect("/home")
        if tmp_Task is None:
            error = "Title not found!!! Enter a valid title"
            return render_template("Update_list.html", card=card, error=error)


@app.route("/home/move_task", methods=["GET", "POST"])
def move_Task():
    global cur_user
    user = cur_user
    card = Card.query.filter_by(username=user).all()
    task = []
    for c in card:
        task += Task.query.filter_by(Card_id=c.ID).all()
    if request.method == "GET":
        return render_template("move_task.html", task=task, card=card, username=user)
    if request.method == "POST":
        title = request.form.__getitem__("title")
        card_id = request.form.__getitem__("card")
        tmp_task = Task.query.filter_by(Title=title).one()
        if tmp_task is not None:
            tmp_task.Card_id = card_id
            db.session.commit()
            return redirect("/home")

@app.route("/home/<int:card_id>/update_card/<string:title>/delete_list", methods=["GET", "POST"])
def delete_Task(card_id,title):
    tmp_Task = Task.query.filter_by(Card_id=card_id, Title=title).all()
    for obj in tmp_Task:
        db.session.delete(obj)
    db.session.commit()
    return redirect("/home")


@app.route("/home/summary", methods=["GET"])
def summary():
    global cur_user
    user = cur_user
    recl = []
    l=[]
    countl = []
    card = Card.query.filter_by(username=user).all()
    for i in card:
        tmp_Task = Task.query.filter_by(Card_id=i.ID).all()
        count, rec = 0, 0
        l=[]
        for j in tmp_Task:
            rec += 1
            if j.C_Flag == "yes":
                count += 1
                l.append(j.C_Date)
        countl.append(count)
        recl.append(rec)
    plt.hist(l)
    plt.xlabel("date")
    plt.ylabel("No. of Completed Tasks")
    plt.savefig("static/graph.png")
    return render_template("summary.html", rec=recl, count=countl, card_list=card, username=user)


@app.route("/home/logout", methods=["GET"])
def logout():
    return redirect("/login")


if __name__ == '__main__':
    app.debug = True
    app.run()
