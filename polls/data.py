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
        self.__media = Media.pdobjects.all().to_dataframe()
        self.__media["pct"] = self.__media["pct"].astype(float)
        self.__media["value"] = self.__media["value"].astype(float)
        self.__media["date"] = pd.to_datetime(self.__media["date"])\
            .dt.strftime("%Y-%m-%d")
        self.__media["create_week"] = pd.to_datetime(self.__media["create_week"])\
            .dt.strftime("%Y-%m-%d")
        # self.__media["date"] = self.__media["date"].dt.strftime("%Y-%m-%d")

        # load polls data
        self.__polls = Poll.pdobjects.all().to_dataframe()
        self.__polls["pct"] = self.__polls["pct"].astype(float)
        self.__polls["create_date"] = pd.to_datetime(self.__polls["created_at"],
                                                infer_datetime_format=True)
        self.__polls["create_week"] = (self.__polls['create_date'] - \
            pd.to_timedelta(self.__polls['create_date'].dt.dayofweek, \
            unit='d') - np.timedelta64(1, 'D')) \
            .dt.normalize().dt.strftime("%Y-%m-%d")
        # subset this, temporarily
        self.__polls = self.__polls[self.__polls["party"] == "DEM"]


    def get_polls(self, start_date = None, end_date = None, candidates = None):
        df = self.__polls
        if start_date is not None:
            df = df[df["create_date"] >= start_date]
        if end_date is not None:
           df = df[df["create_date"] <= end_date]
        if candidates is not None:
           df = df[df["answer"].isin(candidates)]
        return df

    def get_media(self, start_date = None, end_date = None, candidates = None,
                series = None):
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

    # helper functions
    def get_candidate_list(self):
        return self.__media['candidate'].unique()
    def get_outlets_list(self):
        return self.__media['series'].unique()

    
