from django import forms
import pdb, numpy
import pandas as pd
import numpy as np
from bootstrap_select import BootstrapSelect
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import Poll, Media
from .data import DataLoader

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
        initial='01.01.2020 - 01.03.2020',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    candidates = forms.MultipleChoiceField(
        choices=CANDIDATES,
        required = False,
        # initial = DataLoader.instance().get_initial_candidates(),
        initial = DataLoader.instance().get_initial_candidates(),
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )
    outlets = forms.MultipleChoiceField(
        choices=OUTLETS,
        required = False,
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        ),
        initial = DataLoader.instance().get_outlets_list()
    )
    state = forms.ChoiceField(
        choices=STATES,
        required = False,
        initial = "National",
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )

class CandidatesForm(forms.Form):
    # date range
    daterange = forms.CharField(
        label='Date Range', 
        initial='01.01.2020 - 01.03.2020',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    candidates = forms.ChoiceField(
        choices=CANDIDATES,
        required = False,
        initial = DataLoader.instance().get_initial_candidates(),
        widget = Select2Widget(
            attrs={'class': 'form-control'}
        )
    )
    outlets = forms.MultipleChoiceField(
        choices=OUTLETS,
        required = False,
        initial = DataLoader.instance().get_outlets_list(),
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
        initial='01.01.2020 - 01.03.2020',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    candidates = forms.MultipleChoiceField(
        choices=CANDIDATES,
        required = False,
        initial = DataLoader.instance().get_initial_candidates(),
        widget = Select2MultipleWidget(
            attrs={'class': 'form-control'}
        )
    )
    outlets = forms.ChoiceField(
        choices=OUTLETS,
        required = False,
        initial = DataLoader.instance().get_outlets_list(),
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