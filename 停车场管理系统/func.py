import re
import random
import datetime

class Stack(object):    # 栈
    def __init__(self):
        self.stack = []

    def push(self, value):    # 入栈
        self.stack.append(value)

    def pop(self):      # 出栈
        if self.stack:
            return self.stack.pop()
        else:
            raise LookupError('stack is empty!')

    def top(self):
        # 取出栈顶元素
        return self.stack[-1]


class Head(object):     # 头指针
    def __init__(self):
        self.left = None
        self.right = None


class Node(object):     # 指针
    def __init__(self, value):
        self.value = value
        self.next = None


class Queue(object):    # 队列

    def __init__(self):    # 初始化节点
        self.head = Head()

    def enqueue(self, value):    # 插入一个元素
        newnode = Node(value)
        p = self.head
        if p.right:    # head右结点不为None，说明队列存在元素
            temp = p.right
            p.right = newnode
            p.right.next = temp
        else:    # 这说明队列为空，插入第一个元素
            p.right = newnode
            p.left = newnode

    def dequeue(self):    # 取出一个元素
        p = self.head
        temp = p.left
        if p.left and (p.left == p.right):  # 队列中有元素且为最后一个
            p.left = p.right = None
            return temp.value

        elif p.left and (p.left != p.right):    # 队列中存在不止一个的元素
            pp = p.right
            while pp:
                if pp.next == p.left:
                    p.left = pp
                    pp.next = None
                    return temp.value
                else:
                    pp = pp.next

        else:   # 队列为空，抛出错误
            raise LookupError('queue is empty!')

    def top(self):  # 查询目前队列中最早入队的元素
        if self.head.left:
            return self.head.left.value
        else:
            raise LookupError('queue is empty!')


class Car(object):      # 车辆信息，包含车牌、到达/离去信息、到达/离去时间
    def __init__(self):
        str = ['辽', '吉', '黑', '冀', '晋', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '琼', '川', '贵', '云', '陕', '甘',
               '青']
        str1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        str2 = str1 + "1234567890"
        self.num = str[random.randint(0, 21)] + str1[random.randint(0, 14)] + "." + "".join(random.sample(str2, 5))   # 随机生成车牌号
        self.flag = 0   # 标志车辆是否在停车场内，1表示车辆不在停车场里
        self.time = 0   # 先置0，在进入/离开停车场可用time.time()获取当前时间


def printpavement(pavement):
    p = pavement.head
    if p.right:
        p = p.right
        while p:
            print(p.value.num)
            p = p.next


def checkcarn():
    str = ['辽', '吉', '黑', '冀', '晋', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '琼', '川', '贵', '云', '陕', '甘', '青']
    str1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    str2 = str1 + "1234567890"
    num = str[random.randint(0, 21)] + str1[random.randint(0, 25)] + "." + "".join(random.sample(str2, 5))  # 随机生成车牌号
    print(num)

    if num[0] in str:
        print(re.match('[A-Z]?\.[a-zA-Z0-9]{5}', num[1:]))


def main():
    # 初始化
    park = Stack()      # 停车场
    qroad = Stack()     # 退出时用来存放车辆的道路
    pavement = Queue()  # 便道
    max = 20

    while True:
        print("==" * 30)
        print("[*]1、停车\r\n[*]2、取车\r\n[*]3、输出当前停车场的车辆\r\n[*]4、输出当前便道的车辆")
        chose = input("[+]你选择: ")
        if chose == '1':
            if len(park.stack) >= max:
                print("==" * 30)
                print("[*]停车场已满，需停到便道上~")
                ch = input("[+]是否要停入便道呢？：1/0")
                if ch == '1':
                    tempc = Car()
                    pavement.enqueue(tempc)
                    print("==" * 30)
                    print(f"[*]车牌号为 {tempc.num} 的车辆已停入便道等待")

            else:
                park.push(Car())
                carnum = len(park.stack) - 1
                park.stack[carnum].time = datetime.datetime.now().replace(microsecond=0)
                park.stack[carnum].flag = 1
                print("==" * 30)
                print(f"[*]停车成功~，车牌号为 {park.stack[carnum].num} 的车辆已停入 {carnum} 号车位\r\n[*]停车时间为：{park.stack[carnum].time}")

        elif chose == '2':
            cnum = input("[+]请输入要取出车辆的车牌号：")
            for i in range(len(park.stack)):    # 找到车辆所在的位置
                if cnum == park.stack[i].num:
                    pos = i
                    poscar = park.stack[i]
                    time2 = datetime.datetime.now().replace(microsecond=0)
                    print("==" * 30)
                    print(f"[*]车牌号为{cnum}的车辆离去，停留时间为：{(time2-poscar.time).seconds}秒")

            for i in range(pos, len(park.stack)):   # 在该车之后进入的车辆都要先退出
                qroad.push(park.pop())

            while qroad.stack:  # 退出的车再进入
                tempcar = qroad.pop()
                if poscar.num != tempcar.num:
                    park.push(tempcar)

            if pavement.head.right:     # 检查便道是否有车辆停留
                while len(park.stack) < max:   # 检查停车场是否已满
                    temp = pavement.dequeue()
                    temp.time = datetime.datetime.now().replace(microsecond=0)
                    temp.flag = 1
                    print(f"[*]便道中存在车辆且停车场存在空位，将其停入\r\n[*]车牌号为 {temp.num} 的车辆已停入停车场\r\n[*]停车时间为：{temp.time}")
                    park.push(temp)


        elif chose == '3':
            print("==" * 30)
            if park.stack:
                a = []
                print(f"[*]停车位\t  车牌号\t\t  停入时间")
                for i in range(len(park.stack)):
                    b = {'carnum': f'{park.stack[i].num}', 'time': f'{park.stack[i].time}'}
                    a.append(b)
                    print(f"[*]{i:^5}\t{park.stack[i].num}\t  {park.stack[i].time}")
                # print(a)
            else:
                print("[*]当前停车场没有车辆噢~")

        elif chose == '4':
            printpavement(pavement)


if __name__ == '__main__':
    main()