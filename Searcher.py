    
#WebPageSearcher.py
from sql import sql
from MorphemeParser import MorphemeParser
import math
import asyncio
import pymysql

class ScoredWebPage:
    def __init__(self,url,title,description,score):
        self.url = url
        self.title = title
        self.description = description
        self.score = score
    def __lt__(self,other):
        return self.score>other.score

class Searcher:
    @staticmethod
    def Search(conn,query):
        sws=[]
        tdcnt = sql.TotalDocumentCount(conn)
        moes = MorphemeParser.Parse(query)
        for mo in moes:
            mids = sql.FindMid(conn, mo.word)
            for mid in mids:
                # print(mid[0])
                ins = sql.FindInv(conn, mid[0])
                # print(ins)
                oidf = tdcnt/(max(len(ins),1)) #분모가 0이 나오지 않게 조절
                idf = max(math.log(oidf),0.1) #idf값이 0이 나오지 않게 조절
                for ri in range(0,len(ins)):
                    data_id,rcnt = ins[ri]
                    title,url,description,mcnt = sql.FindPageByWid(conn, data_id)
                    tf = rcnt/mcnt
                    score = tf*idf
                    sw = ScoredWebPage(url,title,description,score)
                    sws.append(sw)
        return Searcher.MergeDupSns(sws)
    @staticmethod
    def MergeDupSns(sws):
        res = list()
        for sw in sws:
            flag = False
            for i in range(0,len(res)):
                rsw = res[i]
                # if(rsw.url== sw.url):
                #     rsw.score += sw.score
                if(rsw== sw.url):
                    flag = True
                    break
            if flag == False:
                # res.append(sw)
                res.append(sw.url)
        res = sorted(res)
        return res
    

# async def run():
#     # DATABASE 연결
#     try:
#         connect = pymysql.connect(
#             host= 'localhost',
#             user= 'root',
#             password= 'darkwing991',
#             db='dream_joonggo',
#             charset='utf8mb4',
#         );
#         print(f'DB connection success.')
#     except:
#         print(connect)
#         print(pymysql.error)
        
#     try:
#         sns = Searcher.Search(connect,'6700xt') 
#         for sn in sns: 
#             print(f"{sn}")
#     finally:
#         connect.close()


# asyncio.run(run())

