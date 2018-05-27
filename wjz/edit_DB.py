import pymysql
import json
from datetime import datetime
from wjz.wjzlog import get_logger
import hashlib

logger = get_logger('edit_DB', 'edit_DB.log')


def sha_id(*args):
    sha = hashlib.sha256()
    for arg in args:
        if isinstance(arg, str):
            arg = arg.encode()
        sha.update(arg)
    digest = sha.hexdigest()
    if len(digest) != 64:
        return ''
    return digest


def size_time(t_str):
    return datetime.strptime(t_str, '%Y-%m-%d %H:%M:%S')


def merge_data(cursor, id_list):
    sql = 'select id,domains,update_time from domain_sentence where id IN {0} ORDER BY update_time ASC'
    sql = sql.format(str(tuple(id_list)))
    try:
        cursor.execute(sql)
    except:
        logger.error(sql)
        logger.error(cursor.Error())
    results = cursor.fetchall()
    domains_dict = {}
    last_id = ''
    for row in results:
        last_id = row[0]
        temp_domains = json.loads(row[1])
        logger.info(row)
        for k in temp_domains:
            if k in domains_dict:
                if size_time(temp_domains[k]['modify_time']) > size_time(domains_dict[k]['modify_time']):
                    domains_dict[k] = temp_domains[k]
            else:
                domains_dict[k] = temp_domains[k]
    return last_id, json.dumps(domains_dict, ensure_ascii=False)


def insert_new_data(cursor, id_domian_dict):
    select_sql = 'select * from domain_sentence where id="{0}"'
    insert_sql = 'insert into domain_sentence VALUES{0}'
    for k in id_domian_dict:
        sql = select_sql.format(k)
        try:
            cursor.execute(sql)
        except:
            logger.error(sql)
            logger.error(cursor.Error())
        row = cursor.fetchone()
        if not row:
            continue
        row = list(row)
        # id = sha()
        row[6] = str(row[6])
        row[7] = str(row[7])
        row[8] = sha_id(row[3])
        row[4] = id_domian_dict[k]
        sql = insert_sql.format(str(tuple(row)))
        try:
            c = cursor.execute(sql)
            logger.info('insert: ' + str(c) + '  ' + k)
        except:
            logger.error(sql)
            logger.error(cursor.Error())


def delete_old_data(cursor, sen_id_dict):
    delete_sql = 'delete from domain_sentence where id in {0}'
    for k in sen_id_dict:
        sql = delete_sql.format(str(tuple(sen_id_dict[k])))
        try:
            c = cursor.execute(sql)
            logger.info('delete: ' + str(c) + '  ' + k)
        except:
            logger.error(sql)
            logger.error(cursor.Error())


if __name__ == '__main__':
    db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='for_platform',
                         charset='utf8')
    cursor = db.cursor()
    with open("domain_same", 'r', encoding='utf-8') as f:
        sen_idlist_dict = json.load(f)
    id_domains_dict = {}
    for k in sen_idlist_dict:
        lastid, new_domains = merge_data(cursor, sen_idlist_dict[k])
        logger.info(lastid + ': ' + new_domains)
        logger.info('----------------------------------')
        id_domains_dict[lastid] = new_domains
    insert_new_data(cursor, id_domains_dict)
    delete_old_data(cursor, sen_idlist_dict)
    db.commit()
    cursor.close()
    db.close()
