#! /usr/bin/env python3
# -*- coding:utf-8 -*-


def old_fixed_tax_at_class(cl):
    val = 0
    if cl == 1:
        val = 1500 * 0.03
    elif cl == 2:
        val = old_fixed_tax_at_class(cl - 1) + 3000 * 0.1
    elif cl == 3:
        val = old_fixed_tax_at_class(cl - 1) + 4500 * 0.2
    elif cl == 4:
        val = old_fixed_tax_at_class(cl - 1) + 26000 * 0.25
    elif cl == 5:
        val = old_fixed_tax_at_class(cl - 1) + 20000 * 0.3
    elif cl == 6:
        val = old_fixed_tax_at_class(cl - 1) + 25000 * 0.35
    return val


def cal_tax_old(salary, none_tax=0):
    sa = salary - none_tax
    st = 3500
    t1 = st + 1500
    t2 = st + 4500
    t3 = st + 9000
    t4 = st + 35000
    t5 = st + 55000
    t6 = st + 80000
    val = 0
    if sa > t6:
        val = old_fixed_tax_at_class(6) + (sa - t6) * 0.45
    elif sa > t5 and sa <= t6:
        val = old_fixed_tax_at_class(5) + (sa - t5) * 0.35
    elif sa > t4 and sa <= t5:
        val = old_fixed_tax_at_class(4) + (sa - t4) * 0.3
    elif sa > t3 and sa <= t4:
        val = old_fixed_tax_at_class(3) + (sa - t3) * 0.25
    elif sa > t2 and sa <= t3:
        val = old_fixed_tax_at_class(2) + (sa - t2) * 0.2
    elif sa > t1 and sa <= t2:
        val = old_fixed_tax_at_class(1) + (sa - t1) * 0.1
    elif sa > st and st <= t1:
        val = (sa - t1) * 0.03
    else:
        val = 0
    return val


def new_fixed_tax_at_class(cl):
    val = 0
    if cl == 1:
        val = 3000 * 0.03
    elif cl == 2:
        val = new_fixed_tax_at_class(cl - 1) + 9000 * 0.1
    elif cl == 3:
        val = new_fixed_tax_at_class(cl - 1) + 13000 * 0.2
    elif cl == 4:
        val = new_fixed_tax_at_class(cl - 1) + 10000 * 0.25
    elif cl == 5:
        val = new_fixed_tax_at_class(cl - 1) + 20000 * 0.3
    elif cl == 6:
        val = new_fixed_tax_at_class(cl - 1) + 25000 * 0.35
    return val


def cal_tax_new(salary, none_tax=0):
    sa = salary - none_tax
    st = 5000
    t1 = st + 3000
    t2 = st + 12000
    t3 = st + 25000
    t4 = st + 35000
    t5 = st + 55000
    t6 = st + 80000
    val = 0
    if sa > t6:
        val = new_fixed_tax_at_class(6) + (sa - t6) * 0.45
    elif sa > t5 and sa <= t6:
        val = new_fixed_tax_at_class(5) + (sa - t5) * 0.35
    elif sa > t4 and sa <= t5:
        val = new_fixed_tax_at_class(4) + (sa - t4) * 0.3
    elif sa > t3 and sa <= t4:
        val = new_fixed_tax_at_class(3) + (sa - t3) * 0.25
    elif sa > t2 and sa <= t3:
        val = new_fixed_tax_at_class(2) + (sa - t2) * 0.2
    elif sa > t1 and sa <= t2:
        val = new_fixed_tax_at_class(1) + (sa - t1) * 0.1
    elif sa > st and sa <= t1:
        val = (sa - st) * 0.1
    else:
        val = 0
    return val


def main():
    salary = int(input('请输入你的薪资:'))
    none_tax = float(input('请输入不交税部分金额:'))
    now_tax = cal_tax_old(salary, none_tax)
    print('现行交税方案应缴税额:%.2f, 税后收入:%.2f' % (now_tax, salary - none_tax - now_tax))
    new_tax = cal_tax_new(salary, none_tax)
    print('新个税方案应缴税额:%.2f， 税后收入:%.2f' % (new_tax, salary - none_tax - new_tax))
    print('新个税方案少缴税:%.2f' % (now_tax - new_tax))


if __name__ == '__main__':
    main()
