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

from polls.forms import CandidatesForm, NationalForm, OutletsForm

from polls.data import DataLoader
from polls.updatedb import auto_update_president_polls
from polls.util import parse_daterange

class PollJSONView(BaseLineChartView):
    def post(self, request, *args, **kwargs):
        form = NationalForm(request.POST)
        start_date, end_date = parse_daterange(form["daterange"].value())
        candidates = form["candidates"].value()[0]
        if len(candidates) == 0:
            candidates = "-".join(DataLoader.instance().get_candidate_list())
        return redirect('poll_json', start_date=start_date, end_date=end_date,
                        candidates=candidates)

    def do_compute(self):
        self.candidates = self.kwargs.get('candidates').split('-')
        self.df = DataLoader.instance().get_polls(
            self.kwargs.get('start_date'),
            self.kwargs.get('end_date'),
            self.candidates
        )

        self.df_pivot = self.df.pivot_table(
            values="pct", index="create_week", columns="answer",
            aggfunc=np.mean).fillna(0)

    def get_labels(self):
        self.do_compute()
        """Return n_weeks labels for the x-axis."""
        return list(self.df_pivot.index)

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


class CoverageJSONView(BaseLineChartView):
    def post(self, request, *args, **kwargs):
        form = NationalForm(request.POST)
        start_date, end_date = parse_daterange(form["daterange"].value())
        candidates = form["candidates"].value()[0]
        if len(candidates) == 0:
            candidates = "-".join(DataLoader.instance().get_candidate_list())
        outlets = form["outlets"].value()[0]
        if len(outlets) == 0:
            outlets = "-".join(DataLoader.instance().get_outlets_list())
        return redirect('cov_json', start_date=start_date, end_date=end_date,
                        candidates=candidates, series=outlets)

    def do_compute(self):
        self.candidates = self.kwargs.get('candidates').split('-')
        self.series = self.kwargs.get('series').split('-')
        self.df = DataLoader.instance().get_media(
            self.kwargs.get('start_date'),
            self.kwargs.get('end_date'),
            self.candidates,
            self.series
        )

        self.df_pivot = self.df.pivot_table(
            values="value", index="create_week", columns="answer",
            aggfunc=np.mean).fillna(0)

    def get_labels(self):
        self.do_compute()
        """Return n_weeks labels for the x-axis."""
        return list(self.df_pivot.index)

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

        self.date_filtered_df = DataLoader.instance().get_media(start_date, end_date,
            self.candidates, self.series)

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
    form_class = NationalForm
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
    form_class = CandidatesForm
    success_url = '.'

    # add items to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the elements from the form
        form = super().get_form()

        return context

    def form_valid(self, form):
        return super().get(form)

# auto_update_president_polls()
main_page = MainPageView.as_view()
candidate = CandidatePageView.as_view()
poll_json_view = PollJSONView.as_view()
cov_json_view = CoverageJSONView.as_view()
# correlation_view = CorrelationView.as_view()
# gdelt_heatmap_view = GDeltAnalysisPlotView.as_view()
