#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import sys


def equal_loan_payment(total, months, rate):
    # 等额本息
    month_rate = rate / 12.0
    X = (total * month_rate * (1 + month_rate) ** months) / ((1 + month_rate) ** months - 1)

    ret_string = ''
    total_payment = X * months
    total_interest = total_payment - total
    month_payment = X

    month_string = '每月还款:%.2f' % (month_payment)
    interst_string = '支付利息:%.2f' % (total_interest)
    total_string = '还款总额:%.2f' % (total_payment)
    ret_string = ret_string + month_string + '\n'
    ret_string = ret_string + interst_string + '\n'
    ret_string = ret_string + total_string + '\n'
    return ret_string


def equal_principal_payment(total, months, rate):
    # 等额本金
    month_rate = rate / 12.0
    first_month = total / months + total * month_rate
    second_month = total / months + (total - total / months) * month_rate
    month_less = first_month - second_month
    total_payment = first_month * months - month_less * (sum_in_range(range(months)))
    month_string = '首月还款:%.2f，每月递减:%.2f' % (first_month, month_less)
    interst_string = '支付利息:%.2f' % (total_payment - total)
    total_string = '还款总额:%.2f' % (total_payment)
    ret_string = ''
    ret_string = ret_string + month_string + '\n'
    ret_string = ret_string + interst_string + '\n'
    ret_string = ret_string + total_string + '\n'
    return ret_string


def sum_in_range(r):
    sum = 0
    for i in r:
        sum += i
    return sum


def print_line(len=77):
    print('-' * len)


def get_rate():
    print('请选择贷款利率:')
    print('\t1.公积金贷款基准利率(大于5年):3.25%')
    print('\t2.公积金贷款基准利率(小于5年):2.75%')
    print('\t3.商业贷款基准利率:4.9%')
    print('\t4.商业贷款基准利率(上浮10%):5.39%')
    print('\t5.商业贷款基准利率(9折):4.41%')
    print('\t6.手动输入')
    opt = input('请选择:')
    rate = 0
    idx = int(opt)
    if idx == 1:
        rate = 0.0325
    elif idx == 2:
        rate = 0.0275
    elif idx == 3:
        rate = 0.0490
    elif idx == 4:
        rate = 0.0539
    elif idx == 5:
        rate = 0.0441
    elif idx == 6:
        rate_str = input('请输入贷款利率(0.0325 = 3.25%):')
        rate = float(rate_str)
    else:
        print('选择错误。。。')
        sys.exit(-1)
    return rate


def get_months():
    print('请选择贷款年限:')
    print('\t1. 5年')
    print('\t2. 10年')
    print('\t3. 15年')
    print('\t4. 20年')
    print('\t5. 25年')
    print('\t6. 30年')
    print('\t7. 手动输入')
    opt = input('请选择:')
    months = 0
    idx = int(opt)
    year = 0
    if idx == 1:
        year = 5
    elif idx == 2:
        year = 10
    elif idx == 3:
        year = 15
    elif idx == 4:
        year = 20
    elif idx == 5:
        year = 25
    elif idx == 6:
        year = 30
    elif idx == 7:
        year_str = input('请输入时长(仅支持输入整数年，如18年等。单位:年)')
        year = int(year_str)
    else:
        print('选择错误。。。')
        sys.exit(-1)
    months = year * 12
    return months


def main():
    print_line()
    print('\t\t\t\t欢迎使用贷款计算器')
    total_str = input('请输入贷款金额:(单位:元)')
    total = int(total_str)
    months = get_months()
    rate = get_rate()
    print(equal_loan_payment(total, months, rate))  # 打印等额本息贷款信息
    print(equal_principal_payment(total, months, rate))  # 打印等额本金贷款信息


if __name__ == '__main__':
    main()
