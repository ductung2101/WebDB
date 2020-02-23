from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView, FormView
from chartjs.views.lines import BaseLineChartView
from chartjs.views.lines import HighchartPlotLineChartView
from random import randint
from polls.models import Poll, Media
from polls.forms import DateForm
import datetime, requests, csv
import pytz
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from plotly.offline import plot
from django import forms
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView
from django.shortcuts import redirect


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


def parse_daterange(daterange):
    dates = [("-").join(y.strip().split(".")[::-1]) for y in daterange.split("-")]
    start_date = dates[0]
    end_date = dates[1]
    return start_date, end_date



# auto update poll using requests
def auto_update_president_polls():
    url = 'https://projects.fivethirtyeight.com/polls-page/president_primary_polls.csv'
    r = requests.get(url, allow_redirects=True)
    open('polls\\new_file.csv', 'wb').write(r.content)
    temp = pd.read_csv('polls\\new_file.csv', sep=',', quotechar='"')
    with open('polls\\new_file.csv', 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        header = next(reader)
        total_row_new_record = sum(1 for line in csv_file)
        print(total_row_new_record)
        total_new_records_count = total_row_new_record - Poll.objects.count()
        print(total_new_records_count)
        csv_file.seek(0)
        header = next(reader)
        subsequent_no_new_poll = 0
        for row in reader:
            current_poll_id = row[1]
            current_candidate_id = row[30]
            # print(current_poll_id)
            if Poll.objects.filter(poll_id=current_poll_id, candidate_id=current_candidate_id).count() == 0:
                subsequent_no_new_poll = 0
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
                if type(created) != bool:
                    created.save()
            else:
                subsequent_no_new_poll += 1
            if subsequent_no_new_poll == 200:
                break
    # problem: date is sorted decreasingly, if new records are written, they are added to the end
    # -> need to sort whole DB due to start_date -> not optimal, use poll_id instead.
    # compare current file with existing model data
        #pdb.set_trace()
    return False


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def sub(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


'''class CorrelationView(View):
    def post(self, request, *args, **kwargs):
        form = DateForm(request.POST)
        if form.is_valid():
            print('yes done')
        return redirect('correlation_view', start_date=form['start_date'].value(), end_date=form['end_date'].value())

    @classmethod
    def make_table(cls, start_date=None, end_date=None):
        # try to replace df with model.Media
        qs = Media.pdobjects.all()
        df = qs.to_dataframe()

        print("qs", qs[0])
        if start_date is not None and end_date is not None:
            # change type of start_date to be same type with Media.date
            start_date_new = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_new = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            mask = (df['date'] > start_date_new) & (df['date'] <= end_date_new)
            df = df.loc[mask]
        df["pct"] = df["pct"].astype(float)
        df["value"] = df["value"].astype(float)
        # import pdb; pdb.set_trace()
        colnames = df["candidate"].unique()
        rownames = df["series"].unique()
        cor_mat = pd.DataFrame(columns=colnames, index=rownames)
        for col in colnames:
            for row in rownames:
                subset = df[df["candidate"] == col]
                subset = subset[subset["series"] == row]

                cor_mat.at[row, col] = np.corrcoef(subset["value"], subset["pct"])[0, 1]
                if cor_mat.at[row, col] != cor_mat.at[row, col] or cor_mat.at[row, col] == 0 or cor_mat.at[
                    row, col] == -1 or cor_mat.at[row, col] == 1:
                    cor_mat.at[row, col] = "-"

        return cor_mat.to_html()

    def get(self, request, start_date=None, end_date=None):
        cor_mat = self.make_table(start_date, end_date)
        return HttpResponse(cor_mat)'''


class PollJSONView(BaseLineChartView):
    def post(self, request, *args, **kwargs):
        form = DateForm(request.POST)
        start_date, end_date = parse_daterange(form["daterange"].value())
        return redirect('poll_json', start_date=start_date, end_date=end_date)

    def do_compute(self):
        self.n_weeks = self.kwargs.get('n_weeks')
        self.start_date = pytz.utc.localize(datetime.datetime.strptime(
            self.kwargs.get('start_date'), "%Y-%m-%d"))
        self.end_date = pytz.utc.localize(datetime.datetime.strptime(
            self.kwargs.get('end_date'), "%Y-%m-%d"))

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
            aggfunc=np.mean).fillna(0)  # .iloc[-self.n_weeks:]
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


class GDeltAnalysisPlot:
    def __init__(self, start_date=None, end_date=None, selected_candidates=None, selected_series=None):
        qs = Media.pdobjects.all()
        self.date_filtered_df = qs.to_dataframe()
        if start_date is not None and end_date is not None:
            # change type of start_date to be same type with Media.date
            start_date_new = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_new = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            mask = (self.date_filtered_df['date'] > start_date_new) & (self.date_filtered_df['date'] <= end_date_new)
            self.date_filtered_df = self.date_filtered_df.loc[mask]

        self.date_filtered_df["pct"] = self.date_filtered_df["pct"].astype(float)
        self.date_filtered_df["value"] = self.date_filtered_df["value"].astype(float)

        if selected_candidates is None:
            self.candidates = self.date_filtered_df["candidate"].unique()
        else:
            self.candidates = selected_candidates

        if selected_series is None:
            self.series = self.date_filtered_df["series"].unique()
        else:
            self.series = selected_series;

        self.min_cor = 2
        self.min_cand = None
        self.min_ser = None
        self.max_cor = -2
        self.max_cand = None
        self.max_ser = None
        self.cor_mat = self.make_cor_mat()

    def make_cor_mat(self):
        cor_mat = pd.DataFrame(columns=self.candidates, index=self.series)
        for col in self.candidates:
            for row in self.series:
                subset = self.date_filtered_df[self.date_filtered_df["candidate"] == col]
                subset = subset[subset["series"] == row]

                cor_mat.at[row, col] = np.corrcoef(subset["value"], subset["pct"])[0, 1]
                if cor_mat.at[row, col] != cor_mat.at[row, col] or cor_mat.at[row, col] == 0 or cor_mat.at[row, col] \
                        == -1 or cor_mat.at[row, col] == 1:
                    cor_mat.at[row, col] = None
                if cor_mat.at[row, col] is not None and cor_mat.at[row, col] < self.min_cor:
                    self.min_cor = cor_mat.at[row, col]
                    self.min_cand = col
                    self.min_ser = row
                if cor_mat.at[row, col] is not None and cor_mat.at[row, col] > self.max_cor:
                    self.max_cor = cor_mat.at[row, col]
                    self.max_cand = col
                    self.max_ser = row

        return cor_mat

    def make_heatmap(self):
        hover = []
        for i in range(len(self.series)):
            hover.append([('The impact of ' + self.series[i] + ' on ' + self.candidates[j] + "'s polls is " +
                           ('positive' if (self.cor_mat.values[
                                               i, j] > 0) else 'negative')
                           + ' with a correlation of ' + str(self.cor_mat.values[i, j]))
                          if self.cor_mat.values[
                                 i, j] is not None else 'There is not enough data to calculate correlation'
                          for j in range(len(self.candidates))]
                         )
        hm = go.Heatmap(
            z=self.cor_mat.values,
            x=self.candidates,
            y=self.series,
            colorscale=["red", "white", "green"],
            text=hover,
            hoverinfo='text')

        fig = go.Figure(data=hm)

        plot_div = plot(fig, output_type='div', include_plotlyjs=True)

        return plot_div

    def make_radar_chart(self):
        series_a = self.date_filtered_df['series'] == 'MSNBC'
        series_b = self.date_filtered_df['series'] == 'CNN'
        categories = self.date_filtered_df[series_a]['candidate'][:5]
        chart_data_a = self.date_filtered_df[series_a].groupby(['candidate'])['value'].agg('mean')[:5]
        chart_data_b = self.date_filtered_df[series_b].groupby(['candidate'])['value'].agg('mean')[:5]
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=chart_data_a,
            theta=categories,
            fill='toself',
            name='Product A'
        ))
        fig.add_trace(go.Scatterpolar(
            r=chart_data_b,
            theta=categories,
            fill='toself',
            name='Product B'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=True)
        return plot_div

    def make_scatter_plot(self):
        df = self.date_filtered_df[self.date_filtered_df.candidate == 'Warren']
        df = df[self.date_filtered_df.series == 'FOXNEWS']
        fig = px.scatter(df, x="value", y="pct", trendline="ols")

        plot_div = plot(fig, output_type='div', include_plotlyjs=True)
        return plot_div


class MainPageView(FormView):
    template_name = 'index.html'
    form_class = DateForm
    success_url = '.'

    # add items to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = super().get_form()

        print(form["candidates"].value())

        start_date, end_date = parse_daterange(form["daterange"].value())

        plot_data = GDeltAnalysisPlot(start_date, end_date)

        # make heatmap
        context['heatmap'] = plot_data.make_heatmap()

        # make radar
        context['radar'] = plot_data.make_radar_chart()

        # make scatter
        context['scatter'] = plot_data.make_scatter_plot()

        # make corr matrix
        context['corr_table'] = plot_data.cor_mat.to_html

        # get minmax data
        context['cor_min_val'] = plot_data.min_cor
        context['cor_min_candidate'] = plot_data.min_cand
        context['cor_min_series'] = plot_data.min_ser
        context['cor_max_val'] = plot_data.max_cor
        context['cor_max_candidate'] = plot_data.max_cand
        context['cor_max_series'] = plot_data.max_ser

        return context

    def form_valid(self, form):
        return super().get(form)


auto_update_president_polls()
main_page = MainPageView.as_view()
poll_json_view = PollJSONView.as_view()
# correlation_view = CorrelationView.as_view()
# gdelt_heatmap_view = GDeltAnalysisPlotView.as_view()
