# DATABASE 연결
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'dream_joonggo',
    'HOST': 'aws.connect.psdb.cloud',
    'PORT': '3306',
    'USER': 'b3m09mx2prgyo1smqr5n',
    'PASSWORD': 'pscale_pw_E7GlHv7exqCP6GcOavy5YXemfLllsn0i41w1eP4v7qn',
    'OPTIONS': {'ssl': {'ca': 'C:\WORK\dream_webpage\cacert.pem'}, 
                'charset': 'utf8mb4'}
  }
}

SECRET_KEY = "django-insecure-2uz#p9%w^fq(4@_+x#hccw@$humlgi=wx8m6dfj1@x0!7asx_&";