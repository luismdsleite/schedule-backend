import pandas as pd
import datetime


def datetime_to_timedelta(dt: datetime.datetime):
    if dt is not pd.NaT:
        return datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
    else:
        return pd.NaT    

"""
converts the "hora" and "duração" columns to "StartTime" and "Endtime columns"
"""
def convertTime(df: pd.DataFrame): 
    # Convert the "hora" and "duracao" columns to datetime objects
    df["hora"] = pd.to_datetime(df["hora"])
    df["hora"] = df["hora"].apply(lambda dt: datetime_to_timedelta(dt))
    df["duracao"] = pd.to_datetime(df["duracao"])
    df["duracao"] = df["duracao"].apply(lambda dt: datetime_to_timedelta(dt))

    # Calculate the "EndTime" by adding "hora" and "duracao" columns
    df["EndTime"] = df["hora"] + df["duracao"]
    df = df.drop(columns=["duracao"])

    def timedelta_to_string(td : datetime.timedelta):
        if td is not pd.NaT:
            return f'{td.seconds//3600:02}:{(td.seconds//60)%60:02}:00'
        else:
            return pd.NaT 
    df.rename(columns={"hora": "StartTime"}, inplace=True)

    df["StartTime"] = df["StartTime"].apply(lambda td: timedelta_to_string(td))
    df["EndTime"] = df["EndTime"].apply(lambda td: timedelta_to_string(td))
    return df