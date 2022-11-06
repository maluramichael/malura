from datetime import date
from diskcache import Cache
cache = Cache("_cache")


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_age():
    birthDate = date(1990, 4, 2)
    today = date.today()
    age = today.year - birthDate.year - \
        ((today.month, today.day) < (birthDate.month, birthDate.day))

    return age


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_work_years():
    work_start = date(2011, 8, 1)
    today = date.today()
    years = today.year - work_start.year - \
        ((today.month, today.day) < (work_start.month, work_start.day))

    return years


def get_personal_infos():
    print('Get personal infos')
    return {
        'age': get_age(),
        'work_years': get_work_years()
    }
