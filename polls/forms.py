from django import forms

class DateForm(forms.Form):
    daterange = forms.CharField(label='Date Range', initial='01.04.2019 - 01.08.2019')

#if DateForm().is_valid():
#    DateForm().save()
