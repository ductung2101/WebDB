from django import forms

class DateForm(forms.Form):
    start_date = forms.CharField(label='Start Date', max_length=100, initial = "2019-01-01")
    end_date = forms.CharField(label='End Date', max_length=100, initial = "2019-05-01")