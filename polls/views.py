from django.http import HttpResponse
import datetime
import requests

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
from chartjs.views.lines import BaseLineChartView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView
from plotly.offline import plot

from polls.forms import DateForm

from polls.data import DataLoader
from polls.updatedb import auto_update_president_polls
from polls.util import parse_daterange


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def sub(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


class PollJSONView(BaseLineChartView):
    def post(self, request, *args, **kwargs):
        form = DateForm(request.POST)
        start_date, end_date = parse_daterange(form["daterange"].value())
        candidates = form["candidates"].value()[0]
        if len(candidates) == 0:
            candidates = "-".join(DataLoader.instance().get_candidate_list())
        return redirect('poll_json', start_date=start_date, end_date=end_date,
                        candidates=candidates)

    def do_compute(self):
        self.n_weeks = self.kwargs.get('n_weeks')
        self.start_date = pytz.utc.localize(datetime.datetime.strptime(
            self.kwargs.get('start_date'), "%Y-%m-%d"))
        self.end_date = pytz.utc.localize(datetime.datetime.strptime(
            self.kwargs.get('end_date'), "%Y-%m-%d"))
        self.candidates = self.kwargs.get('candidates').split('-')
        print("Plot based on", self.candidates)

        self.df = DataLoader.instance().get_polls()
        self.df["pct"] = self.df["pct"].astype(float)
        self.df["create_date"] = pd.to_datetime(self.df["created_at"],
                                                infer_datetime_format=True)
        self.df["create_week"] = (self.df['create_date'] - pd.to_timedelta( \
            self.df['create_date'].dt.dayofweek, unit='d') + np.timedelta64(7, 'D')) \
            .dt.normalize()
        # TODO: insert better filtering here
        self.df_subset = self.df[self.df["party"] == "DEM"]
        # import pdb; pdb.set_trace()
        self.df_pivot = self.df_subset.pivot_table(
            values="pct", index="create_week", columns="answer",
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
        return self.candidates

    def get_data(self):
        """Return timeseries to plot for each candidate."""
        can_selected = self.get_providers()
        lst_selected = []
        for can in can_selected:
            lst_selected.append(list(self.df_pivot[can]))
        return lst_selected


class GDeltAnalysisPlot:
    def __init__(self, start_date=None, end_date=None, selected_candidates=[], selected_series=None):
        self.date_filtered_df = DataLoader.instance().get_media()
        if start_date is not None and end_date is not None:
            # change type of start_date to be same type with Media.date
            start_date_new = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_new = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            mask = (self.date_filtered_df['date'] > start_date_new) & (self.date_filtered_df['date'] <= end_date_new)
            self.date_filtered_df = self.date_filtered_df.loc[mask]

        self.date_filtered_df["pct"] = self.date_filtered_df["pct"].astype(float)
        self.date_filtered_df["value"] = self.date_filtered_df["value"].astype(float)

        if selected_candidates is None or len(selected_candidates) == 0:
            self.candidates = DataLoader.instance().get_candidate_list()
        else:
            self.candidates = selected_candidates
        print("Rendering for candidates", self.candidates, "from query", selected_candidates)

        if selected_series is None:
            self.series = DataLoader.instance().get_outlets_list()
        else:
            self.series = selected_series
        print("Rendering for series", self.series)

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
        zero_pos = abs(self.min_cor) / (abs(self.min_cor) + abs(self.max_cor))
        hm = go.Heatmap(
            z=self.cor_mat.values,
            x=self.candidates,
            y=self.series,
            colorscale=[(0, "red"), (zero_pos, "white"), (1, "green")],
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

        # get the elements from the form
        form = super().get_form()
        print(form["candidates"].value())
        start_date, end_date = parse_daterange(form["daterange"].value())
        candidates = form["candidates"].value()

        plot_data = GDeltAnalysisPlot(start_date, end_date, candidates)

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


class CandidatePageView(FormView):
    template_name = 'candidate.html'
    form_class = DateForm
    success_url = '.'

    # add items to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the elements from the form
        form = super().get_form()
        print(form["candidates"].value())
        start_date, end_date = parse_daterange(form["daterange"].value())
        candidates = form["candidates"].value()

        plot_data = GDeltAnalysisPlot(start_date, end_date, candidates)

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

# auto_update_president_polls()
main_page = MainPageView.as_view()
candidate = CandidatePageView.as_view()
poll_json_view = PollJSONView.as_view()
# correlation_view = CorrelationView.as_view()
# gdelt_heatmap_view = GDeltAnalysisPlotView.as_view()
