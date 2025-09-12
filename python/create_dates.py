import datetime
import check_date

def create_dates(date_start, date_final, date_inter):
    dates=[]
    date_start = check_date.check_date(date_start, outtype=datetime.datetime)
    date_final = check_date.check_date(date_final, outtype=datetime.datetime)
    
    date = date_start
    while ( date <= date_final ):
        dates.append(date)
        date = date + datetime.timedelta(days=float(date_inter))
    return dates
