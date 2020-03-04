import datetime
from django.db import models
from django.utils import timezone
import csv
import pandas as pd
from django_pandas.managers import DataFrameManager
import requests
from requests.auth import HTTPDigestAuth
import json
import pdb


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


def convertingdatetimefield(str):
    return datetime.datetime.strptime(str, '%m/%d/%y %H:%M')


def convertDateField(str):
    #in poll data
    if "/" in str:
        return datetime.datetime.strptime(str, '%m/%d/%y')
    #in media data
    if "-" in str:
        temp = str[0:10]
        return datetime.datetime.strptime(temp, '%Y-%m-%d')


class Poll(models.Model):
    objects = models.Manager()
    pdobjects = DataFrameManager()
    question_id = models.CharField(max_length=200)
    poll_id = models.CharField(max_length=200)
    cycle = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    pollster_id = models.CharField(max_length=200)
    pollster = models.CharField(max_length=200)
    sponsor_ids = models.CharField(max_length=200)
    sponsors = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    pollster_rating_id = models.CharField(max_length=200)
    pollster_rating_name = models.CharField(max_length=200)
    fte_grade = models.CharField(max_length=200)
    sample_size = models.BigIntegerField()
    population = models.CharField(max_length=200)
    population_full = models.CharField(max_length=200)
    methodology = models.CharField(max_length=200)
    office_type = models.CharField(max_length=200)
    start_date = models.DateField(max_length=200)
    end_date = models.DateField(max_length=200)
    sponsor_candidate = models.CharField(max_length=200)
    internal = models.CharField(max_length=200)
    partisan = models.CharField(max_length=200)
    tracking = models.CharField(max_length=200)
    nationwide_batch = models.CharField(max_length=200)
    created_at = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    stage = models.CharField(max_length=200)
    party = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    candidate_id = models.CharField(max_length=200)
    candidate_name = models.CharField(max_length=200)
    pct = models.FloatField()
    #class Meta:
        #order_with_respect_to = 'start_date'


class Media(models.Model):
    objects = models.Manager()
    pdobjects = DataFrameManager()
    media_id = models.IntegerField()
    answer = models.CharField(max_length=200)
    create_week = models.DateField()
    pct = models.FloatField()
    date = models.DateField()
    series = models.CharField(max_length=200)
    value = models.FloatField()
    candidate = models.CharField(max_length=200)
    state = models.CharField(max_length=100)


'''
file_path = "C:\\Users\\ndtun\\PycharmProjects\\WebDB\\WebDBSite\\polls\\corr_data.csv"
temp = pd.read_csv(file_path, sep=',', quotechar='"')
with open(file_path, 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    header = next(reader)
    for row in reader:
        
        media = Media.objects.get(media_id=int(row[0]))
        if media is not None:
            media.state = row[3]
            media.save()
'''