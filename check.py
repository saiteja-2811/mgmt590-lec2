dict_1 = {
"name": "distilled-bert",
"tokenizer": "distilbert-base-uncased-distilled-squad",
"model": "distilbert-base-uncased-distilled-squad"
}

dict_2 = {
"name": "deepset-roberta",
"tokenizer": "deepset/roberta-base-squad2",
"model": "deepset/roberta-base-squad2"
}
model_list = []
model_list.append(dict_1)
model_list.append(dict_2)

import sqlite3

try:
    sqliteConnection = sqlite3.connect('SQLite_Python.db')
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    sqlite_drop_query = """drop table model_details"""

    sqlite_create_Query = """ create table model_details(
                                timestamp int primary key not null,
                                model text,
                                name text,
                                tokenizer text
                            );
                                """
    v1 = 1234567
    v2 = 'model1'
    v3 = 'name1'
    v4 = 'tknzr1'
    sqlite_insert_Query = """
                            insert into model_details VALUES (?,?,?,?);
                            """
    sqlite_select_Query = """select * from model_details;"""

    cursor.execute(sqlite_drop_query)
    cursor.execute(sqlite_create_Query)
    cursor.execute(sqlite_insert_Query,(v1,v2,v3,v4))
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()
    sqliteConnection.commit()
    print(record)
    cursor.close()

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print("The SQLite connection is closed")