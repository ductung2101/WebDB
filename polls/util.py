import datetime

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