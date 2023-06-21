import json
import os
from flask import Flask, render_template, request, session, g, redirect, url_for
from library.db_ctl import *
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = os.urandom(24)

def read_json(file):
    with open(file, "r", encoding="UTF-8") as f:
        data = json.load(f)
        # print(data)
        return data

@app.before_request
def before_request():
    # print(request.url)
    print("Before request")
    get_db()

@app.after_request
def after_request(response):
    close_db()
    print('After request finished')
    print(request.url)
    response.headers['key'] = 'value'
    return response


@app.route('/')
def home():
    return redirect(url_for("actresses"))

def is_login():
    user=None
    if "user" in session:
        user=session["user"]["name"]
    return user

@app.route('/actresses', methods=["GET"])
def actresses():
    user=is_login()
    
    tags=request.args.getlist("tags[]")
    sort=request.args.get("sort")
    if len(tags) == 0:
        # print("\nNNN\n")
        return render_template('home/actresses.html', user=user, sort=sort, tags=db_get_tags(), actresses=db_get_actresses(order=sort))
    else:
        tags=list(map(int, tags))
        # print("\n", tags, "\n")
        # print(db_get_tags_filter(tags))

    # for actress in db_get_actresses():
    #     for data in actress:
    #         print(data, end=" ")
    #     print("\n")

        return render_template('home/actresses.html', user=user, sort=sort, selected_tags=tags, tags=db_get_tags(), actresses=db_get_actresses(tag_ids=tags, order=sort))

@app.route("/actress/<id>")
def actress(id):
    user=is_login()
    is_favorite=False
    if is_login():
        is_favorite=db_is_in_favorate(session["user"]["id"], id)
    return render_template("actress/actress.html", user=user, actress=db_get_actress(id), tags=db_get_actress_tags(id), favorite=is_favorite, comments=db_get_comments(id))

@app.route("/login", methods=["GET", "POST"])
def login():
    # session.pop("user", None)

    if request.method == "POST":
        

        email = request.form.get("email")
        password = request.form.get("password")
        user = db_user_login(email, password)

        if user == -1:
            return f"<div style=\"font-weight: bold; color: red;\">Name or password incorrect</div>" + render_template("login.html")
        else:
            session["user"] = {"id": user[0], "name": user[2]}
            # session["user"]["id"] = user[0]
            # session["user"]["name"] = user[2]
            return redirect(url_for("actresses"))
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("home"))

@app.route("/sign_up", methods=["GET", "POST"])
def signUp():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        db_sign_up(name, email, password)
        return redirect(url_for("login"))
        # return name +"<br>"+ password +"<br>"+ student_id +"<br>"+ phone
    else:
        return render_template("signUp.html")
    
@app.route("/my_info")
def myInfo():
    if "user" in session:
        uid = session["user"]["id"]
        user = db_get_user_info(uid)
        favorites=db_get_favorite_actresses(uid)
        for actress in favorites:
            for data in actress:
                print(data, end=" ")
            print("\n")
        return render_template("my_info/my_info.html", user=user[1], id=user[0], name=user[1], email=user[2], actresses=favorites)
    else:
        return redirect(url_for("login"))
    
# @app.route("/sql_tables")
# def showTables():
#     return db_show_tables()

# @app.route("/sql_users")
# def showUsers():
#     return db_show_users()

# @app.route("/drop_table/<table>")
# def dropTable(table):
#     return db_drop_table(table)
    
@app.route("/favorate", methods=["GET"])
def favorate():
    user=is_login()

    if user != None:
        uid=session["user"]["id"]
        # print("\n", {session["user"]["id"]}, "\n")
        id=request.args["id"]
        # print("\nFavorate", id, "\n")
        is_favorate=db_is_in_favorate(uid, id)
        # print(f"\n{is_favorate}\n")
        if is_favorate:
            db_remove_favorite(uid, id)
        else:
            db_add_favorite(uid, id)
        return redirect(url_for('actress', id=id))
    else:
        return redirect(url_for("login"))

@app.route("/comment", methods=["POST"])
def comment():
    uid = session["user"]["id"]
    aid=request.form.get('actress_id')
    comment=request.form.get('comment')
    
    if len(comment) is not 0:
        print("\n", aid, comment, "\n")
        db_add_comment(uid=uid, aid=aid, comment=comment)
    return redirect(url_for('actress', id=aid))
