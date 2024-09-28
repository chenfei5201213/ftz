import calendar
from datetime import timedelta, datetime


def generate_month_calendar(year, month):
    # 获取月份的第一天和最后一天
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    # 计算第一天往前补到第一个周日
    while first_day.weekday() != 6:  # 6 表示周日
        first_day -= timedelta(days=1)

    # 计算最后一天往后补到最近的一个周六
    while last_day.weekday() != 5:  # 5 表示周六
        last_day += timedelta(days=1)

    # 创建一个空字典来存储结果
    result = {}

    # 遍历从第一天到最后一天的每一天
    current_day = first_day
    while current_day <= last_day:
        date_str = current_day.strftime('%Y-%m-%d')
        weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][current_day.weekday()]
        in_month = (current_day.month == month)

        result[date_str] = {
            'weekday': weekday,
            'in_month': in_month,
            'count': 0,
            'finish_count': 0
        }

        current_day += timedelta(days=1)

    return result


if __name__ == '__main__':
    print(generate_month_calendar(2024, 8))
