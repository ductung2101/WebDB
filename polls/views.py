from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, FormView
from chartjs.views.lines import BaseLineChartView
from chartjs.views.lines import HighchartPlotLineChartView
from random import randint
from polls.models import Poll
from polls.forms import DateForm
import datetime
import pytz
import numpy as np
import pandas as pd
import os
from django import forms
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def sub(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def correlation_matrix_post(request, *args, **kwargs):
    form = DateForm(request.POST)
    if form.is_valid():
        print('yes done')
    return redirect('correlation_matrix', start_date = form['start_date'].value(), end_date = form['end_date'].value())

def correlation_matix(request, start_date = None, end_date = None):
    df = pd.read_csv(os.path.join("polls", "corr_data.csv"))
    df['Date'] = pd.to_datetime(df['Date'])
    if start_date is not None and end_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        mask = (df['Date'] > start_date) & (df['Date'] <= end_date)
        df = df.loc[mask]
    df["pct"] = df["pct"].astype(float)
    df["Value"] = df["Value"].astype(float)
    colnames = df["Candidate"].unique()
    rownames = df["Series"].unique()
    cor_mat = pd.DataFrame(columns=colnames, index=rownames)
    for col in colnames:
        for row in rownames:
            subset = df[df["Candidate"] == col]
            subset = subset[subset["Series"] == row]

            cor_mat.at[row, col] = np.corrcoef(subset["Value"], subset["pct"])[0, 1]
            if cor_mat.at[row, col] != cor_mat.at[row, col] or cor_mat.at[row, col] == 0 or cor_mat.at[
                row, col] == -1 or cor_mat.at[row, col] == 1:
                cor_mat.at[row, col] = "-"

    return HttpResponse(cor_mat.to_html())


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 0, 0, 13, 65]]

class PollJSONView(BaseLineChartView):

    def post(self, request, *args, **kwargs):
        form = DateForm(request.POST)
        if form.is_valid():
            print('yes done')
        import pdb
        #pdb.set_trace()
        return redirect('poll_json', start_date = form['start_date'].value(),
                                    end_date = form['end_date'].value())

    def do_compute(self):

        #self.new_start_date = forms.CharField(label='Start Date', max_length=100, initial="2019-01-01")
        self.n_weeks = self.kwargs.get('n_weeks')



        self.start_date = pytz.utc.localize(datetime.datetime.strptime(
            self.kwargs.get('start_date'), "%Y-%m-%d"))
        #self.start_date = pytz.utc.localize(datetime.datetime.strptime(
         #  self.new_start_date.initial, "%Y-%m-%d"))
        self.end_date = pytz.utc.localize(datetime.datetime.strptime(
            self.kwargs.get('end_date'), "%Y-%m-%d"))

        #print('works', self.start_date, self.end_date)
        qs = Poll.pdobjects.all()  # Use the Pandas Manager
        self.df = qs.to_dataframe()
        self.df["pct"] = self.df["pct"].astype(float)
        self.df["create_date"] = pd.to_datetime(self.df["created_at"],
                                                infer_datetime_format=True)
        self.df["create_week"] = (self.df['create_date'] - pd.to_timedelta( \
            self.df['create_date'].dt.dayofweek, unit='d') + np.timedelta64(7, 'D')) \
            .dt.normalize()
        # TODO: insert better filtering here
        self.df_subset = self.df[self.df["party"] == "DEM"]
        self.df_pivot = self.df_subset.pivot_table(
            values="pct", index="create_week", columns="candidate_name",
            aggfunc=np.mean).fillna(0)#.iloc[-self.n_weeks:]
        self.df_pivot = self.df_pivot[
            (self.df_pivot.index <= self.end_date) & 
            (self.df_pivot.index >= self.start_date)]
        # import pdb; pdb.set_trace()

    def get_labels(self):
        self.do_compute()
        """Return n_weeks labels for the x-axis."""
        return list(self.df_pivot.index.strftime("%d.%m.%Y"))

    def get_providers(self):
        """Return names of selected candidates."""
        candidates = self.df_subset["candidate_name"].unique()
        can_selected = []
        for can in candidates:
            if (self.df_pivot[can] == 0).mean() < 0.5 and \
                    self.df_pivot[can].iloc[-1] > 1:
                can_selected.append(can)
        return can_selected

    def get_data(self):
        """Return timeseries to plot for each candidate."""
        can_selected = self.get_providers()
        lst_selected = []
        for can in can_selected:
            lst_selected.append(list(self.df_pivot[can]))
        return lst_selected

main_page = FormView.as_view(template_name='index.html', 
    form_class = DateForm, success_url=u'')
line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = LineChartJSONView.as_view()
poll_json = PollJSONView.as_view()
