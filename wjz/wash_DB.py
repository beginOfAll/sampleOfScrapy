import pymysql
import json
from datetime import datetime
from wjz.wjzlog import get_logger
import hashlib
import time

logger = get_logger('wash_DB', 'wash_DB.log')


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


def merge_data(cursor, id_list, table_name):
    if table_name == 'domain_sentence':
        sql = 'select id,domains,platform,update_time from {0} where id IN {1} ORDER BY update_time ASC'
    else:
        sql = 'select id,slots,platform,update_time from {0} where id IN {1} ORDER BY update_time ASC'
    sql = sql.format(table_name, str(tuple(id_list)))
    try:
        cursor.execute(sql)
    except:
        logger.error(sql)
        logger.error(cursor.Error())
    results = cursor.fetchall()
    domains_dict = {}
    platform_set = set()
    last_id = ''
    for row in results:
        last_id = row[0]
        platform_set.add(row[2])
        temp_domains = json.loads(row[1])
        logger.info(str(row[3]) + row[2] + row[1])
        for k in temp_domains:
            if k in domains_dict:
                if size_time(temp_domains[k]['modify_time']) > size_time(domains_dict[k]['modify_time']):
                    domains_dict[k] = temp_domains[k]
            else:
                domains_dict[k] = temp_domains[k]
    return last_id, json.dumps(domains_dict, ensure_ascii=False), json.dumps(list(platform_set), ensure_ascii=False)


def insert_new_data(cursor, id_domian_dict, table_name):
    select_sql = 'select * from {0} where id="{1}"'
    insert_sql = 'insert into {0} VALUES{1}'
    res = {}  # oldID : newID
    for k in id_domian_dict:
        sql = select_sql.format(table_name, k)
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
        row[4] = id_domian_dict[k][0]
        row[2] = id_domian_dict[k][1]
        sql = insert_sql.format(table_name, str(tuple(row)))
        try:
            c = cursor.execute(sql)
            if c != 1:
                logger.error('insert: new_data ' + str(c) + '  ' + row[3] + row[2] + row[8])
                logger.error(sql)
            res[k] = row[8]
        except:
            logger.error(sql)
            logger.error(cursor.Error())
    return res


def delete_old_data(cursor, sen_id_dict, table_name):
    delete_sql = 'delete from {0} where id in {1}'
    for k in sen_id_dict:
        sql = delete_sql.format(table_name, str(tuple(sen_id_dict[k])))
        try:
            c = cursor.execute(sql)
            if c != len(sen_id_dict[k]):
                logger.error('delete: ' + str(c) + '  real count' + len(sen_id_dict[k]))
                logger.error(sql)
        except:
            logger.error(sql)
            logger.error(cursor.Error())


def id_replace_map(sen_id_dict, id_dict):
    res = {}
    for sen in sen_id_dict:
        for old_id in id_dict:
            if old_id in sen_id_dict[sen]:
                for one_old_id in sen_id_dict[sen]:
                    res[one_old_id] = id_dict[old_id]
    return res


def get_all_sentence(cursor, table_name):
    sql = "select sentence from {0}"
    cursor.execute(sql.format(table_name))
    results = cursor.fetchall()
    temp = [row[0] for row in results]
    for sen in set(temp):
        yield sen


def get_id_send(cursor, table_name):
    sql = "select id,sentence from {0}"
    cursor.execute(sql.format(table_name))
    results = cursor.fetchall()
    for row in results:
        yield row[0], row[1]


def find_same_sentence(cursor, sen, table_name):
    sql = 'select id from {0} WHERE binary sentence="{1}"'
    sql = sql.format(table_name, sen)
    try:
        cursor.execute(sql)
    except:
        logger.error(sql)
    results = cursor.fetchall()
    if len(results) > 1:
        logger.info(sen + ': ' + str(len(results)))
        yield [i[0] for i in results]


def update_id_by_oldid(cursor, oldid, newid, table_name):
    update_sql = 'update {0} set id="{1}" WHERE id="{2}"'
    sql = update_sql.format(table_name, newid, oldid)
    try:
        c = cursor.execute(sql)
        if c != 1:
            logger.error('ID:old --> new ' + str(c))
            logger.error(sql)
    except:
        logger.error(sql)


