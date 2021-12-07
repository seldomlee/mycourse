#-- coding:UTF-8 --
# author：Na0h

import numpy as np

# 打印表格
def printTable(available, max, allocation, need):
    n = allocation.shape[0]
    print("=="*30)
    print("[*]进程\tMax\t\tAllo\tNeed")
    for i in range(n):
        print(f"[*]P{i}\t{max[i]}\t{allocation[i]}\t{need[i]}")
    print("[*]当前剩余资源:", available)

# 安全性算法
def safe(work,need,allocation):
    n = need.shape[0]
    finish = np.array([0] * n, dtype=int)

    a = []
    j = 0

    while not(finish.all()):
        # flag用于标记是否找到满足条件的进程
        flag = 0
        for i in range(n):
            if not finish[i] and (need[i] <= work).all():
                a.insert(j, i)
                j += 1
                flag = 1

                work += allocation[i]
                finish[i] = 1
                break

        if not flag:
            return 0

    print("==" * 30)
    print("[*]存在安全序列：", end='')
    for i in a:
        if i == len(a) - 1:
            print(f"P{i}")
        else:
            print(f"P{i}", end='->')
    print("[*]当前不存在死锁")
    return 1


# 利用资源抢占的方式解除死锁
def comproc(allocation, available, need, max):
    n = allocation.shape[0]
    m = allocation[0].shape[0]

    flag = 0

    for i in range(n):
        for j in range(m):
            process_id, req = i, allocation[i]

            if need[i][j] > available[j]:
                # 安全性判断
                available += req
                allocation[process_id] -= req
                need[process_id] = max[process_id]-allocation[process_id]

                flag = 1
                if safe(available.copy(), need, allocation):
                    print(f"[*]可行,撤销P{process_id}资源以解除死锁")
                    print("==" * 30)
                    print("[*]进程\tMax\tAllo\tNeed")
                    for k in range(n):
                        print(f"[*]P{k}\t{max[k]}\t{allocation[k]}\t{need[k]}")
                    print("[*]当前剩余资源:", available)

                    return available, allocation, need
                else:
                    comproc(allocation, available, need, max)

            elif not allocation.any():
                if flag:
                    available -= req
                    allocation[process_id] += req
                    need[process_id] = max[process_id]-allocation[process_id]
                print("[*]无法解除")
                return available, allocation, need


def main():
    # 资源总数m
    m = int(input("[+]资源种类数目 m: "))

    # 可用资源向量(资源池)——(available)
    temp = input("[+]输入资源池资源(用空格隔开):").split()
    available = np.array(temp, dtype=int)

    # 进程数n
    n = int(input("[+]进程数 n: "))

    # 最大需求资源——(max)
    max = np.zeros([n, m], dtype=int)
    i = 0
    while i < n:
        temp = input(f"[+]输入进程 p{i} 最大需求资源(max): ").split()
        max[i] = np.array(temp, dtype=int)
        if(available < max[i]).any():
            print("[*]错误输入，请重试")
            i -= 1
        i += 1

    # 分配给该进程的资源——(allocation)
    allocation = np.zeros([n, m], dtype=int)
    i = 0
    while i < n:
        temp = input("[+]输入进程 P{} 的已分配资源(allocation)：".format(i)).split()
        allocation[i] = np.array(temp, dtype=int)
        if(max[i] < allocation[i]).any():
            print("[*]错误输入，请重试")
            i -= 1
        i += 1



    # 计算需求资源数量
    need = max - allocation

    # 计算出剩余资源
    for i in allocation:
        available -= i

    printTable(available, max, allocation, need)

    while (need != 0).any():
        # 进行选择
        print("==" * 30)
        print("[*]1.请求资源\r\n[*]2.死锁检测\r\n[*]3.输出当前资源状态")
        chose = input("[+]你选择：")

        if chose == '1':
            process_id, req = input("[+]请求资源 (eg:P1, 1 0 1): ").split(',')
            process_id = int(process_id[1:])
            req = np.array(req.split(), dtype=int)
            if (req > max[process_id]).any():
                print("[*]错误输入，请重试")

            else:  # 安全性判断
                available -= req
                allocation[process_id] += req
                need[process_id] -= req
                if safe(available.copy(), need, allocation):
                    printTable(available, max, allocation, need)
                    continue
                else:
                    print("[*]不安全，分配失败")
                    available += req
                    allocation[process_id] -= req
                    need[process_id] += req

        elif chose == '2':
            if safe(available.copy(), need, allocation):
                continue
            else:
                print("[*]存在死锁")
                print("==" * 30)
                print("[*]是否要抢占资源以解除死锁？\r\n[*]1.是\r\n[*]2.输入其他则返回上一级")
                chose = input("[+]你选择：")
                if chose == '1':
                    available, allocation, need = comproc(allocation.copy(), available.copy(), need.copy(), max)
                else:
                    continue

        elif chose == '3':
            printTable(available, max, allocation, need)

        else:
            continue


if __name__ == '__main__':
    main()
