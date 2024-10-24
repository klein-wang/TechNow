from datetime import datetime
import pytz


def get_cst_time():
    cst_timezone = pytz.timezone('Asia/Shanghai')
    cur_time = datetime.now()
    # 指定时区
    cur_time = cur_time.astimezone(cst_timezone)
    return cur_time


def get_cst_time_formatter(pattern):
    cst_timezone = pytz.timezone('Asia/Shanghai')
    cur_time = datetime.now()
    # 指定时区
    cur_time = cur_time.astimezone(cst_timezone)
    cur_time = cur_time.strftime(pattern)
    return cur_time


def get_utc_to_cst_time(sub_str, parse_format):
    ts_time = datetime.strptime(sub_str, parse_format)
    secondUtc = int((ts_time - (datetime.utcfromtimestamp(0))).total_seconds())
    cst_time = datetime.fromtimestamp(secondUtc).astimezone(pytz.timezone("Asia/Shanghai"))
    return cst_time


def get_cst_time_by_second(second):
    if second:
        cst_time = datetime.fromtimestamp(second).astimezone(pytz.timezone("Asia/Shanghai"))
        cst_time_str = cst_time.strftime("%Y-%m-%d %H:%M:%S")
        return cst_time_str
    return ''


def get_str_to_date_time(sub_str, parse_format):
    return datetime.strptime(sub_str, parse_format)


def get_cst_second(date_time):
    cst = pytz.timezone('Asia/Shanghai')
    second = int(cst.localize(date_time).timestamp())
    return second


# 小于等于比较
def compare_lt_eq(sr_p, ta_p, sr_c, ta_c):
    return sr_p < ta_p if sr_p != ta_p else sr_c <= ta_c


# 大于比较
def compare_gt(sr_p, ta_p, sr_c, ta_c):
    return sr_p > ta_p if sr_p != ta_p else sr_c > ta_c
