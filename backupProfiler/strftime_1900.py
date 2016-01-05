import datetime
import re
import warnings

def strftime_1900(dt, fmt):
    if dt.year < 1900:
        # create a copy of this datetime, just in case, then set the year to
        # something acceptable, then replace that year in the resulting string
        tmp_dt = datetime.datetime(datetime.MAXYEAR, dt.month, dt.day,
                                  dt.hour, dt.minute,
                                  dt.second, dt.microsecond,
                                  dt.tzinfo)
        
        if re.search('(?<!%)((?:%%)*)(%y)', fmt):
            warnings.warn("Using %y time format with year prior to 1900 "
                          "could produce unusual results!")
        
        tmp_fmt = fmt
        tmp_fmt = re.sub('(?<!%)((?:%%)*)(%y)', '\\1\x11\x11', tmp_fmt, re.U)
        tmp_fmt = re.sub('(?<!%)((?:%%)*)(%Y)', '\\1\x12\x12\x12\x12', tmp_fmt, re.U)
        tmp_fmt = tmp_fmt.replace(str(datetime.MAXYEAR), '\x13\x13\x13\x13')
        tmp_fmt = tmp_fmt.replace(str(datetime.MAXYEAR)[-2:], '\x14\x14')
        
        result = tmp_dt.strftime(tmp_fmt)
        
        if '%c' in fmt:
            # local datetime format - uses full year but hard for us to guess
            # where.
            result = result.replace(str(datetime.MAXYEAR), str(dt.year))
        
        result = result.replace('\x11\x11', str(dt.year)[-2:])
        result = result.replace('\x12\x12\x12\x12', str(dt.year))
        result = result.replace('\x13\x13\x13\x13', str(datetime.MAXYEAR))
        result = result.replace('\x14\x14', str(datetime.MAXYEAR)[-2:])
            
        return result
        
    else:
        return dt.strftime(fmt)