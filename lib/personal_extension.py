from datetime import date


def get_age():
    birthDate = date(1990, 4, 2)
    today = date.today()
    age = today.year - birthDate.year - \
        ((today.month, today.day) < (birthDate.month, birthDate.day))

    return age


def get_personal_infos():
    print('Get personal infos')
    return {
        'age': get_age()
    }
