import pymysql
import json
import random

sample_sql = "select chengyu from chengyudaquan WHERE chengyu REGEXP '^{0}' AND common = TRUE AND isfour = TRUE "


def jielong(word):
    res = ''
    sql = sample_sql.format(word)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        # for row in results:
        #     print(row[0])

        res = random.choice(results)[0]
    except:
        db.rollback()
    return res


def four():
    sql = "UPDATE chengyu SET isfour = TRUE WHERE chengyu REGEXP '.{4}'"
    try:
        cursor.execute(sql)
        print(cursor.rowcount)
    except:
        db.rollback()
        print('error')


if __name__ == '__main__':
    db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='wjz', charset='utf8')
    cursor = db.cursor()
    w = input()
    for i in range(20):
        if w is not '':
            print(w, end='->')
            w = jielong(w[-1])
        else:
            print('')
    print('')
    cursor.close()
    db.close()
