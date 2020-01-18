from django import forms

class DateForm(forms.Form):
    start_date = forms.CharField(label='Start Date', max_length=100 , initial = "2019-01-01")
    end_date = forms.CharField(label='End Date', max_length=100, initial = "2019-05-01")

    daterange = forms.CharField(label='Date Range', initial='01.04.2019 - 01.08.2019')

#if DateForm().is_valid():
#    DateForm().save()
