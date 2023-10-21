from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import joblib
import time
import asyncio
import pymysql
import sys
import re





# 전역변수 선언 및 초기화
LISTURL = "https://web.joongna.com/store/4355739"
NOWPAGE = 1

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-gpu")
options.add_argument("--disable-extensions")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options)

cnt = 0
connect = None
db = None
# 저장된 모델 불러오기
loaded_model = joblib.load('ad_checker.pkl')
loaded_vectorizer = joblib.load('vectorizer.pkl')





class WebPage:
    def __init__(self,url,platform,issoldout,title,price,text):
        self.url = url
        self.platform = platform
        self.issoldout = issoldout
        self.title = title
        self.price = price
        self.text = text
    




# 수집하는 함수가 주기적으로 페이지를 수집할 수 있게 하기위한 함수 원래는 후보에 url 저장하는 기능도 같이 있었는데 나는 분리하도록 하겠음
async def Collectdata(conn, start):
    for i in range(10000000000):
        url,platform = sql.GetCandidate(conn, start)
        if url == '':
            break;
        # print(url,platform)
        res,imgs = await Collect(url, platform)
        # print(res.text,imgs)
        if res != None and res != '':
            sql.AddData(conn, res)
            sql.AddImg(conn, url, imgs)
        sql.DeleteCandidate(conn, url)





# 웹페이지에서 데이터를 수집하는 함수
async def Collect(url, platform):
    try:
        driver.get(url)
        await asyncio.sleep(3)

        # 웹 페이지가 로드될 때까지 대기
        driver.implicitly_wait(10)

        if platform == 'bunjang':
            #이미 삭제된 상품인지 확인
            try:
                rawdeletedcheck = driver.find_element(By.XPATH, '//*[contains(@class,"Productsstyle__FailedProductWrapper")]')
                print("이건 이미 삭제됐어")
                deletedcheck = rawdeletedcheck.text
                return "",""
            except NoSuchElementException:
                print("")

            # 이미 팔린 상품인지 확인
            issoldout = 0
            try:
                rawsoldoutcheck = driver.find_element(By.XPATH, '//*[contains(@class,"Productsstyle__SoldoutTitle")]')
                soldoutcheck = rawsoldoutcheck.text
                issoldout = 1
                url = url + '?original=1'
                driver.get(url)
                print('이건 이미 팔렸어')
            except NoSuchElementException:
                issoldout = 0
                print('이건 아직 안팔림')

            # 데이터 수집
            rawtitle = driver.find_elements(By.XPATH, '//*[contains(@class,"ProductSummarystyle__Name")]')
            title = [element.text for element in rawtitle][0]
            # print(title)

            rawprice = driver.find_elements(By.XPATH, '//*[contains(@class,"ProductSummarystyle__Price")]//*[contains(@class,"ProductSummarystyle__Price")]')
            price_str = [element.text for element in rawprice][0]
            price = re.sub(r'[^0-9]', '', price_str)
            # print(price)

            rawtext = driver.find_elements(By.XPATH, '//*[contains(@class,"ProductInfostyle__DescriptionContent")]/p')
            text = [element.text for element in rawtext][0]
            print(text)

            rawimg = driver.find_elements(By.XPATH, '//*[contains(@class,"Productsstyle__ProductImageWrapper")]/div/div/img')
            imgs = [element.get_attribute('src') for element in rawimg]
            return WebPage(url,platform,issoldout,title,price,text), imgs
            # print(imgs)
        elif platform == 'joongna':
            #제목으로 이미 삭제된 상품인지 확인
            rawtitle = driver.find_elements(By.XPATH, '//h1')
            title = [element.text for element in rawtitle][0]
            # print(title)
            if '상품은 삭제된 상태입니다' in title or '판매보류된 상품입니다' in title or '이용제한된 회원의 상품입니다.' in title or '현재 거래가 불가능한 회원의 상품입니다.' in title or '탈퇴한 회원의 상품입니다.' in title:
                print("\n\n이건 이미 삭제됐어")
                return "",""

            # 이미 팔린 상품인지 확인
            issoldout = 0
            try:
                rawsoldoutcheck = driver.find_element(By.XPATH, '//div[contains(@class,"items-start")]/div[1]/div[1]/div[1]/div[1]/div/div')
                soldoutcheck = rawsoldoutcheck.text
                issoldout = 1
                print('\n\n이건 이미 팔렸어')
            except NoSuchElementException:
                issoldout = 0
                print('\n\n이건 아직 안팔림')

            rawprice = driver.find_elements(By.XPATH, '//h1/following-sibling::div/div')
            price_str = [element.text for element in rawprice][0]
            price = re.sub(r'[^0-9]', '', price_str)
            # print(price)

            text = ""
            rawtext = driver.find_elements(By.XPATH, '//article/p')
            if rawtext != []:
                text = [element.text for element in rawtext][0]
            # print(text)

            rawimg = driver.find_elements(By.XPATH, '//div[contains(@class,"items-start")]//img')
            rawimgs = [element.get_attribute('src') for element in rawimg]
            imgs = []
            for img in rawimgs:
                if 'https://web.joongna.com/assets/' not in img:
                    imgs.append(img)
            # print(imgs)
            return WebPage(url,platform,issoldout,title,price,text), imgs
    finally:
        print("\n\n데이터 수집 완료! 처리중...\n\n")





