import datetime
from django.db import models
from django.utils import timezone
# add to read CSV
import csv
import pandas as pd
from django_pandas.managers import DataFrameManager


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
    return datetime.datetime.strptime(str, '%m/%d/%y')


class Poll(models.Model):
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

'''
#comment to disable loading data, uncomment to update data manually
file_path = "C:\\Users\\ndtun\\PycharmProjects\\WebDB\\WebDBSite\\president_primary_polls.csv"
temp = pd.read_csv(file_path, sep=',', quotechar='"')
with open(file_path, 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    header = next(reader)
    i=0
    for row in reader:
        i+=1
        print(i)
        if row[0] != "question_id":
            _, created = Poll.objects.get_or_create(
                question_id=row[0],
                poll_id=row[1],
                cycle=row[2],
                state=row[3],
                pollster_id=row[4],
                pollster=row[5],
                sponsor_ids=row[6],
                sponsors=row[7],
                display_name=row[8],
                pollster_rating_id=row[9],
                pollster_rating_name=row[10],
                fte_grade=row[11],
                sample_size=row[12],
                population=row[13],
                population_full=row[14],
                methodology=row[15],
                office_type=row[16],
                start_date=convertDateField(row[17]),
                end_date=convertDateField(row[18]),
                sponsor_candidate=row[19],
                internal=row[20],
                partisan=row[21],
                tracking=row[22],
                nationwide_batch=row[23],
                created_at=convertingdatetimefield(row[24]),
                notes=row[25],
                url=row[26],
                stage=row[27],
                party=row[28],
                answer=row[29],
                candidate_id=row[30],
                candidate_name=row[31],
                pct=row[32]
            )
'''