#from colour import Color
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

from .forms import CandidatesForm, NationalForm, OutletsForm

from .data import DataLoader
from .updatedb import auto_update_president_polls
from .util import parse_daterange


class PollJSONView(BaseLineChartView):
    def post(self, request, *args, **kwargs):
        form = NationalForm(request.POST)
        start_date, end_date = parse_daterange(form["daterange"].value())
        candidates = form["candidates"].value()[0]
        state = form["state"].value()
        if len(candidates) == 0:
            candidates = "-".join(DataLoader.instance().get_candidate_list())
        return redirect('poll_json', start_date=start_date, end_date=end_date,
                        candidates=candidates, state=state)

    def do_compute(self):
        self.df = DataLoader.instance().get_polls(
            self.kwargs.get('start_date'),
            self.kwargs.get('end_date'),
            self.kwargs.get('candidates').split('-'),
            self.kwargs.get('state'),
        )
        self.candidates = self.df["answer"].unique()
        self.df_pivot = self.df.pivot_table(
            values="pct", index="create_week", columns="answer",
            aggfunc=np.mean).fillna(0)

        # import pdb; pdb.set_trace()

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
        if len(candidates) == 0 or candidates is None:
            candidates = "-".join(DataLoader.instance().get_candidate_list())
        outlets = form["outlets"].value()[0]
        if len(outlets) == 0 or candidates is None:
            outlets = "-".join(DataLoader.instance().get_outlets_list())
        return redirect('cov_json', start_date=start_date, end_date=end_date,
                        candidates=candidates, series=outlets)

    def do_compute(self):
        self.series = self.kwargs.get('series').split('-')
        self.df = DataLoader.instance().get_media_influence(
            self.kwargs.get('start_date'),
            self.kwargs.get('end_date'),
            self.kwargs.get('candidates').split('-'),
            self.series,
        ).round({'value': 2})
        self.candidates = self.df["answer"].unique()
        self.df_pivot = self.df.pivot_table(
            values="value", index="create_week", columns="answer",
            aggfunc=np.mean).fillna(0).round(2)

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
    def __init__(self, start_date=None, end_date=None, state=None,
                 selected_candidates=None, selected_series=None):
        if selected_candidates is None:
            selected_candidates = []
        if selected_candidates is None or len(selected_candidates) == 0:
            self.candidates = DataLoader.instance().get_candidate_list()
        else:
            self.candidates = selected_candidates
        print("Rendering for candidates", self.candidates, "from query", selected_candidates)

        if selected_series is None or len(selected_series) == 0:
            self.series = DataLoader.instance().get_outlets_list()
        else:
            self.series = selected_series
        print("Rendering for series", self.series)

        self.date_filtered_df = DataLoader.instance().get_media_influence(
            start_date, end_date, self.candidates, self.series).round({'pct': 2, 'value': 2})

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

                cor_mat.at[row, col] = np.corrcoef(subset["value"], subset["pct"])[0, 1].round(2)
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
        if len(self.candidates) == 1 and len(self.series) == 1:
            return ''
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
            colorscale=[(0, "red"), (zero_pos, "rgb(226, 223, 208)"), (1, "green")],
            text=hover,
            hoverinfo='text')

        fig = go.Figure(data=hm)
        fig.update_layout(
            title="Correlation heatmap"
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=True)

        return plot_div

    def make_radar_chart(self):
        is_outlets_wise = len(self.series) > len(self.candidates)
        categories = self.series if is_outlets_wise else self.candidates
        radars = self.candidates if is_outlets_wise else self.series
        if len(categories) > 6 or len(radars) > 3:
            return ""
        if len(categories) == 1 and len(radars) == 1:
            return ""

        chart_data = []
        if is_outlets_wise:
            for i in range(len(radars)):
                current_candidate = self.date_filtered_df['candidate'] == radars[i]
                chart_data_row = []
                for j in range(len(categories)):
                    current_outlet = self.date_filtered_df['series'] == categories[j]
                    chart_data_row.append(self.date_filtered_df[current_candidate & current_outlet]['value'].mean())
                chart_data.append(chart_data_row)
        else:
            for i in range(len(radars)):
                current_outlet = self.date_filtered_df['series'] == radars[i]
                chart_data_row = []
                for j in range(len(categories)):
                    current_candidate = self.date_filtered_df['candidate'] == categories[j]
                    chart_data_row.append(self.date_filtered_df[current_outlet & current_candidate]['value'].mean())
                chart_data.append(chart_data_row)

        fig = go.Figure()
        for i in range(len(radars)):
            fig.add_trace(go.Scatterpolar(
                r=chart_data[i],
                theta=categories,
                fill='toself',
                name=radars[i]
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True
                )),
            showlegend=True
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=True)
        return plot_div

    def make_scatter_plot(self):
        is_outlets_wise = len(self.series) < len(self.candidates)
        lines = self.series if is_outlets_wise else self.candidates
        facets = self.candidates if is_outlets_wise else self.series
        if len(lines) > 3 or len(facets) > 6:
            return ""
        df = self.date_filtered_df[self.date_filtered_df["candidate"].isin(self.candidates)]
        df = df[self.date_filtered_df["series"].isin(self.series)]
        fig = px.scatter(df, x="value", y="pct", facet_col="candidate" if is_outlets_wise else "series",
                         color="series" if is_outlets_wise else "candidate", trendline="ols", facet_col_wrap=2)
        if len(self.candidates) == 1 and len(self.series) == 1:
            plot_title = self.candidates[0] + ' vs. ' + self.series[0] + ' station'
        elif len(self.candidates) == 1:
            plot_title = self.candidates[0] + ' vs. outlets'
        elif len(self.series) == 1:
            plot_title = 'Selected candidates vs. ' + self.series[0] + ' station'
        else:
            plot_title = 'Selected candidates vs. Selected outlets'
        fig.update_layout(
            title=plot_title,
            xaxis_title = 'Media Coverage',
            yaxis_title = 'Polling results (%)'
        )
        plot_div = plot(fig, output_type='div', include_plotlyjs=True)
        return plot_div


