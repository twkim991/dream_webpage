# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Candidate(models.Model):
    url = models.CharField(unique=True, max_length=512, blank=True, null=True)
    platform = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'candidate'


class JoonggoData(models.Model):
    url = models.CharField(unique=True, max_length=512)
    platform = models.CharField(max_length=32, blank=True, null=True)
    issoldout = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    text = models.CharField(max_length=4192, blank=True, null=True)
    mcnt = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'joonggo_data'


class JoonggoImg(models.Model):
    url = models.CharField(max_length=512)
    img_url = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'joonggo_img'