def remove_dup(cursor, table):
    # 查找重复句子及ID {sen:[id1,id2...]}
    same_dict = {}
    for sen in get_all_sentence(cursor, table):
        for id_list in find_same_sentence(cursor, sen, table):
            same_dict[sen] = id_list
    # 统合重复句子数据 以最新数据为准 {id:[{domains},[platform]]}
    id_domains_dict = {}
    for k in same_dict:
        logger.info('---------------------------------------------------------------------')
        logger.info('merge: ' + k)
        lastid, new_domains, new_platform = merge_data(cursor, same_dict[k], table)
        logger.info(new_platform + ' ' + new_domains + 'new_id: ' + lastid)
        id_domains_dict[lastid] = [new_domains, new_platform]
    # 插入 统合后的数据,新旧ID {old_id:new_id}
    id_dict = insert_new_data(cursor, id_domains_dict, table)
    # 删除旧数据
    delete_old_data(cursor, same_dict, table)
    # 输出 id 置换表 {oldid:newid}
    new_old_id_dict = id_replace_map(same_dict, id_dict)
    with open(table + '_domain_same.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(same_dict, ensure_ascii=False))
    with open(table + '_remove_dup_id_map.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(new_old_id_dict, ensure_ascii=False))
    return new_old_id_dict


def update_all_id(cursor, table_name):
    # 取得所有数据
    replace_id_dict = {}
    for oldid, sen in get_id_send(cursor, table_name):
        newid = sha_id(sen)
        if newid != oldid:
            update_id_by_oldid(cursor, oldid, newid, table_name)
            replace_id_dict[oldid] = newid
    with open(table_name + '_replace_id_map.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(replace_id_dict, ensure_ascii=False))
    return replace_id_dict


def dict_merge(*args):
    res = {}
    for arg in args:
        for i in arg:
            if i not in res:
                res[i] = arg[i]
            else:
                if arg[i] != res[i]:
                    logger.error("------------- old_id 对应不同 new_id")
                    logger.error(i + "---new1" + res[i] + "---new2" + arg[i])
    return res


def update_dialog(cursor, id_map):
    select_sql = 'select id,sentence_id from dialogue '
    update_sql = "update dialogue set sentence_id='{0}' WHERE id='{1}'"
    try:
        cursor.execute(select_sql)
    except:
        logger.error(select_sql)
    results = cursor.fetchall()
    results = list(results)
    for row in results:
        is_update = False
        sen_id_list = json.loads(row[1])
        for index, value in enumerate(sen_id_list):
            if value in id_map:
                sen_id_list[index] = id_map[value]
                is_update = True
        if is_update:
            sql = update_sql.format(json.dumps(sen_id_list, ensure_ascii=False), row[0])
            try:
                c = cursor.execute(sql)
                if c != 1:
                    logger.error('update dialog ' + str(c))
                    logger.error(sql)
            except:
                logger.error(sql)


def update_annotate_record(cursor, id_map):
    select_sql = 'select id,sentence_id from annotate_record'
    update_sql = 'update annotate_record set sentence_id="{0}" WHERE id="{1}"'
    try:
        cursor.execute(select_sql)
    except:
        logger.error(select_sql)
    results = cursor.fetchall()
    results = [list(row) for row in results]
    for row in results:
        is_update = False
        if row[1] in id_map:
            row[1] = id_map[row[1]]
            is_update = True
        if is_update:
            sql = update_sql.format(row[1], row[0])
            try:
                c = cursor.execute(sql)
                if c != 1:
                    logger.error('update annotate_record ' + str(c))
                    logger.error(sql)
            except:
                logger.error(sql)


if __name__ == '__main__':
    # 1.清洗domain句子库(重复句子,统合信息,插入统合后新句子,删除旧句子) 输出id更新map
    # 2.用新方法计算表内所有句子的新id, 替换所有id, 输出id更新map
    # 3.整合两张map,输出 总id-map
    # 4.用总map, 更新其他表中id信息

    # localhost
    db = pymysql.connect(host='10.12.6.26', port=3306, user='root', passwd='aispeech2018', db='semantic_tagging_tool',
                         charset='utf8')
    cursor = db.cursor()

    time0 = time.time()
    id_map_1 = remove_dup(cursor, 'domain_sentence')
    db.commit()

    id_map_2 = update_all_id(cursor, 'domain_sentence')
    db.commit()

    id_map_3 = remove_dup(cursor, 'slot_sentence')
    db.commit()

    id_map_4 = update_all_id(cursor, 'slot_sentence')
    db.commit()

    id_map = dict_merge(id_map_1, id_map_2, id_map_3, id_map_4)

    with open('id_map.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(id_map, ensure_ascii=False))

    # 修改dialog表ID,annotate_record表ID
    logger.info('update dialog....')
    update_dialog(cursor, id_map)
    db.commit()

    logger.info('annotate_record....')
    update_annotate_record(cursor, id_map)
    db.commit()

    cursor.close()
    db.close()
    logger.info('time info : ' + str(time.time() - time0))
