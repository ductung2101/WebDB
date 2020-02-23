from django import forms
import pdb, numpy
import pandas as pd
from bootstrap_select import BootstrapSelect
from django_select2.forms import Select2MultipleWidget, Select2Widget

from polls.models import Poll, Media
from polls.data import DataLoader

qs = Media.pdobjects.all().to_dataframe()
candidate_list = qs['candidate'].unique()
CANDIDATES=zip(candidate_list,candidate_list)


class DateForm(forms.Form):
    daterange = forms.CharField(
        label='Date Range', 
        initial='01.04.2019 - 01.08.2019',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    candidates = forms.MultipleChoiceField(
        choices=CANDIDATES,
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )

    # outlets = forms.MultipleChoiceField(
    #     choices=CANDIDATES,
    #     widget = Select2MultipleWidget(
    #         attrs={'class': 'form-control'}
    #     )
    # )

    # state = forms.ChoiceField(
    #     choices=STATES,
    #     widget = Select2Widget(
    #         attrs={'class': 'form-control'}
    #     )
    # )
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
