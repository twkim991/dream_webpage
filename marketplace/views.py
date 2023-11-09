from django.shortcuts import render
from django.db import connection
from Searcher import Searcher
from .forms import KeywordForm
from django.core.cache import cache

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
    print('search 페이지로 가는 중')
    joonggo = []
    if request.method == 'GET':
        # print(request.GET)

        cat = request.GET.get('category', 'all')
        keyword = request.GET.get('keyword', '*')
        id_list = list()
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
        print(f'\n{category}\n{keyword}\n')
        # db에서 중고거래 데이터를 가져온다
        try:
            db = connection.cursor()
            qry = ''
            if category == 'all':
                if keyword == '*':
                    qry = f"SELECT url, platform, issoldout, title, price, text, isad, id FROM dream_joonggo.joonggo_data ORDER BY id LIMIT 1000;"
                else:
                    id_list = Searcher.Search(connection,keyword) 
                    print(id_list[0].url)
                    qry = f"""SELECT url, platform, issoldout, title, price, text, isad, id FROM dream_joonggo.joonggo_data WHERE url IN ({','.join("'" + str(i.url) + "'" for i in id_list)}) ORDER BY id LIMIT 1000;"""
            else:
                if keyword == '*':
                    qry = f"SELECT url, platform, issoldout, title, price, text, isad, id FROM dream_joonggo.joonggo_data WHERE maincategory = '{category}' OR subcategory = '{category}' ORDER BY id LIMIT 1000;"
                else:
                    id_list = Searcher.Search(connection,keyword) 
                    print(id_list[0].url)
                    qry = f"""SELECT url, platform, issoldout, title, price, text, isad, id FROM dream_joonggo.joonggo_data WHERE url IN ({','.join("'" + str(i.url) + "'" for i in id_list)}) AND (maincategory = '{category}' OR subcategory = '{category}') ORDER BY id LIMIT 1000;"""
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

            if keyword != '*':
                for dict2 in data:
                    for dict1 in id_list:
                        if dict1.url == dict2[0]:
                            merged_dict = {
                                'url': dict2[0],
                                'platform': dict2[1],
                                'title' : dict2[3],
                                'price' : dict2[4],
                                'text' : dict2[5],
                                'isad' : dict2[6],
                                'issoldout' : dict2[2],
                                'score' : dict1.score,
                                'id' : dict2[7],
                                'imgurl': imgdata_dict.get(dict2[0],[])
                            }
                            joonggo.append(merged_dict)
            else:
                for dict2 in data:
                    merged_dict = {
                        'url': dict2[0],
                        'platform': dict2[1],
                        'title' : dict2[3],
                        'price' : dict2[4],
                        'text' : dict2[5],
                        'isad' : dict2[6],
                        'issoldout' : dict2[2],
                        'score' : 0,
                        'id' : dict2[7],
                        'imgurl': imgdata_dict.get(dict2[0],[])
                    }
                    joonggo.append(merged_dict)

        except Exception as err:
            connection.rollback()
            print("에러 발생")
            print(err)
        
        # print(joonggo[0])
        # 데이터를 캐시에 저장
        cache.set('joonggo_list', joonggo, timeout=3600)  # 1시간 동안 유효
        return render(request, 'search.html', {'joonggo_list': joonggo})
    
def reorder(request):
    print('search/ordered 페이지로 가는 중')
    joonggo = []
    # 캐시에서 중고거래 데이터를 가져옴
    not_sorted = cache.get('joonggo_list')
    # 캐시에 저장된 데이터가 만료된 상태면 db에서 다시 데이터를 가져옴
    if not_sorted is None:
        print(request.GET)

        cat = request.GET.get('category', 'all')
        keyword = request.GET.get('keyword', '*')
        id_list = list()
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
        print(f'\n{category}\n{keyword}\n')
        # db에서 중고거래 데이터를 가져온다
        try:
            db = connection.cursor()
            qry = ''
            if category == 'all':
                if keyword == '*':
                    qry = f"SELECT url, platform, issoldout, title, price, text, isad FROM dream_joonggo.joonggo_data ORDER BY id LIMIT 1000;"
                else:
                    id_list = Searcher.Search(connection,keyword) 
                    print(id_list[0].url)
                    qry = f"""SELECT url, platform, issoldout, title, price, text, isad, id FROM dream_joonggo.joonggo_data WHERE url IN ({','.join("'" + str(i.url) + "'" for i in id_list)}) ORDER BY id LIMIT 1000;"""
            else:
                if keyword == '*':
                    qry = f"SELECT url, platform, issoldout, title, price, text, isad FROM dream_joonggo.joonggo_data WHERE maincategory = '{category}' OR subcategory = '{category}' ORDER BY id LIMIT 1000;"
                else:
                    id_list = Searcher.Search(connection,keyword) 
                    print(id_list[0].url)
                    qry = f"""SELECT url, platform, issoldout, title, price, text, isad, id FROM dream_joonggo.joonggo_data WHERE url IN ({','.join("'" + str(i.url) + "'" for i in id_list)}) AND (maincategory = '{category}' OR subcategory = '{category}') ORDER BY id LIMIT 1000;"""
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

            for dict2 in data:
                    for dict1 in id_list:
                        if dict1.url == dict2[0]:
                            merged_dict = {
                                'url': dict2[0],
                                'platform': dict2[1],
                                'title' : dict2[3],
                                'price' : dict2[4],
                                'text' : dict2[5],
                                'isad' : dict2[6],
                                'issoldout' : dict2[2],
                                'score' : dict1.score,
                                'id' : dict2[7],
                                'imgurl': imgdata_dict.get(dict2[0],[])
                            }
                            joonggo.append(merged_dict)
        except Exception as err:
            connection.rollback()
            print("에러 발생")
            print(err)
        
        # print(joonggo[0])
        # 데이터를 캐시에 저장
        cache.set('joonggo_list', joonggo, timeout=3600)  # 1시간 동안 유효
        return render(request, 'search.html', {'joonggo_list': joonggo})
    # 이외에는 캐시 데이터를 가져와서 정렬만 한다.
    else:
        sort_option = request.GET.get('sort', 'id')
        sort_option2 = request.GET.get('sort2', 'ASCENDING')
        if sort_option2 == 'ASCENDING':
            joonggo = sorted(not_sorted, key=lambda x: x[f'{sort_option}'])
        elif sort_option2 == 'DESCENDING':
            joonggo = sorted(not_sorted, key=lambda x: x[f'{sort_option}'], reverse=True)
        
        # print(joonggo[0])
        return render(request, 'search.html', {'joonggo_list': joonggo})