# 웹페이지에서 후보 url을 수집하는 함수
async def Collecturl(conn):
    global NOWPAGE
    global LISTURL
    driver.get(LISTURL)


    if 'm.bunjang.co.kr' in LISTURL:
        for i in range(10000000000):
            # 웹 페이지가 로드될 때까지 대기
            await asyncio.sleep(3)
            driver.implicitly_wait(10)

            # #url 수집
            rawdata = driver.find_elements(By.TAG_NAME, 'a')
            rawlinks = [element.get_attribute('href') for element in rawdata]
            # print(rawlinks)
            links = []
            for i,link in enumerate(rawlinks):
                if link is not None and '/products/' in link and 'https://m.bunjang.co.kr/products/new' not in link:
                    index = link.find("?")
                    if(index != -1):
                        link = link[:index]
                    links.append(link)
            # print(links)
            # print(links[0],links[1],links[2])
            #수집한 링크들을 후보 db에 저장
            if links != []:
                sql.AddCandidate(conn, links, 'bunjang')

            # 현재 페이지가 몇번째인지 체크하고 마지막페이지면 종료함
            pagingicons = driver.find_elements(By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div[last()]/div/a')
            icons = [btn.value_of_css_property('background') for btn in pagingicons]
            nextpagenum = 1
            for i,icon in enumerate(icons):
                if 'rgb(255, 80, 88)' in icon:
                    nextpagenum = i+1
            print(NOWPAGE)
            nexticons = driver.find_elements(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[last()]/div/a[{nextpagenum+1}]')
            nexticon = [ btn.value_of_css_property('visibility') for btn in nexticons]
            # print(nexticon[0])
            if nexticon[0] == 'visible':
                NOWPAGE = NOWPAGE + 1
                driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[last()]/div/a[{nextpagenum+1}]').click()
            else:
                print("마지막 페이지에 도달했습니다. 크롤링을 종료합니다.")
                break;
    elif 'web.joongna.com' in LISTURL:
        for i in range(10000000000):
        # 웹 페이지가 로드될 때까지 대기
            await asyncio.sleep(3)
            driver.implicitly_wait(10)

            # #url 수집
            rawdata = driver.find_elements(By.TAG_NAME, 'a')
            rawlinks = [element.get_attribute('href') for element in rawdata]
            # print(rawlinks)
            links = []
            for i,link in enumerate(rawlinks):
                if link is not None and '/product/' in link:
                    index = link.find("?")
                    if(index != -1):
                        link = link[:index]
                    links.append(link)

            #수집한 링크들을 후보 db에 저장
            if links != []:
                sql.AddCandidate(conn, links, 'joongna')

            # 현재 페이지가 몇번째인지 체크하고 마지막페이지면 종료함
            try:
                nexticon = driver.find_element(By.XPATH, '//main/div[1]/div[2]/div[4]/ul/li[contains(@class,"bg-jngreen/80")]/following-sibling::li')
            except NoSuchElementException:
                print("마지막 페이지입니다. 장비를 정지합니다.")
                break;
            NOWPAGE = NOWPAGE + 1
            print(NOWPAGE)
            driver.get(LISTURL + f'&page={NOWPAGE}')
                  

        # console_log(PAGING-1,links);
        




# db에 저장되어있던 링크의 중고물품이 팔렸는지 확인하는 함수
async def CheckIssoldout(conn):
    datas = sql.GetData(conn)
    for i, data in enumerate(datas):
        url = data[0]
        platform = data[1]
        issoldout = await Check(conn, url, platform)
        if issoldout == 0:
            pass;
        else:
            sql.UpdateIssoldout(conn,url,issoldout)
        

    if url == '':
        return;





# 링크의 웹페이지에 들어가서 팔렸는지 직접 체크하는 함수
async def Check(conn, url, platform):
    try:
        driver.get(url)
        await asyncio.sleep(3)

        # 웹 페이지가 로드될 때까지 대기
        driver.implicitly_wait(10)

        if platform == 'bunjang':
            #이미 삭제된 상품인지 확인
            try:
                rawdeletedcheck = driver.find_element(By.XPATH, '//*[contains(@class,"Productsstyle__FailedProductWrapper")]')
                print("이건 이미 삭제됐어")
                deletedcheck = rawdeletedcheck.text
                return 1
            except NoSuchElementException:
                print("")

            # 이미 팔린 상품인지 확인
            issoldout = 0
            try:
                rawsoldoutcheck = driver.find_element(By.XPATH, '//*[contains(@class,"Productsstyle__SoldoutTitle")]')
                soldoutcheck = rawsoldoutcheck.text
                issoldout = 1
                url = url + '?original=1'
                driver.get(url)
                print('이건 이미 팔렸어')
            except NoSuchElementException:
                issoldout = 0
                print('이건 아직 안팔림')
            return issoldout
        elif platform == 'joongna':
            #제목으로 이미 삭제된 상품인지 확인
            rawtitle = driver.find_elements(By.XPATH, '//h1')
            title = [element.text for element in rawtitle][0]
            # print(title)
            if '상품은 삭제된 상태입니다' in title or '판매보류된 상품입니다' in title or '이용제한된 회원의 상품입니다.' in title or '현재 거래가 불가능한 회원의 상품입니다.' in title or '탈퇴한 회원의 상품입니다.' in title:
                print("\n\n이건 이미 삭제됐어")
                return 1

            # 이미 팔린 상품인지 확인
            issoldout = 0
            try:
                rawsoldoutcheck = driver.find_element(By.XPATH, '//div[contains(@class,"items-start")]/div[1]/div[1]/div[1]/div[1]/div/div')
                soldoutcheck = rawsoldoutcheck.text
                issoldout = 1
                print('\n\n이건 이미 팔렸어')
            except NoSuchElementException:
                issoldout = 0
                print('\n\n이건 아직 안팔림')
            return issoldout
    finally:
        print("\n\n판매여부 체크 완료!\n\n")





# 임시 함수
async def temp(conn):
    global NOWPAGE
    global LISTURL
    driver.get(LISTURL)


    if 'm.bunjang.co.kr' in LISTURL:
        # 웹 페이지가 로드될 때까지 대기
        await asyncio.sleep(3)
        driver.implicitly_wait(10)

        

        # #url 수집
        rawdata = driver.find_elements(By.TAG_NAME, 'a')
        rawlinks = [element.get_attribute('href') for element in rawdata]
        # print(rawlinks)
        links = []
        for i,link in enumerate(rawlinks):
            if link is not None and '/products/' in link and 'https://m.bunjang.co.kr/products/new' not in link:
                index = link.find("?")
                if(index != -1):
                    link = link[:index]
                links.append(link)
        # print(links)
        # print(links[0],links[1],links[2])
        #수집한 링크들을 후보 db에 저장
        if links != []:
            sql.AddCandidate(conn, links, 'bunjang')

    elif 'web.joongna.com' in LISTURL:
        # 웹 페이지가 로드될 때까지 대기
        await asyncio.sleep(3)
        driver.implicitly_wait(10)

        while(True):
            try:
                rawplus = driver.find_elements(By.XPATH, '//button[text()="더보기"]')
                plus = [element.text for element in rawplus][0]
                print(plus)
                driver.find_element(By.XPATH, '//button[text()="더보기"]').click()
                await asyncio.sleep(3)
            except:
                break;
        
        # #url 수집
        rawdata = driver.find_elements(By.TAG_NAME, 'a')
        rawlinks = [element.get_attribute('href') for element in rawdata]
        # print(rawlinks)
        links = []
        for i,link in enumerate(rawlinks):
            if link is not None and '/product/' in link:
                index = link.find("?")
                if(index != -1):
                    link = link[:index]
                links.append(link)

        #수집한 링크들을 후보 db에 저장
        if links != []:
            sql.AddCandidate(conn, links, 'joongna')





# DB를 조작하는 각종 함수들을 모아놓은 클래스
class sql:
    # 후보 링크들을 추가하는 함수
    @staticmethod
    def AddCandidate(conn, links, platform):
        db = conn.cursor();
        # print(links)
        for url in links:
            print(url)
            # 후보 링크가 데이터 db에 있는지, 후보 db에 있는지 체크
            if sql.CheckData(conn, 'joonggo_data', url)==0 or sql.CheckData(conn, 'candidate', url)==0:
                continue
            qry = f"INSERT INTO Candidate(url,platform) values('{url}', '{platform}')"
            print(qry)
            try:
                db.execute(qry)
                print(qry)
            except:
                print('ADDCANDIDATE ERROR')
                return False
        conn.commit()

    # 후보에 있는 url의 페이지를 크롤링하기 위해 후보 db에서 가져오는 함수
    @staticmethod
    def GetCandidate(conn, start):
        db = conn.cursor();
        qry = f"SELECT url,platform,id FROM Candidate WHERE id>{start} LIMIT 1;"
        db.execute(qry)
        row = db.fetchone()
        print(f"\n\n{row[2]}번 후보 데이터 수집 시작!")
        if row:
            return row[0], row[1]
        else:
            return "",""

    @staticmethod
    def DeleteCandidate(conn, url):
        db = conn.cursor();
        qry = f"DELETE FROM Candidate WHERE url='{url}';"
        print(qry)
        print(f"\n\n{url}데이터 수집 완료! 후보DB에서 삭제!")
        db.execute(qry);
        conn.commit();

    # 크롤링한 페이지를 data db에 저장하는 함수
    @staticmethod
    def AddData(conn, data):
        db = conn.cursor();
        data.title = data.title.replace("'", "''")
        data.title = data.title.replace('""', '""')
        data.text = data.text.replace("'", "''")
        data.text = data.text.replace('""', '""')
        

        # 샘플 데이터 예측하기
        text1 = [data.text]
        title1 = [data.title]
        combined_text = [text + ' ' + title for text, title in zip(text1, title1)]
        X_sample = loaded_vectorizer.transform(combined_text)
        predictions = loaded_model.predict(X_sample.toarray())
        isad = predictions[0]
        qry = f"INSERT IGNORE INTO joonggo_data(url, platform, issoldout, title, price, text, isad) values('{data.url}', '{data.platform}', '{data.issoldout}', '{data.title}', '{data.price}', '{data.text}', {isad})"
        # print(qry)
        db.execute(qry)
        conn.commit();

    # 크롤링한 페이지를 data db에 저장하는 함수
    @staticmethod
    def AddImg(conn, url, imgs):
        db = conn.cursor();
        for img_url in imgs:
            qry = f"INSERT IGNORE INTO joonggo_img(url, img_url) values('{url}', '{img_url}')"
            print(qry)
            db.execute(qry)
        conn.commit();
    
    # 후보에 넣으려는 링크가 원하는 db에 있는지 체크하는 함수
    @staticmethod
    def CheckData(conn, dbname, url):
        db = conn.cursor();
        qry = f"SELECT url FROM {dbname} WHERE url = '{url}';"
        db.execute(qry)
        res = db.fetchone()
        if res:
            return 0
        else:
            return -1

    # 팔렸는지 안팔렸는지 체크하기 위해서 데이터 가져오는 함수
    @staticmethod
    def GetData(conn):
        db = conn.cursor();
        qry = f"SELECT url,platform FROM joonggo_data WHERE issoldout = 0 LIMIT 10"
        db.execute(qry)
        rows = db.fetchall()
        print(rows)
        print(f"\n\n{len(rows)}개의 데이터를 DB에서 가져와 검수 시작")
        if rows:
            return rows
        else:
            return ""

    # issoldout 수정
    @staticmethod
    def UpdateIssoldout(conn, url, issoldout):
        db = conn.cursor();
        qry = f"UPDATE joonggo_data SET issoldout = '{issoldout}' WHERE url = '{url}'"
        db.execute(qry)
        print(f"\n\n{url}은 현재는 팔린 상태입니다.")





async def temp2(conn):
    db = conn.cursor();
    qry = f"SELECT img_url FROM dream_joonggo.joonggo_img WHERE url = 'https://m.bunjang.co.kr/products/201600871'"
    db.execute(qry)
    row = db.fetchall()
    print(row)




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
        if sys.argv[1] == 'url':
            await Collecturl(connect)
        elif sys.argv[1] == 'data':
            await Collectdata(connect, 0)
        elif sys.argv[1] == 'check':
            await CheckIssoldout(connect)
        elif sys.argv[1] == 'test':
            await temp2(connect)
    finally:
        # WebDriver 종료
        driver.quit()
        connect.close()


asyncio.run(run())
  
# 번개장터는 300페이지를 넘기면 데이터 로딩이 안된다. 중고나라는 125페이지를 넘기면 안된다
# 나머지는 몰루