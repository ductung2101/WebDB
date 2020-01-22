from django import forms
from bootstrap_select import BootstrapSelect
from django_select2.forms import Select2MultipleWidget

CANDIDATES=(
    (0, 'aabsabdsiad'),
    (1, 'bsdiasjdasdamsd'),
    (2, 'c'),
    (3, 'd'),
)

class DateForm(forms.Form):
    daterange = forms.CharField(label='Date Range', initial='01.04.2019 - 01.08.2019')
    candidates = forms.MultipleChoiceField(
        choices=CANDIDATES,
        widget = Select2MultipleWidget)
        # widget=forms.CheckboxSelectMultiple()
    # candidates = forms.CharField(label = "Candidates", 
    #     widget = BootstrapSelect(
    #         attrs={
    #             'class' : 'selectpicker',
    #             'multiple' : ''},
    #         choices = CANDIDATES),
    #     required = False)

#if DateForm().is_valid():
#    DateForm().save()
