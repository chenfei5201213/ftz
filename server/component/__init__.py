import calendar
from collections import defaultdict


def generate_month_calendar(specific_year, specific_month):
    # 获取指定年月的天数和第一天是星期几
    month_range = calendar.monthrange(specific_year, specific_month)
    num_days = month_range[1]

    # 初始化日历字典
    calendar_dict = {}

    # 遍历每个月的每一天，填充日历字典
    for day in range(1, num_days + 1):
        weekday = calendar.weekday(specific_year, specific_month, day)
        date = f"{specific_year}-{specific_month:02d}-{day:02d}"  # 格式化的日期
        calendar_dict[date] = {'weekday': calendar.day_name[weekday]}  # 星期几
    return calendar_dict


if __name__ == '__main__':
    print(generate_month_calendar(2023, 1))
