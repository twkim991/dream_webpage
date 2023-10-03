from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import asyncio
import pymysql
import sys
import threading





# 전역변수 선언 및 초기화
URL = "https://m.bunjang.co.kr/products/237939672"
LISTURL = "https://m.bunjang.co.kr/categories/600200"
LISTURLURL = "https://m.bunjang.co.kr/categories/600200?page=301"
PAGING = 301

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
# options.add_argument("headless")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options)

cnt = 0
connect = None
db = None





class WebPage:
    def __init__(self,url,title,text,links):
        self.url = url
        self.title = title
        self.price = price
        self.text = text
        self.img = img
        self.links = links
        self.mcnt=0
    @staticmethod
    def MakeWebPage(url,cpage):
        try:
            title = cpage.title.text
            atags = cpage.find_all("a")
            links=WebPage.ExtractionUrls(atags)
        except:
            return None
        else:
            return WebPage(url,title,cpage.text,links)
    





# 웹페이지에서 데이터를 수집하는 함수
async def Collect(url):
    try:
        driver.get(URL)
        await asyncio.sleep(300)

        # 웹 페이지가 로드될 때까지 대기
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div')))

        # 데이터 수집
        rawtitle = driver.find_elements(By.XPATH, '//*[contains(@class,"ProductSummarystyle__Name")]')
        title = [element.text for element in rawtitle][0]
        print(title)

        rawprice = driver.find_elements(By.XPATH, '//*[contains(@class,"ProductSummarystyle__Price")]//*[contains(@class,"ProductSummarystyle__Price")]')
        price = [element.text for element in rawprice][0]
        print(price)

        rawtext = driver.find_elements(By.XPATH, '//*[contains(@class,"ProductInfostyle__DescriptionContent")]/p')
        text = [element.text for element in rawtext][0]
        print(text)

        rawimg = driver.find_elements(By.XPATH, '//*[@class="sc-fONwsr koteUt"]/img')
        img = [element.get_attribute('src') for element in rawimg]
        print(img)
    finally:
        # WebDriver 종료
        driver.quit()
        return WebPage(url,title,price,text,img,links)



async def Collecturl(conn):
    global PAGING
    global LISTURLURL
    while True:
        driver.get(LISTURLURL)
        await asyncio.sleep(3)

        # 웹 페이지가 로드될 때까지 대기
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[1]')))

        # #url 수집
        rawdata = driver.find_elements(By.TAG_NAME, 'a')
        rawlinks = [element.get_attribute('href') for element in rawdata]
        links = []
        for i,link in enumerate(rawlinks):
            if link is not None and 'https://m.bunjang.co.kr/products/' in link:
                index = link.find("?")
                if(index != -1):
                    link = link[:index]
                links.append(link)
        
        # print(links[0],links[1],links[2])
        #수집한 링크들을 후보 db에 저장
        if links != []:
            sql.AddCandidate(conn, links)

        # 현재 페이지가 몇번째인지 체크하고 마지막페이지면 종료함
        lastpaging = driver.find_elements(By.XPATH, '//*[@class="sc-bfYoXt esGGYP"]/a[last()]')
        islastpage = [ btn.value_of_css_property('visibility') for btn in lastpaging]
        # print(islastpage)
        if islastpage == 'visible':
            PAGING = PAGING + 1
            LISTURLURL = LISTURL + f'?page={PAGING}'
        else:
            rawpage = driver.find_elements(By.XPATH, '//*[@class="sc-bfYoXt esGGYP"]/a')
            # print(len(rawpage))
            if PAGING%10 != len(rawpage) - 2:
                PAGING = PAGING + 1
                LISTURLURL = LISTURL + f'?page={PAGING}'
            else:
                print("마지막 페이지에 도달했습니다. 크롤링을 종료합니다.")
                break;

        console_log(PAGING-1,links);

# # 수집하는 함수가 주기적으로 후보 url을 수집해서 후보 db에 저장하는 함수
# async def Collecturl(conn, period,tm_callback):
#     global PAGING
#     global LISTURLURL
#     driver.get(LISTURLURL)
#     await asyncio.sleep(3)

#     # 웹 페이지가 로드될 때까지 대기
#     wait = WebDriverWait(driver, 10)
#     wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div')))

#     #url 수집
#     rawdata = driver.find_elements(By.TAG_NAME, 'a')
#     rawlinks = [element.get_attribute('href') for element in rawdata]
#     links = []
#     for i,link in enumerate(rawlinks):
#         if link is not None and 'https://m.bunjang.co.kr/products/' in link:
#             index = link.find("?")
#             if(index != -1):
#                 link = link[:index]
#             links.append(link)
    
