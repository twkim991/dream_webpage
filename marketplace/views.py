from django.shortcuts import render
from django.db import connection
from Searcher import Searcher
from .forms import KeywordForm

def index(request):
    joonggo = []
    try:
        db = connection.cursor()
        qry = f"SELECT url, platform, issoldout, title, price FROM dream_joonggo.joonggo_data ORDER BY ID DESC LIMIT 100;"
        db.execute(qry)
        data = db.fetchall()
        # print(data)
        connection.close()

        for res in data:
            url = res[0]
            # print(imgdata_dict.get(url, []))
            row = {'url': url,
                'platform': res[1],
                'issoldout': res[2],
                'title': res[3],
                'price': res[4]}
            joonggo.append(row)
    except Exception as err:
        connection.rollback()
        print("에러 발생")
        print(err)
        
    # print(joonggo[0])
    return render(request, 'index.html', {'joonggo_list': joonggo})

def search(request):
    joonggo = []
    if request.method == 'POST':
        # print(request.POST)
        form = KeywordForm(request.POST)
        # print(form)
        # 유효성 검사
        print(form.is_valid())
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            print(keyword)
            # db에서 중고거래 데이터를 가져온다
            try:
                db = connection.cursor()
                id_list = Searcher.Search(connection,keyword) 
                # print(id_list[0])
                qry = f"""SELECT url, platform, issoldout, title, price, text, isad FROM dream_joonggo.joonggo_data WHERE url IN ({','.join("'" + str(i) + "'" for i in id_list)}) ORDER BY FIELD (url,{','.join("'" + str(i) + "'" for i in id_list)}) LIMIT 1000;"""
                # print(qry)
                db.execute(qry)
                data = db.fetchall()
                # print(data[0])
                connection.close()

                # 여기에 이미지 정보도 같이 가져와야한다.
                db2 = connection.cursor()
                qry2 = "SELECT url, img_url FROM dream_joonggo.joonggo_img WHERE url IN (%s)"
                url_list = [res[0] for res in data]
                placeholders = ', '.join(['%s'] * len(url_list))
                qry2 = qry2 % placeholders
                db2.execute(qry2, url_list)
                imgdata = db2.fetchall()

                # 이미지 데이터를 그룹화하기 위한 딕셔너리 생성
                imgdata_dict = {}
                try:
                    for img in imgdata:
                        url = img[0]
                        imgurl = img[1]
                        if url not in imgdata_dict:
                            imgdata_dict[url] = []
                        imgdata_dict[url].append(imgurl)
                except Exception as err:
                    print(err)

                # print(imgdata_dict)

                for res in data:
                    url = res[0]
                    # print(imgdata_dict.get(url, []))
                    row = {'url': url,
                        'platform': res[1],
                        'issoldout': res[2],
                        'title': res[3],
                        'price': res[4],
                        'text': res[5],
                        'isad': res[6],
                        'imgurl': imgdata_dict.get(url, [])}
                    joonggo.append(row)
            except Exception as err:
                connection.rollback()
                print("에러 발생")
                print(err)
            
        # print(joonggo[0])
        return render(request, 'search.html', {'joonggo_list': joonggo})
    elif request.method == 'GET':
        cat = request.GET.get('category')
        print(cat)
        category = ''
        if cat == "001":
            category = '데스크탑/본체'
        elif cat == "002":
            category = '모니터'
        elif cat == "003":
            category = 'CPU/메인보드'
        elif cat == "004":
            category = '메모리/VGA'
        elif cat == "005":
            category = 'HDD/SDD/ODD'
        elif cat == "006":
            category = "케이스/파워/쿨러"
        elif cat == "007":
            category = "프린터/복합기/잉크/토너"
        elif cat == "008":
            category = '소모품'
        else:
            category = 'all'
        # db에서 중고거래 데이터를 가져온다
        try:
            db = connection.cursor()
            if category == 'all':
                qry = f"SELECT url, platform, issoldout, title, price, text, isad FROM dream_joonggo.joonggo_data LIMIT 1000;"
            else:
                qry = f"SELECT url, platform, issoldout, title, price, text, isad FROM dream_joonggo.joonggo_data WHERE maincategory = '{category}' OR subcategory = '{category}' LIMIT 1000;"
            db.execute(qry)
            data = db.fetchall()
            # print(data)
            connection.close()

            # 여기에 이미지 정보도 같이 가져와야한다.
            db2 = connection.cursor()
            qry2 = "SELECT url, img_url FROM dream_joonggo.joonggo_img WHERE url IN (%s)"
            url_list = [res[0] for res in data]
            placeholders = ', '.join(['%s'] * len(url_list))
            qry2 = qry2 % placeholders
            db2.execute(qry2, url_list)
            imgdata = db2.fetchall()

            # 이미지 데이터를 그룹화하기 위한 딕셔너리 생성
            imgdata_dict = {}
            try:
                for img in imgdata:
                    url = img[0]
                    imgurl = img[1]
                    if url not in imgdata_dict:
                        imgdata_dict[url] = []
                    imgdata_dict[url].append(imgurl)
            except Exception as err:
                print(err)

            # print(imgdata_dict)

            for res in data:
                url = res[0]
                # print(imgdata_dict.get(url, []))
                row = {'url': url,
                    'platform': res[1],
                    'issoldout': res[2],
                    'title': res[3],
                    'price': res[4],
                    'text': res[5],
                    'isad': res[6],
                    'imgurl': imgdata_dict.get(url, [])}
                joonggo.append(row)
        except Exception as err:
            connection.rollback()
            print("에러 발생")
            print(err)
        
        # print(joonggo[0])
        return render(request, 'search.html', {'joonggo_list': joonggo})