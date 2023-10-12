from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from .models import JoonggoData, JoonggoImg
from .forms import KeywordForm


def index(request):
    #edit
    joonggo_list = JoonggoData.objects.all()	
    img_list = JoonggoImg.objects.all()	
    context = {'joonggo_list': joonggo_list, 'img_list' : img_list}	# ist의 정보를 context에 담는다.
 
    return render(request,'index.html')

def search(request):
    joonggo = []
    if request.method == 'POST':
        # print(request.POST)
        form = KeywordForm(request.POST)
        # 유효성 검사
        # print(form.is_valid())
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            # print(keyword)
            try:
                db = connection.cursor()
                qry = f"SELECT url, platform, issoldout, title, price, text FROM joonggo_data WHERE title LIKE '{keyword}' limit 10"
                # print(qry)
                db.execute(qry)
                data = db.fetchall()
                # print(data)
                connection.close()
                for res in data:
                    row = {'url': res[0],
                        'platform': res[1],
                        'issoldout': res[2],
                        'title': res[3],
                        'price': res[4],
                        'text': res[5]}
                    joonggo.append(row)
            except:
                connection.rollback()
                print("Failed selecting in Database")
    print(joonggo)
    return render(request, 'search.html', {'joonggo_list': joonggo})