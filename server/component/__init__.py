import calendar
from collections import defaultdict


def generate_month_calendar(specific_year, specific_month):
    # 获取指定年月的天数和第一天是星期几
    month_range = calendar.monthrange(specific_year, specific_month)
    num_days = month_range[1]
    first_weekday = month_range[0]  # 月的第一天是星期几

    # 初始化日历字典，键为日期，值为包含相关信息的字典
    calendar_dict = {}

    # 计算需要补充的空位（上月的天数）
    prev_month = specific_month - 1 if specific_month > 1 else 12
    prev_year = specific_year if specific_month > 1 else specific_year - 1
    prev_month_days = calendar.monthrange(prev_year, prev_month)[1]

    # 填充月初的空位
    for i in range(first_weekday):
        day = prev_month_days - first_weekday + i + 1
        date = f"{prev_year}-{prev_month:02d}-{day:02d}"  # 格式化的日期
        calendar_dict[date] = {'weekday': calendar.day_name[calendar.weekday(prev_year, prev_month, day)], 'in_month': False}

    # 遍历每个月的每一天，填充日历
    for day in range(1, num_days + 1):
        weekday = calendar.weekday(specific_year, specific_month, day)
        date = f"{specific_year}-{specific_month:02d}-{day:02d}"  # 格式化的日期
        calendar_dict[date] = {'weekday': calendar.day_name[weekday], 'in_month': True}

    # 补充月末的空位（下月的天数）
    next_month = specific_month + 1 if specific_month < 12 else 1
    next_year = specific_year if specific_month < 12 else specific_year + 1
    days_to_add = (7 - (len(calendar_dict) % 7)) % 7  # 计算需要补充的天数以完成最后一周
    for i in range(days_to_add):
        day = i + 1
        date = f"{next_year}-{next_month:02d}-{day:02d}"  # 格式化的日期
        calendar_dict[date] = {'weekday': calendar.day_name[calendar.weekday(next_year, next_month, day)], 'in_month': False}

    return calendar_dict


if __name__ == '__main__':
    print(generate_month_calendar(2023, 1))
