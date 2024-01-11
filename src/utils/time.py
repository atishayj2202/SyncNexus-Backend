from datetime import datetime

import pytz


def get_current_time():
    return datetime.now(tz=pytz.utc)
