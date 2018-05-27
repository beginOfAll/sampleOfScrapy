from pypinyin import pinyin
from wjz.db_connect import connect_db


def get_pinyin(word):
    res_list = pinyin(word)
    res = []
    for i in res_list:
        res.append(i[0])
    return ' '.join(res)


def select_pinyin_num(db):
    sql = "select num,chengyu from chengyudaquan where pinyin is null"
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    for row in results:
        yield row


def update_pinyin(cursor, pinyin, num):
    sql = "update chengyudaquan set pinyin='{0}' where num={1}"
    try:
        r = cursor.execute(sql.format(pinyin, num))
        print(r, num, pinyin)
    except:
        print('error:', num, pinyin)


if __name__ == '__main__':
    db = connect_db('wjz')
    cursor = db.cursor()
    for row in select_pinyin_num(db):
        update_pinyin(cursor, get_pinyin(row[1]), row[0])
    db.commit()
    cursor.close()
    db.cursor()
