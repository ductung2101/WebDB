from polls.models import Poll, Media
import pandas as pd

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

        self.__polls = Poll.pdobjects.all().to_dataframe()
        self.__media = Media.pdobjects.all().to_dataframe()

    def get_polls(self):
        return self.__polls

    def get_media(self):
        return self.__media

    
