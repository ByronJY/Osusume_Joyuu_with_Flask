import sqlite3 as db
import hashlib
from flask import g, current_app

DB_PATH = "./data/data.db"

def get_db():
    if 'db' not in g:
        g.db = db.connect(
            DB_PATH,
            detect_types=db.PARSE_DECLTYPES
        )
        g.db.row_factory = db.Row

    # return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def db_init():
    connection = db.connect(DB_PATH)
    cursor = connection.cursor()
    try:
        cursor.execute("""CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name CHAR(100),
                email CHAR(100),
                password CHAR(128) );""")
    except:
        pass
    connection.commit()
    connection.close()

def db_sign_up(name, email, password):
    cursor = g.db.cursor()

    password_sha512 = hashlib.sha512(password.encode("utf-8")).hexdigest()

    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password_sha512))
    g.db.commit()

    uid = cursor.execute(f"""SELECT id FROM users
                        WHERE name='{name}' AND email='{email}' AND password='{password_sha512}' """).fetchone()["id"]
    # print("User: ", name, "UID: ", uid)
    cursor.execute(f"""CREATE TABLE user{uid}_favorites (
                        id INT UNIQUE
                        );""")
    g.db.commit()

def db_user_login(email, password):
    cursor = g.db.cursor()
    password_sha512 = hashlib.sha512(password.encode("utf-8")).hexdigest()
    
    ret = cursor.execute(f"""SELECT id, email, name FROM users
                      WHERE email='{email}' AND password='{password_sha512}';""").fetchone()

    g.db.commit()

    if ret != None:
        return ret
    else:
        return -1

def db_get_user_info(id):
    cursor = g.db.cursor()
    ret = cursor.execute(f"""SELECT * FROM users
                            WHERE id='{id}';""").fetchone()

    g.db.commit()

    return ret

def db_get_tags_filter(arr):
    cursor = g.db.cursor()

    tag_tables = []
    for id in arr:
        tag_tables.append(f"tag{id}")
    # print("\n", tag_tables, "\n")

    sql_query = ""
    for table in tag_tables[:-1]:
        sql_query+=f"SELECT * FROM {table} INTERSECT "
    sql_query+=f"SELECT * FROM {tag_tables[-1:][0]}"
    # print("\n", sql_query, "\n")

    ret = cursor.execute(sql_query).fetchall()
    # for r in ret:
    #     for id in r:
    #         print(id)

    if len(ret) is not 0:
        sql_query = " WHERE "

        for result in ret[:-1]:
            sql_query+=f" actresses.id={result['id']} OR "
        sql_query+=f" actresses.id={ret[-1:][0]['id']}"
        # print("\n", sql_query, "\n")
        return sql_query
    else:
        return -1



def db_get_actresses(tag_ids=[], order="rank_desc"):
    cursor = g.db.cursor()
    where_query = ""
    if len(tag_ids):
        where_query = db_get_tags_filter(tag_ids)
    # print("\n", where_query, "\n")
    if where_query == -1:
        return -1

    order_query = ""
    if order == "rank_desc":
        order_query = "ORDER BY actresses.rank DESC"
    elif order == "rank_asc":
        order_query = "ORDER BY actresses.rank ASC"
    elif order == "cup_desc":
        order_query = "ORDER BY actresses.cup_r DESC"
    elif order == "cup_asc":
        order_query = "ORDER BY actresses.cup_r ASC"

    ret = cursor.execute(f"""SELECT *, cr.cup AS r_cup, cl.cup AS l_cup,
                                CASE WHEN cup_r=cup_l
                                    THEN 1
                                    ELSE 0
                                    END AS cups_same
                                from "actresses"
                                INNER JOIN cups AS cr ON actresses.cup_r=cr.id
                                INNER JOIN cups AS cl ON actresses.cup_l=cl.id
                                {where_query}
                                {order_query}""").fetchall()
    g.db.commit()
    return ret

def db_get_actress(id):
    cursor = g.db.cursor()
    ret = cursor.execute(f"""SELECT *, cr.cup AS r_cup, cl.cup AS l_cup,
                                CASE WHEN cup_r=cup_l
                                    THEN 1
                                    ELSE 0
                                    END AS cups_same
                                from "actresses"
                                INNER JOIN cups AS cr ON actresses.cup_r=cr.id
                                INNER JOIN cups AS cl ON actresses.cup_l=cl.id
                                WHERE actresses.id={id}""").fetchone()
    g.db.commit()
    return ret

def db_get_favorite_actresses(uid):
    cursor = g.db.cursor()
    ret = cursor.execute(f"""SELECT *, cr.cup AS r_cup, cl.cup AS l_cup,
                                CASE WHEN cup_r=cup_l
                                    THEN 1
                                    ELSE 0
                                    END AS cups_same
                                from "actresses"
                                INNER JOIN cups AS cr ON actresses.cup_r=cr.id
                                INNER JOIN cups AS cl ON actresses.cup_l=cl.id
                                INNER JOIN user{uid}_favorites ON actresses.id=user{uid}_favorites.id
                                """).fetchall()
    g.db.commit()

    return ret



def db_get_actress_tags(id):
    cursor = g.db.cursor()
    ret = cursor.execute(f"""SELECT * FROM actress{id}_tags
                                JOIN tags ON actress{id}_tags.id=tags.id""").fetchall()
    g.db.commit()
    return ret

def db_get_tags():
    cursor = g.db.cursor()
    ret = cursor.execute("SELECT * FROM tags").fetchall()
    g.db.commit()
    return ret

def db_show_tables():
    cursor = g.db.cursor()
    ret = cursor.execute("""SELECT name FROM sqlite_master
                            WHERE TYPE='table' ORDER BY name""").fetchall()

    g.db.commit()
    return ret

def db_show_users():
    cursor = g.db.cursor()
    ret = cursor.execute("SELECT * FROM users ORDER BY name").fetchall()

    g.db.commit()
    return ret

def db_drop_table(table):
    cursor = g.db.cursor()
    cursor.execute(f"DROP TABLE {table}")
    ret = cursor.execute("""SELECT name FROM sqlite_master
                            WHERE TYPE='table' ORDER BY name""").fetchall()

    g.db.commit()
    return ret

def db_is_in_favorate(uid, aid):
    cursor = g.db.cursor()
    ret = cursor.execute(f"""SELECT id FROM user{uid}_favorites
                                WHERE id={aid}""").fetchone()

    g.db.commit()

    # print("\n", f"Is {uid}\'s favorate: ", ret, "\n")
    if ret is None:
        return False
    else:
        return True
    
def db_add_favorite(uid, aid):
    cursor = g.db.cursor()
    cursor.execute(f"""INSERT INTO user{uid}_favorites (id)
                                                    VALUES ({aid})""")
    g.db.commit()

def db_remove_favorite(uid, aid):
    cursor = g.db.cursor()
    cursor.execute(f"""DELETE FROM user{uid}_favorites
                                WHERE id={aid}""")

    g.db.commit()

def db_add_comment(uid, aid, comment):
    cursor = g.db.cursor()
    cursor.execute(f"""INSERT INTO actress{aid}_comments (uid, comment)
                                                VALUES ({uid}, '{comment}')""")
    g.db.commit()

def db_get_comments(aid):
    cursor = g.db.cursor()
    ret = cursor.execute(f"""SELECT actress{aid}_comments.id, actress{aid}_comments.uid, users.name, actress{aid}_comments.comment
                                FROM actress{aid}_comments
                                JOIN users ON actress{aid}_comments.uid=users.id
                                """).fetchall()

    g.db.commit()

    return ret