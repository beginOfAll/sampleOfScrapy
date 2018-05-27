import json
import pymysql


def dict_merge(*args):
    res = {}
    for arg in args:
        for i in arg:
            if i not in res:
                res[i] = arg[i]
            else:
                print(res[i])
                print(arg[i])
                res[i].extend(arg[i])
                print(res[i])
    return res


def tempf():
    with open('domain_sentence_remove_dup_id_map.json', 'r') as f:
        map1 = json.load(f)
    with open('domain_sentence_replace_id_map.json', 'r') as f:
        map2 = json.load(f)
    with open('slot_sentence_remove_dup_id_map.json', 'r') as f:
        map3 = json.load(f)
    with open('slot_sentence_replace_id_map.json', 'r') as f:
        map4 = json.load(f)
    id_map = dict_merge(map1, map2, map3, map4)


"""
db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='for_platform', charset='utf8')
cursor = db.cursor()
sql = 'select id from {0} WHERE binary sentence="{1}"'
sql = sql.format('domain_sentence', '你好')
cursor.execute(sql)
res = cursor.fetchall()
print(len(res))
"""
d = {'w': '123', 'j': '123', 'z': '123', 'l': '123'}
k = d.keys()

print(len(k))
for i in k:
    print(i)
