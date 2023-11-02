from sql import sql
import asyncio
import pymysql
from MorphemeParser import MorphemeParser
import re


def analyze(conn, url, title, text):
    print(f"{url}:{title}====")
    m1 = MorphemeParser.Parse(title)
    m2 = MorphemeParser.Parse(text)
    sql.UpdateMcnt(conn, url, len(m1)+len(m2))    
    m1.extend(m2)
    m1 = MorphemeParser.Merge(m1)
    data_id = sql.findid(conn, url)
    for mo in m1:
        sql.AddMorpheme(conn, mo)
        mo_id = sql.FindMid(conn, mo.word)
        sql.AddInverseItem(conn, mo_id, data_id, mo.ref)
        # print(f"{mo.word}:{mo.ref}")

async def run():
    # DATABASE 연결
    try:
        connect = pymysql.connect(
            host= 'localhost',
            user= 'root',
            password= 'darkwing991',
            db='dream_joonggo',
            charset='utf8mb4',
        );
        print(f'DB connection success.')
    except:
        print(connect)
        print(pymysql.error)
        
    try:
        for i in range(88000, 10000000):
            url, title, text = sql.GetData2(connect, i+1)
            title = re.sub(pattern='[^\w\s]', repl='', string=title)
            text = re.sub(pattern='[^\w\s]', repl='', string=text)
            analyze(connect, url, title, text)
    finally:
        connect.close()


asyncio.run(run())
