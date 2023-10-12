from django import forms

class KeywordForm(forms.Form):
    keyword = forms.CharField()