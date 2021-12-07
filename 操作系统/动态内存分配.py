#-- coding:UTF-8 --
# author：Na0h

class Memory(object):
    def __init__(self, start, end, length, state=1, ID=0 ):     # 类的初始化方法，当创建这个类的实例时就会调用该方法
        self.Id = ID            # 分区号 (ID为0是未分配，其余为任务编号
        self.start = start      # 分区起始地址
        self.end = end          # 分区结束地址
        self.length = length    # 分区大小
        self.state = state      # 为1：表示内存未分配


def printmemory(list):  #   输出内存分配情况
    print("[*]分区号\t起始地址\t结束地址\t分区大小\t分配状态")
    for i in range(len(list)):
        if list[i].state == 1:
            st = "空闲"
        else:
            st = "已分配"
        print(f"[*]{list[i].Id}\t\t{list[i].start}\t\t{list[i].end}\t\t{list[i].length}\t\t{st}")


def up_bsort(list):   # 正序冒泡排序
    for i in range(len(list)):
        for j in range(i + 1, len(list)):
            if list[i].length < list[j].length:
                list[i], list[j] = list[j], list[i]
    return list


def low_bsort(list):   # 降序冒泡排序
    for i in range(len(list)):
        for j in range(i + 1, len(list)):
            if list[i].length > list[j].length:
                list[i], list[j] = list[j], list[i]
    return list


def freem(id, list):    #   回收空间
    for i in range(len(list)):
        if list[i].Id == id:
            list[i].state = 1
            list[i].Id = 0
            t = i
            break
    # 向前合并
    if t - 1 > 0:
       if list[t-1].state == 1:
            a = Memory(list[t-1].start, list[t-1].end, list[t-1].length + list[t].length, 1, 0)
            del list[t-1]
            del list[t-1]
            list.insert(t-1,a)
            t = t-1
    if t + 1 < len(list):
        if list[t+1].state == 1:
            a = Memory(list[t].start, list[t + 1].end, list[t].length + list[t+1].length, 1, 0)
            del list[t]
            del list[t]
            list.insert(t, a)
    printmemory(list)


# 动态分区分配算法

def FF(id, length, list):   #  首次适应算法
    for i in list:
        if i.Id == id:      #  检测是否已存在该作业号
            print(f"[*]已存在作业{i.Id}")
            return
    for i in range(len(list)):
        if list[i].state == 1 and list[i].length > length:  #   该分区未被分配，且未分配内存大小大于请求大小
            m1 = Memory(list[i].start, list[i].start + length - 1, length, state=0, ID=id)   #   被分配的分区
            m2 = Memory(list[i].start + length, list[i].end, list[i].length - length, 1, 0)  #   分配完毕后的空闲分区
            del list[i]
            list.insert(i, m2)
            list.insert(i, m1)
            printmemory(list)
            return
        if list[i].state == 1 and list[i].length == length:
            list[i].state = 0
            printmemory(list)
            return
    print("[*]空间不足")

def BF(id, length, list):   #   最佳适应算法
    for i in list:
        if i.Id == id:      #   检测是否已存在该作业号
            print(f"[*]已存在作业{i.Id}")
            return

    # 找满足要求的空闲分区
    m = up_bsort(list.copy())
    f1, f2 = -1, -1
    for i in range(len(m)):
        if m[i].state == 1 and m[i].length > length:
            f1 = m[i].start
        elif m[i].state == 1 and m[i].length == length:
            f2 = m[i].start
    if f1 == -1 and f2 == -1:
        print("[*]空间不足")
        return

    for i in range(len(list)):
        if list[i].start == f1:
            m1 = Memory(list[i].start, list[i].start + length - 1, length, state=0, ID=id)   #   被分配的分区
            m2 = Memory(list[i].start + length, list[i].end, list[i].length - length, 1, 0)  #   分配完毕后的空闲分区
            del list[i]
            list.insert(i, m2)
            list.insert(i, m1)
            printmemory(list)
            return
        elif list[i].start == f2:
            list[i].state = 0
            printmemory(list)
            return

def WF(id, length, list):   #   最坏适应算法
    for i in list:
        if i.Id == id:      #   检测是否已存在该作业号
            print(f"[*]已存在作业{i.Id}")
            return

    # 找满足要求的空闲分区
    m = low_bsort(list.copy())
    f1, f2 = -1, -1
    for i in range(len(m)):
        if m[i].state == 1 and m[i].length > length:
            f1 = m[i].start
        elif m[i].state == 1 and m[i].length == length:
            f2 = m[i].start
    if f1 == -1 and f2 == -1:
        print("[*]空间不足")
        return

    for i in range(len(list)):
        if list[i].start == f1:
            m1 = Memory(list[i].start, list[i].start + length - 1, length, state=0, ID=id)   #   被分配的分区
            m2 = Memory(list[i].start + length, list[i].end, list[i].length - length, 1, 0)  #   分配完毕后的空闲分区
            del list[i]
            list.insert(i, m2)
            list.insert(i, m1)
            printmemory(list)
            return
        elif list[i].start == f2:
            list[i].state = 0
            printmemory(list)
            return

def main():
    size = int(input("[+]输入内存大小: "))
    a = Memory(0, size - 1, size, state=1, ID=0)
    b = []
    b.append(a)
    while True:
        print("[*]1.初始化内存空间\r\n[*]2.分配空间\r\n[*]3.回收\r\n[*]4.查看当前内存分配情况\r\n")
        chose = input("[+]你选择: ")
        if chose == '1':
            print("[+]输入内存大小: ")
            size = int(input())
            a = Memory(0, size - 1, size, state=1, ID=0)
            b = []
            b.append(a)
        elif chose == '2':
            print("[*]1.首次适应算法：FF\r\n[*]2.最佳适应算法：BF\r\n[*]3.最坏适应算法：WF\r\n[*]其他则返回上一界面")
            x = input("[+]请输入分配执行的算法: ")
            x = float(x)
            flag = 'y'
            while (flag == 'y'):
                if x == 1:
                    work_size = input('[+]请输入作业id和大小: ').split()
                    FF(work_size[0], int(work_size[1]), b)
                    flag = input('[+]是否继续y/n: ')
                elif x == 2:
                    work_size = input('[+]请输入作业id和大小: ').split()
                    BF(work_size[0], int(work_size[1]), b)
                    flag = input('[+]是否继续y/n: ')
                elif x == 3:
                    work_size = input('[+]请输入作业id和大小: ').split()
                    WF(work_size[0], int(work_size[1]), b)
                    flag = input('[+]是否继续y/n: ')
                else:
                    break
        elif chose == '3':
            id_delete = input('[+]请输入删除作业id: ')
            freem(id_delete, b)
        elif chose == '4':
            printmemory(b)

if __name__ == '__main__':
    main()