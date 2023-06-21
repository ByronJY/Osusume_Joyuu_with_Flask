import json
import sqlite3 as db

DB_PATH = "data.db"

connection = db.connect(DB_PATH)
cursor = connection.cursor()

def print_dict(data):
    pretty = json.dumps(data, indent=4)
    print(pretty)

def db_init():
    try:
        cursor.execute("""CREATE TABLE actresses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name CHAR(100),
                            name_ch CHAR(100),
                            height INT,
                            bust INT,
                            waist INT,
                            hips INT,
                            cup_r CHAR(5),
                            cup_l CHAR(5),
                            info CHAR(255),
                            url_youtube CHAR(255),
                            url_twitter CHAR(255),
                            url_instagram CHAR(255),
                            rank INT,
                            tags_table CHAR(50),
                            img_url CHAR(255)
                        );""")
        connection.commit()
    except:
        pass

    try:
        cursor.execute("""CREATE TABLE tags(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tag CHAR(100)
                        );""")
        connection.commit()
    except:
        pass

    try:
        cursor.execute(f"""CREATE TABLE cups (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       cup CHAR(5));""")
        connection.commit()
    except:
        pass

def read_json(file: str):
    with open(file, "r", encoding="UTF-8") as f:
        data = json.load(f)
        # print(data)
        return data
    
def get_cup_id(cup: str):
    if cup == "AA":
        return 0
    elif cup == "":
        return -1
    else:
        return ord(cup) - (ord('A')-1)
def insert_actress(id:int, actress: dict):
    # print("id: "+str(id))
    # print_dict(actress)

    cup_r, cup_l = -1, -1
    if len(actress["cup"]) == 2:
        cup_r = get_cup_id(actress["cup"][0])
        cup_l = get_cup_id(actress["cup"][1])
    else:
        if actress["cup"][0] != '':
            cup_r, cup_l = get_cup_id(actress["cup"][0]), get_cup_id(actress["cup"][0])


    # print(id, actress["name"], actress["name_ch"], actress["height"], actress["measurements"][0], actress["measurements"][1], actress["measurements"][2], actress["cup"], cup_r, cup_l, actress["info"], actress["sns"]["youtube"], actress["sns"]["twitter"], actress["sns"]["instagram"], actress["rank"], actress["tag"], actress["img"], "\n")

    actress_tags_table = f"actress{str(id)}_tags"
    cursor.execute(f"""CREATE TABLE {actress_tags_table} (id INT)""")
    connection.commit()

    for tag_id in actress["tag"]:
        # print("ID: ", id, tag_id)
        cursor.execute(f"""INSERT INTO tag{str(tag_id)} (id) VALUES ({str(id)})""")
        connection.commit()
        cursor.execute(f"""INSERT INTO {actress_tags_table} (id) VALUES ({tag_id})""")
        connection.commit()

    cursor.execute(f"""INSERT INTO actresses (
                            id,
                            name,
                            name_ch,
                            height,
                            bust,
                            waist,
                            hips,
                            cup_r,
                            cup_l,
                            info,
                            url_youtube,
                            url_twitter,
                            url_instagram,
                            rank,
                            tags_table,
                            img_url) 
                            VALUES(
                                {id},
                                '{actress["name"]}',
                                '{actress["name_ch"]}',
                                {actress["height"]},
                                {actress["measurements"][0]},
                                {actress["measurements"][1]},
                                {actress["measurements"][2]},
                                {cup_r},
                                {cup_l},
                                '{actress["info"]}',
                                '{actress["sns"]["youtube"]}',
                                '{actress["sns"]["twitter"]}',
                                '{actress["sns"]["instagram"]}',
                                {actress["rank"]},
                                '{actress_tags_table}',
                                '{actress["img"]}'
                            )
                    """)
    
    connection.commit()

    cursor.execute(f"""CREATE TABLE actress{id}_comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        uid INT,
                        comment TEXT
                        );""")
    connection.commit()

    
def actresses_init():
    data = read_json("actresses.json")
    # print(data)
    for id in data.keys():
        insert_actress(id, data[id])

def insert_tag(id, data):
    # print(id, data)
    cursor.execute(f"""INSERT INTO tags (id, tag) 
                            VALUES ({id}, '{data}')""")
    connection.commit()

    cursor.execute(f"""CREATE TABLE tag{str(id)} (id INT)""")
    connection.commit()

def tags_init():
    data = read_json("tags.json")
    # print_dict(data)
    for id in data.keys():
        insert_tag(id, data[id])


def cups_init():
    cursor.executemany("""INSERT INTO cups (id, cup)
                                VALUES (?, ?)""",
                                [(-1, "N/A"), (0, "AA")])
    connection.commit()

    # cursor.execute("""INSERT INTO cups (id, cup)
    #                             VALUES (0, 'AA')""")
    # connection.commit()

    for id in range(26):
        # print(chr( ord('A')+id ))
        cursor.execute(f"""INSERT INTO cups (id, cup)
                                    VALUES ({id+1}, '{chr( ord('A')+id )}' );""")
        connection.commit()



if __name__ == "__main__":
    db_init()
    cups_init()
    tags_init()
    actresses_init()
    



connection.close()