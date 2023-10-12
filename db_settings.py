# DATABASE 연결
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dream_joonggo', # DB명
        'USER': 'root', # 데이터베이스 계정
        'PASSWORD': 'darkwing991', # 계정 비밀번호
        'HOST': 'localhost', # 데이테베이스 주소(IP)
        'PORT': '3306', # 데이터베이스 포트(보통은 3306)
    }
}

SECRET_KEY = "django-insecure-2uz#p9%w^fq(4@_+x#hccw@$humlgi=wx8m6dfj1@x0!7asx_&";