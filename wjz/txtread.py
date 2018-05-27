import re
from wjz.wjzlog import get_logger
from wjz.db_connect import connect_db

logger = get_logger(name='txtread', path='txtread_log.log')

pattern_all = re.compile(r'^(.+)拼音：')
pattern = re.compile(r'^(.+)拼音：(.+)释义：(.+)出处：(.+)”示例')
count = 0


def update_db(db_s, cursor_s, data_tuple):
    global count
    try:
        res = cursor_s.execute(select_sql % data_tuple[0])
        if res == 0:
            r = cursor_s.execute(insert_sql % data_tuple)
            logger.info('insert' + str(r) + '->' + str(count) + ': ' + data_tuple[0])
        else:
            r = cursor_s.execute(update_sql % (data_tuple[1], data_tuple[0]))
            logger.info('update' + str(r) + '->' + str(count) + ': ' + data_tuple[0])
        count += 1
        db_s.commit()
    except:
        logger.error('error' + '->' + str(count) + ': ' + data_tuple[0])
        db_s.rollback()


if __name__ == '__main__':
    db = connect_db('wjz')
    cursor = db.cursor()
    select_sql = "select chengyu from chengyudaquan WHERE chengyu='%s'"
    update_sql = "update chengyudaquan set pinyin='%s' where chengyu='%s'"
    insert_sql = "INSERT INTO chengyudaquan(chengyu, pinyin, mean, source) VALUES ('%s', '%s', '%s', '%s')"
    with open('chengyu.txt', encoding='gb18030') as f:
        temp = []
        for line in f:
            line = line.strip()
            temp.clear()
            se = pattern.search(line)
            if se:
                for one in se.groups():
                    temp.append(one.strip())
                if len(temp) == 4:
                    update_db(db, cursor, tuple(temp))
    db.commit()
    cursor.close()
    db.close()
