import sqlite3

from polls.models import Poll, Media
import pandas as pd
import numpy as np


# singleton class for loading data.
# this guy caches everything for speedy access
class DataLoader:
    __instance = None
    __polls = None
    __media = None

    @staticmethod
    def instance():
        """ Static access method. """
        if DataLoader.__instance == None:
            DataLoader()
        return DataLoader.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DataLoader.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            DataLoader.__instance = self
        # load media data
        # import pdb; pdb.set_trace()
        self.__media = Media.pdobjects.all().to_dataframe()
        self.__media["value"] = self.__media["value"].astype(float)
        self.__media["date"] = pd.to_datetime(self.__media["date"]) \
            .dt.strftime("%Y-%m-%d")
        # self.__media["create_week"] = pd.to_datetime(self.__media["create_week"])\
        #   .dt.strftime("%Y-%m-%d")
        # self.__media["date"] = self.__media["date"].dt.strftime("%Y-%m-%d")

        # load polls data

        self.__polls = Poll.pdobjects.all().to_dataframe()
        self.__polls["pct"] = self.__polls["pct"].astype(float)
        self.__polls["create_date"] = pd.to_datetime(self.__polls["created_at"],
                                                     infer_datetime_format=True)
        self.__polls["create_week"] = (self.__polls['create_date'] - \
                                       pd.to_timedelta(self.__polls['create_date'].dt.dayofweek, \
                                                       unit='d') + np.timedelta64(7, 'D')).dt.normalize() \
            .dt.normalize().dt.strftime("%Y-%m-%d")
        # subset this, temporarily
        self.__polls = self.__polls[self.__polls["party"] == "DEM"]

        print("1:")
        temp_polling = self.__polls
        temp_polling[['state']] = temp_polling[['state']].fillna(value='-')
        polling_means = temp_polling.groupby(['answer', 'create_week', 'state'])['pct'].mean().reset_index()
        polling_means_national = temp_polling.groupby(['answer', 'create_week'])['pct'].mean().reset_index()
        print("2:")
        conn = sqlite3.connect(':memory:')
        print("3:")
        self.__media.to_sql('media_coverage', conn, index=False)
        print("4:")
        polling_means.to_sql('polling_means', conn, index=False)

        polling_means_national.to_sql('polling_means_national', conn, index=False)
        qry_statewise = '''
            SELECT *
            FROM
                polling_means JOIN media_coverage ON
                candidate = answer
                AND create_week BETWEEN date AND date(date, '+7 day')
            '''
        qry_national = '''
                    SELECT *
                    FROM
                        polling_means_national JOIN media_coverage ON
                        candidate = answer
                        AND create_week BETWEEN date AND date(date, '+7 day')
                    '''
        self.__media_influence = pd.read_sql_query(qry_statewise, conn)
        self.__media_influence_national = pd.read_sql_query(qry_national, conn)

    def get_polls(self, start_date=None, end_date=None, candidates=None,
                  state=None):
        df = self.__polls
        if state is not None and state != "National":
            df = df[df["state"] == state]
        if start_date is not None:
            df = df[df["create_date"] >= start_date]
        if end_date is not None:
            df = df[df["create_date"] <= end_date]
        if candidates is not None:
            df = df[df["answer"].isin(candidates)]
        return df

    def get_media(self, start_date=None, end_date=None, candidates=None,
                  series=None):
        df = self.__media
        if start_date is not None:
            df = df[df["date"] >= start_date]
        if end_date is not None:
            df = df[df["date"] <= end_date]
        if candidates is not None:
            df = df[df["candidate"].isin(candidates)]
        if series is not None:
            df = df[df["series"].isin(series)]
        return df

    def get_media_influence(self, start_date=None, end_date=None, candidates=None,
                            series=None, state=None):
        if state is not None and state != "National" and state != "":
            df = self.__media_influence
            df = df[df["state"] == state]
        else:
            df = self.__media_influence_national
        if start_date is not None:
            df = df[df["date"] >= start_date]
        if end_date is not None:
            df = df[df["date"] <= end_date]
        if candidates is not None:
            df = df[df["candidate"].isin(candidates)]
        if series is not None:
            df = df[df["series"].isin(series)]
        return df

    # helper functions
    def get_candidate_list(self):
        return list(self.__media['candidate'].unique())

    def get_initial_candidates(self):
        return ["Biden", "Sanders"]

    def get_outlets_list(self):
        return list(self.__media['series'].unique())