#     #수집한 링크들을 후보 db에 저장
#     if links != []:
#         sql.AddCandidate(conn, links)
#         if tm_callback != None:
#             tm_callback(PAGING,links)
#     timer = threading.Timer(conn,period,Collecturl,[period,tm_callback])

#     # 현재 페이지가 몇번째인지 체크하고 마지막페이지면 종료함
#     lastpaging = driver.find_elements(By.XPATH, '//*[@class="sc-bfYoXt esGGYP"]/a[last()]')
#     islastpage = [ btn.value_of_css_property('visibility') for btn in lastpaging]
#     # print(islastpage)
#     if islastpage == 'visible':
#         PAGING = PAGING + 1
#         LISTURLURL = LISTURL + f'?page={PAGING}'
#     else:
#         rawpage = driver.find_elements(By.XPATH, '//*[@class="sc-bfYoXt esGGYP"]/a')
#         # print(len(rawpage)-2)
#         if PAGING/10 != len(rawpage) - 2:
#             PAGING = PAGING + 1
#             LISTURLURL = LISTURL + f'?page={PAGING}'
#         else:
#             print("마지막 페이지에 도달했습니다. 크롤링을 종료합니다.")
#             timer.cancel()
#             return 0

#     timer.start()





# 수집하는 함수가 주기적으로 페이지를 수집할 수 있게 하기위한 함수 원래는 후보에 url 저장하는 기능도 같이 있었는데 나는 분리하도록 하겠음
def Collectdata(conn,period,tm_callback):
    url,depth = sql.GetCandidate()
    res = Collect(url)
    if res != None:
        sql.AddData(conn, res)
        if tm_callback != None:
            tm_callback(url,depth)
    timer = threading.Timer(period,Collectdata,[period,tm_callback])
    timer.start()





# 수집한 페이지가 무엇인지 보여주게 하는 함수
def console_log(cnt,links):
    # print("{0}번째 페이지 {1} 수집".format(cnt,links))
    print("{0}번째 페이지 수집".format(cnt))





class sql:
    # 후보 링크들을 추가하는 함수
    @staticmethod
    def AddCandidate(conn, links):
        db = conn.cursor();
        # print(links[0],links[1],links[2])
        for url in links:
            # print(url)
            # 후보 링크가 데이터 db에 있는지, 후보 db에 있는지 체크
            if sql.CheckData(db, 'joonggo_data', url)==0 or sql.CheckData(db, 'candidate', url)==0:
                continue
            qry = f"INSERT INTO Candidate(url) values('{url}')"
            try:
                db.execute(qry)
                print(qry)
            except:
                print('ADDCANDIDATE ERROR')
                return False
        conn.commit()

    # 후보에 있는 url의 페이지를 크롤링하기 위해 후보 db에서 가져오는 함수
    @staticmethod
    def GetCandidate(conn):
        db = conn.cursor();
        qry = f"SELECT id FROM Candidate LIMIT 1;"
        db.execute(qry)
        id = cursor.fetchone()
        if id not in locals():
            return "",-1
        qry = f"SELECT url,depth FROM Candidate WHERE id={id};"
        db.execute(qry)
        row = cursor.fetchone()
        if row:
            qry = f"DELETE FROM Candidate WHERE id={id};"
            db.execute(qry);
            conn.commit();
            return row[0], row[1]
        else:
            return "",-1

    
    # 크롤링한 페이지를 data db에 저장하는 함수
    @staticmethod
    def AddData(conn, data):
        db = conn.cursor();
        qry = f"INSERT INTO joonggo_data(url, title, text, img_url, mcnt) values('{data.url}', '{data.title}', '{data.text}', '{data.img_url}', {mcnt})"
        db.execute(qry)
        conn.commit();
    
    # 후보에 넣으려는 링크가 원하는 db에 있는지 체크하는 함수
    @staticmethod
    def CheckData(db, dbname, url):
        qry = f"SELECT url FROM {dbname} WHERE url = '{url}';"
        db.execute(qry)
        res = db.fetchone()
        if res:
            return 0
        else:
            return -1





async def run():
    # DATABASE 연결
    try:
        connect = pymysql.connect(
            host= 'localhost',
            user= 'root',
            password= 'darkwing991',
            db='dream_joonggo',
            charset='utf8',
        );
        print(f'DB connection success.')
    except:
        print(connect)
        print(pymysql.error)
        
    try:
        if sys.argv[1] == 'url':
            await Collecturl(connect)
        elif sys.argv[1] == 'data':
            sql.AddCandidate(connect, URL, 0)
            await Collect(URL)
    finally:
        connect.close()


asyncio.run(run())
  
  # 해야하는 일 첫째. url 크롤링 부분 함수 완성시키는것 둘쨰. 번장이랑 다른 사이트 구분짓기