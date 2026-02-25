import datetime
import pytz
import numpy as np

def check_date_list(datelist, outtype=str, dtlen=8):
    if ( not isinstance(datelist, list) ):
        print('datelist must be list')
        dnewlist = datelist
    else:
        dnewlist = [ check_date(date, outtype=outtype, dtlen=dtlen) for date in datelist ]
    return dnewlist
    
def check_date(date, outtype=str, dtlen=8):
    datestr=None
    if ( isinstance(date, np.datetime64) ): date=date.astype(datetime.datetime)
    if ( (outtype==str) or (outtype==int) ):
      if ( isinstance(date, datetime.datetime) or isinstance(date, datetime.date) ):
        if ( dtlen == 8 ):  
          datestr=date.strftime("%Y%m%d")
        elif ( dtlen == 10 ): 
          datestr=date.strftime("%Y%m%d%H")
        elif ( dtlen == 12 ): 
          datestr=date.strftime("%Y%m%d%H%M")
        elif ( dtlen == 14 ): 
          datestr=date.strftime("%Y%m%d%H%M%S")
        else:
          datestr=date.strftime("%Y%m%d")
      if ( isinstance(date, int) ):  datestr=str(date)
      if ( isinstance(date, str) ): datestr=date
      if ( len(datestr) < dtlen ):
          datestr=datestr+str(0).zfill(dtlen-len(datestr))
      if ( len(datestr) > dtlen ):
          datestr=datestr[:dtlen]
    if ( outtype ==int ): datestr=int(datestr)
    if ( ( outtype == datetime.datetime ) or ( outtype == datetime.date) ):
      if ( isinstance(date, int) ): date=str(date)
      if ( isinstance(date, str) and ( len(date) == 8 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d')  
      elif ( isinstance(date, str) and ( len(date) == 10 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H')  
      elif ( isinstance(date, str) and ( len(date) == 12 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H%M')  
      elif ( isinstance(date, str) and ( len(date) == 14 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H%M%S')  
      if ( isinstance(date, datetime.datetime) ): datestr=date
      if ( isinstance(date, datetime.date) ): datestr=datetime.datetime(*date.timetuple()[:4])
      if ( outtype == datetime.date ): datestr=datestr.date()
    if ( isinstance(datestr, type(None) ) ): print('No valid conversion offered', date)
    return datestr

def add_utc(date):
    if ( date.tzinfo == None ):
        date=pytz.utc.localize(date)
    else:
        pass # return date with tzinfo as already in the date
    return date