def overview_table(start_date, end_date, state, candidates, series):
    cols_dict = {
        'answer': 'Candidate',
        'value': 'Coverage Average (%)',
        'cov_growth' : 'Coverage Growth (p.p.)',
        'pct': 'Polling Average (%)',
        'poll_growth' : 'Polling Growth (p.p.)'
    }
    return_dict = {}
    print("TUTAJ!")
    #print(candidates)
    dfp = DataLoader.instance().get_polls(start_date, end_date, candidates, state)
    #print(dfp["answer"].unique())
    dfc = DataLoader.instance().get_media_influence(start_date, end_date, candidates, series, state)
    #print(dfc["candidate"].unique())
    dfp_fst_date = dfp[dfp.start_date == dfp.start_date.min()][["answer", "pct"]]
    dfp_lst_date = dfp[dfp.start_date == dfp.start_date.max()][["answer", "pct"]]
    dfp_date_merged = pd.merge(dfp_fst_date, dfp_lst_date, on = 'answer')
    dfp_date_merged['poll_growth'] = dfp_date_merged['pct_y'].astype(int) - dfp_date_merged['pct_x'].astype(int)
    dfp_date_merged = dfp_date_merged[['answer', 'poll_growth']]
    dfc_fst_date = dfc[dfc.date == dfc.date.min()][["answer", "value"]].groupby("answer").mean()
    dfc_lst_date = dfc[dfc.date == dfc.date.max()][["answer", "value"]].groupby("answer").mean()
    dfc_date_merged = pd.merge(dfc_fst_date, dfc_lst_date, on='answer')
    dfc_date_merged['cov_growth'] = dfc_date_merged['value_y'] - dfc_date_merged['value_x']
    dfc_date_merged = dfc_date_merged['cov_growth']
    print(dfp_date_merged)
    df_agg = dfc.groupby("answer").mean()
    df_agg["pct"] = dfp.groupby("answer")["pct"].mean()
    df_agg = pd.merge(df_agg, dfp_date_merged, on='answer')
    df_agg = pd.merge(df_agg, dfc_date_merged, on='answer')
    df_agg = df_agg.reset_index()[cols_dict.keys()]
    df_agg = df_agg.round(2)

    # get polling values, to display in the template.
    df_agg.sort_values(by="pct", ascending=False, inplace=True)
    return_dict["overview_pct_leader"] = df_agg.iloc[0]["answer"]
    return_dict["overview_pct_runnerup"] = df_agg.iloc[1]["answer"] if len(df_agg) > 1 else ''
    return_dict["overview_pct_leaderv"] = str(df_agg.iloc[0]["pct"])+'%'
    return_dict["overview_pct_runnerupv"] = str(df_agg.iloc[1]["pct"])+'%' if len(df_agg) > 1 else ''

    if len(df_agg) > 1:
        return_dict["intro_1"] = 'The average polling leader over the highlighted period is '
        return_dict["intro_2"] = 'with a polling percentage of '
        return_dict["intro_3"] = 'The average polling leader over the highlighted period is '
        return_dict["intro_4"] = 'with a polling percentage of '
        return_dict["intro_5"] = 'respectively.'
        return_dict["intro_6"] = 'Regarding media coverage, the average leader over the same period is '
        return_dict["intro_7"] = ', with a percentage of '
        return_dict["intro_8"] = ' of the total airtime,'
        return_dict["intro_9"] = 'while the runner-up is '
        return_dict["intro_10"] = 'who garnered '
        return_dict["intro_11"] = ' of the airtime.'
    else:
        return_dict["intro_1"] = 'The average polling of '
        return_dict["intro_2"] = 'is '
        return_dict["intro_3"] = ''
        return_dict["intro_4"] = ''
        return_dict["intro_5"] = ''
        return_dict["intro_6"] = 'Regarding media coverage, the score of '
        return_dict["intro_7"] = ', is '
        return_dict["intro_8"] = ' of the total airtime,'
        return_dict["intro_9"] = ''
        return_dict["intro_10"] = ''
        return_dict["intro_11"] = ''

    # get media coverage values
    df_agg.sort_values(by="value", ascending=False, inplace=True)
    return_dict["overview_value_leader"] = df_agg.iloc[0]["answer"]
    return_dict["overview_value_runnerup"] = df_agg.iloc[1]["answer"] if len(df_agg) > 1 else ''
    return_dict["overview_value_leaderv"] = str(df_agg.iloc[0]["value"]) + '%'
    return_dict["overview_value_runnerupv"] = str(df_agg.iloc[1]["value"]) + '%' if len(df_agg) > 1 else ''

    # get table data
    return_dict["overview_columns"] = [{'field': x, 'title': cols_dict[x]} for x in df_agg.columns]
    return_dict["overview_data"] = df_agg.to_json(orient='records')
    return return_dict


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
        outlets = form["outlets"].value()
        state = form["state"].value()
        if candidates is not None and len(candidates) == 0:
            candidates = None
        if outlets is not None and len(outlets) == 0:
            outlets = None

        plot_data = GDeltAnalysisPlot(start_date, end_date, state, candidates, outlets)

        # make heatmap
        context['heatmap'] = plot_data.make_heatmap()
        if (candidates is None or len(candidates) != 1) or (outlets is None or len(outlets) != 1):
            context['intro_heatmap'] = '<p>The most significant negative correlation occurred between ' + plot_data.min_ser + ' and ' + plot_data.min_cand + ' with the value: ' + str(plot_data.min_cor) + '</p><p>The most significant positive correlation occurred between ' + plot_data.max_ser + ' and ' + plot_data.max_cand + ' with the value: '+ str(plot_data.max_cor) +'</p>'
        else:
            context['intro_heatmap'] = '<p>The correlation between ' + candidates[0] + ' and ' + outlets[0] + ' is ' + str(plot_data.max_cor)
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

        context['cand_num'] = 0 if candidates is None else len(candidates)
        context['outlets_num'] = 0 if outlets is None else len(outlets)

        # get data for the overview table
        context.update(overview_table(start_date, end_date, state, candidates, outlets))


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
