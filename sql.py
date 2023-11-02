import joblib
# 저장된 모델 불러오기
loaded_model = joblib.load('ad_checker.pkl')
loaded_vectorizer = joblib.load('vectorizer.pkl')


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
        qry = f"INSERT IGNORE INTO joonggo_data(url, platform, maincategory, subcategory, title, price, text, issoldout, isad) values('{data.url}', '{data.platform}', '{data.maincategory}', '{data.subcategory}', '{data.title}', '{data.price}', '{data.text}', '{data.issoldout}', {isad})"
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
        
    # 형태소 분석하기 위해 데이터 가져오는 함수
    @staticmethod
    def GetData2(conn, data_id):
        db = conn.cursor();
        qry = f"SELECT url,title,text FROM joonggo_data WHERE id = {data_id}"
        print(qry)
        db.execute(qry)
        rows = db.fetchone()
        # print(rows)
        if rows:
            return rows[0], rows[1], rows[2]
        else:
            return ""

    # issoldout 수정
    @staticmethod
    def UpdateIssoldout(conn, url, issoldout):
        db = conn.cursor();
        qry = f"UPDATE joonggo_data SET issoldout = '{issoldout}' WHERE url = '{url}'"
        db.execute(qry)
        conn.commit()
        print(f"\n\n{url}은 현재는 팔린 상태입니다.")

    # # 카테고리 추가하려고 데이터 가져오는 함수
    # @staticmethod
    # def tempsql(conn):
    #     db = conn.cursor();
    #     qry = f"SELECT id,url,platform FROM joonggo_data WHERE maincategory IS NULL AND id>34500 LIMIT 1;"
    #     db.execute(qry)
    #     row = db.fetchone()
    #     print(row)
    #     if row:
    #         return row[0], row[1], row[2]
    #     else:
    #         return "", ""
        
    # # 카테고리 추가하는 함수
    # @staticmethod
    # def tempsql2(conn, id, maincategory, subcategory):
    #     db = conn.cursor();
    #     qry = f"UPDATE dream_joonggo.joonggo_data SET maincategory = '{maincategory}', subcategory = '{subcategory}' WHERE id = {id};"
    #     print(qry)
    #     db.execute(qry)
    #     conn.commit()

    # url이 일치하는 id를 찾는 함수
    @staticmethod
    def findid(conn, url):
        db = conn.cursor();
        qry = f"select id from dream_joonggo.joonggo_data where (url='{url}')"
        print(qry)
        db.execute(qry)
        row = db.fetchone()
        if row:
            return row[0]
        return 0
    
    # morpheme DB에 형태소를 추가하는 함수
    @staticmethod
    def AddMorpheme(conn, mo):
        db = conn.cursor()
        qry = f"Insert into Morpheme(word) values('{mo.word}')"
        try:
            db.execute(qry)
            conn.commit()
        except:
            return False
        else:
            return True
        
    # morpheme DB에서 특정 형태소의 번호를 가져오는 함수
    @staticmethod
    def FindMid(conn, word):
        db = conn.cursor()    
        qry = f"select id from morpheme where word like '%{word}%'"
        db.execute(qry)
        rows = db.fetchall()
        if rows:
            return rows
        return 0
    
    # inverse DB에 역인덱스 형태로 데이터를 추가하는 함수
    @staticmethod
    def AddInverseItem(conn, morpheme_id, data_id, rcnt):
        db = conn.cursor()
        qry =f"Insert into inverse(morpheme_id,data_id,rcnt) values ({morpheme_id},{data_id},{rcnt})"
        try:
            db.execute(qry)
            conn.commit()
        except:
            return False
        else:
            return True
    
    # inverse DB에서 원하는 형태소가 들어있는 거래데이터의 역인덱스 정보를 가져오는 함수
    @staticmethod
    def FindInv(conn, mid):
        inv_col = list()
        db = conn.cursor()
        qry = f"Select data_id,rcnt from inverse where morpheme_id={mid}"
        db.execute(qry)
        row = db.fetchone()  
        while row:
            inv_col.append(row)
            row = db.fetchone()
        return inv_col
    
    @staticmethod
    def TotalDocumentCount(conn):
        db = conn.cursor()
        qry = "select count(*) from dream_joonggo.joonggo_data"
        db.execute(qry)
        row = db.fetchone()
        return row[0]
    
    @staticmethod
    def UpdateMcnt(conn,url,mcnt):
        db = conn.cursor()
        qry = f"update dream_joonggo.joonggo_data set mcnt={mcnt} where (url='{url}')"
        db.execute(qry)
        conn.commit()

    @staticmethod
    def FindPageByWid(conn, data_id):
        db = conn.cursor()
        qry = f"select title, url, text, mcnt from dream_joonggo.joonggo_data where (id={data_id})"
        db.execute(qry)
        row = db.fetchone()
        return row