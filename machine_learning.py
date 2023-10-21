from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import joblib
import time
import asyncio
import pymysql
import sys
import re





async def GetDataset(conn):
    db = conn.cursor();
    qry = f"SELECT title,text,isad FROM joonggo_data WHERE isad = 1 ORDER BY RAND() LIMIT 10000;"
    db.execute(qry)
    rows1 = db.fetchall()
    qry2 = f"SELECT title,text,isad FROM joonggo_data WHERE isad = 0 ORDER BY RAND() LIMIT 10000;"
    db.execute(qry2)
    rows2 = db.fetchall()
    title = []
    text = []
    isad = []
    for i,data in enumerate(rows1):
        title.append(data[0])
        text.append(data[1])
        isad.append(data[2])
    for i,data in enumerate(rows2):
        title.append(data[0])
        text.append(data[1])
        isad.append(data[2])
    # print(title)
    # print(isad)
    print(f"\n\n{len(rows1)}개, {len(rows2)}개의 데이터를 DB에서 가져와 검수 시작")
    if rows1 and rows2:
        return title, text, isad
    else:
        return ""





async def SampleCheck(conn):
    db = conn.cursor();
    qry = f"SELECT title,text,isad FROM joonggo_data WHERE id = 96228;"
    db.execute(qry)
    rows = db.fetchall()
    title = []
    text = []
    isad = []
    for i,data in enumerate(rows):
        title.append(data[0])
        text.append(data[1])
        isad.append(data[2])
    # print(title)
    # print(isad)
    if rows:
        return title, text, isad
    else:
        return ""





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

    if sys.argv[1] == 'create':  
        try:
            texts,titles,labels = await GetDataset(connect)
            # 텍스트 데이터, 제목 데이터, 해당 클래스(광고글/일반글)를 가진 데이터셋을 준비합니다.

            # print(texts[0])
            # print(titles[0])
            # 텍스트와 제목을 합칩니다.
            combined_texts = [text + ' ' + title for text, title in zip(texts, titles)]

            # 데이터셋을 랜덤하게 섞습니다.
            combined_texts_shuffled, labels_shuffled = shuffle(combined_texts, labels)

            # 텍스트와 제목 데이터를 벡터화합니다.
            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(combined_texts_shuffled)

            # 학습용과 테스트용으로 데이터셋을 분리합니다.
            X_train, X_test, y_train, y_test = train_test_split(X, labels_shuffled)

            # 나이브 베이즈 모델을 생성하고 학습합니다.
            naive_bayes = MultinomialNB()
            naive_bayes.fit(X_train.toarray(), y_train)

            # 모델의 성능을 평가합니다.
            accuracy = naive_bayes.score(X_test.toarray(), y_test)
            print("Accuracy:", accuracy)
            
            # 모델 저장하기
            joblib.dump(naive_bayes, 'ad_checker.pkl')
            joblib.dump(vectorizer,'vectorizer.pkl')

            
        finally:
            connect.close()
    elif sys.argv[1] == 'sample':
        text1,title1,label1 = await SampleCheck(connect)
        print(text1)
        print(title1)
        print(label1)
        # 저장된 모델 불러오기
        loaded_model = joblib.load('ad_checker.pkl')
        loaded_vectorizer = joblib.load('vectorizer.pkl')

        # 샘플 데이터 예측하기
        # text = ["샘플 광고글입니다."]
        # title = ["샘플 광고제목"]
        combined_text = [text + ' ' + title for text, title in zip(text1, title1)]
        X_sample = loaded_vectorizer.transform(combined_text)
        predictions = loaded_model.predict(X_sample.toarray())

        print("Predictions:", predictions)


asyncio.run(run())

