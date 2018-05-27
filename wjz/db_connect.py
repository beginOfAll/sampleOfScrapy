import pymysql


def connect_db(db_name):
    return pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db=db_name, charset='utf8')
