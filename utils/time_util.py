from datetime import datetime

def get_now_str(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(fmt)

def get_date_str():
    return datetime.now().strftime("%Y-%m-%d")