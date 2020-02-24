from django import forms
import pdb, numpy
import pandas as pd
import numpy as np
from bootstrap_select import BootstrapSelect
from django_select2.forms import Select2MultipleWidget, Select2Widget

from polls.models import Poll, Media
from polls.data import DataLoader

# DataLoader()
CANDIDATES=list(zip(DataLoader.instance().get_candidate_list(),
    DataLoader.instance().get_candidate_list()))

OUTLETS=list(zip(DataLoader.instance().get_outlets_list(),
    DataLoader.instance().get_outlets_list()))

states = DataLoader.instance().get_polls()["state"].unique()
states = np.sort(states)
states = list(map(lambda x: "National" if x == "" else x, states))
STATES=list(zip(states, states))

class NationalForm(forms.Form):
    # date range
    daterange = forms.CharField(
        label='Date Range', 
        initial='01.04.2019 - 01.08.2019',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    candidates = forms.MultipleChoiceField(
        choices=CANDIDATES,
        required = False,
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )
    outlets = forms.MultipleChoiceField(
        choices=OUTLETS,
        required = False,
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )

    state = forms.ChoiceField(
        choices=STATES,
        required = False,
        initial = "",
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )

class CandidatesForm(forms.Form):
    # date range
    daterange = forms.CharField(
        label='Date Range', 
        initial='01.04.2019 - 01.08.2019',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    candidates = forms.ChoiceField(
        choices=CANDIDATES,
        required = False,
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )
    outlets = forms.MultipleChoiceField(
        choices=OUTLETS,
        required = False,
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )
    state = forms.ChoiceField(
        choices=STATES,
        required = False,
        initial = "",
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )

class OutletsForm(forms.Form):
    # date range
    daterange = forms.CharField(
        label='Date Range', 
        initial='01.04.2019 - 01.08.2019',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    candidates = forms.MultipleChoiceField(
        choices=CANDIDATES,
        required = False,
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )
    outlets = forms.ChoiceField(
        choices=OUTLETS,
        required = False,
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )
    state = forms.ChoiceField(
        choices=STATES,
        required = False,
        initial = "",
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )