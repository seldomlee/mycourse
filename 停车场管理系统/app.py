#-- coding:UTF-8 --
# author: Na0h

import os
import sys
import datetime
import re
import random

import click
from flask import request, Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'    # 等同于 app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# 随机创建车牌号
def ctcarn():
    str = ['辽', '吉', '黑', '冀', '晋', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '琼', '川', '贵', '云', '陕', '甘', '青']
    str1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    str2 = str1 + "1234567890"
    num = str[random.randint(0, 21)] + str1[random.randint(0, 25)] + "." + "".join(random.sample(str2, 5))  # 随机生成车牌号
    return num
    # if num[0] in str:
    #     print(re.match('[A-Z]?\.[a-zA-Z0-9]{5}', num[1:]))


# 创建sqlite数据库文件
@app.cli.command()
def forge():
    db.create_all()

    # 插入数据
    cars, cars1, cars2 = [], [], []
    for a in range(5):
        z = {'carnum': f'{ctcarn()}'}
        cars.append(z)
    for b in range(5):
        z = {'carnum': f'{ctcarn()}'}
        cars1.append(z)
    for c in range(20):
        z = {'carnum': f'{ctcarn()}'}
        cars2.append(z)
    for m in cars:
        car = Car(carnum=m['carnum'], time=datetime.datetime.now().replace(microsecond=0))
        db.session.add(car)
    for i in cars1:
        car2 = WaitCar(carnum=i['carnum'], time=datetime.datetime.now().replace(microsecond=0))
        db.session.add(car2)
    for j in cars2:
        s = ['in', 'out']
        parlog = ParkLog(carnum=j['carnum'], status=s[random.randint(0, 1)], time=datetime.datetime.now().replace(microsecond=0))
        db.session.add(parlog)

    name = 'Na0H'
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    click.echo('Done.')


# 数据库类
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Car(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    carnum = db.Column(db.String(20), primary_key=True)
    time = db.Column(db.DateTime)


class WaitCar(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    carnum = db.Column(db.String(20), primary_key=True)
    time = db.Column(db.DateTime)


class ParkLog(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    carnum = db.Column(db.String(20))
    status = db.Column(db.String(20))
    time = db.Column(db.DateTime)


def inpavement(carnum):
    car = WaitCar(carnum=carnum, time=datetime.datetime.now().replace(microsecond=0))
    db.session.add(car)
    db.session.commit()
    # flash('车牌号为：' + car.carnum + ' 的车辆已进入便道等待')


# 检测是否还有等待的车辆，有则将其放入停车场
def chepavement(maxc):
    if WaitCar.query.count():   # 便道有车
        if Car.query.count() < maxc:    # 且停车场有空位
            pcar = WaitCar.query.first()
            car = Car(carnum=pcar.carnum, time=datetime.datetime.now().replace(microsecond=0))
            parlog = ParkLog(carnum=pcar.carnum, status='in', time=datetime.datetime.now().replace(microsecond=0))

            db.session.delete(pcar)  # 退出便道
            db.session.add(car)      # 停入停车场
            db.session.add(parlog)
            db.session.commit()      # 提交
            flash('便道中车牌号为：' + pcar.carnum + ' 的车辆已成功停入停车场\r\n，等待时间为：'+str((datetime.datetime.now().replace(microsecond=0)-pcar.time).seconds)+'秒')


# 检查车牌号是否已经存在
def checkexist(carnum):
    for i in Car.query.all():
        if carnum == i.carnum:
            flash('错误的输入')
            redirect(url_for('index'))
            return False
    for j in WaitCar.query.all():
        if carnum == j.carnum:
            flash('错误的输入')
            redirect(url_for('index'))
            return False
    return True


# 检测是否为车牌号
def checkcarn(carnum):
    str = ['辽', '吉', '黑', '冀', '晋', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '琼', '川', '贵', '云', '陕', '甘', '青']
    if carnum[0] in str:
        if re.match('[A-Z]?\.[a-zA-Z0-9]{5}', carnum[1:]):
            return False
    return True


# 主页
@app.route('/', methods=['GET', 'POST'])
def index():
    maxc = 5    # 定义停车场最大车辆数

    # 获取页面表单传输
    if request.method == 'POST':
        carnum = request.form.get('carnum')
        action1 = request.form.get('parkcar')
        action2 = request.form.get('getcar')
        action3 = request.form.get('tolog')
        action4 = request.form.get('searchcarb')

        # 停车
        if action1:
            if not carnum:
                flash('错误的输入')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页

            if checkcarn(carnum):
                flash('非法输入')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页

            if checkexist(carnum):
                if not Car.query.count() < maxc:
                    flash('停车场已满，车牌号为：'+carnum+' 的车辆进入便道等待')

                    inpavement(carnum)
                    return redirect(url_for('index'))

                # 保存表单数据到数据库
                car = Car(carnum=carnum, time=datetime.datetime.now().replace(microsecond=0))  # 创建记录
                parlog = ParkLog(carnum=carnum, status='in', time=datetime.datetime.now().replace(microsecond=0))
                db.session.add(car)  # 添加到数据库会话
                db.session.add(parlog)
                db.session.commit()  # 提交数据库会话
                flash('停车成功，车牌号为：'+carnum+' 的车辆已成功停入停车场')
                return redirect(url_for('index'))  # 重定向回主页

        # 取车
        elif action2:
            if not carnum:
                flash('错误的输入')
                return redirect(url_for('index'))

            if checkcarn(carnum):
                flash('非法输入')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页

            car = Car.query.get(carnum)
            if not car:
                flash('停车场中不存在该车辆')
                return redirect(url_for('index'))

            parlog = ParkLog(carnum=car.carnum, status='out', time=car.time)
            db.session.delete(car)  # 从数据库会话删除
            db.session.add(parlog)
            db.session.commit()
            flash('取车成功，车牌号为：'+car.carnum+' 的车辆离开停车场，您的停车时长为：'+str((datetime.datetime.now().replace(microsecond=0)-car.time).seconds)+'秒')
            chepavement(maxc)
            return redirect(url_for('index'))

        # 跳转到日志界面
        elif action3:
            return redirect(url_for('log'))

        # 查询
        elif action4:
            if not carnum:
                flash('错误的输入')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页

            if checkcarn(carnum):
                flash('非法输入')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页

            for i in Car.query.all():
                if carnum == i.carnum:
                    flash('车辆存在，车牌号为：'+carnum+'的车辆正停放在停车场中')
                    return redirect(url_for('index'))
            for j in WaitCar.query.all():
                if carnum == j.carnum:
                    flash('该车辆存在，车牌号为：'+carnum+'的车辆正在便道中等待')
                    return redirect(url_for('index'))

            flash('停车场中不存在该车辆')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页

    user = User.query.first()
    cars = Car.query.all()
    wcars = WaitCar.query.all()
    return render_template('index.html',
                           user=user,
                           cars=cars,
                           wcars=wcars,
                           clen=Car.query.count(),
                           len=WaitCar.query.count(),
                           carn=Car.query.count(),
                           last=(maxc - Car.query.count()),
                           )


@app.route('/log', methods=['GET', 'POST'])
def log():
    user = User.query.first()
    parlog = ParkLog.query.order_by(ParkLog.status).all()
    len = 0

    if request.method == 'POST':
        back = request.form.get('backindex')
        searchcarn = request.form.get('searchcarnum')
        sec = request.form.get('sec')
        action1 = request.form.get('sortcar')
        action2 = request.form.get('sorttime')
        action3 = request.form.get('sortsta')
        action4 = request.form.get('searchcarb')
        action5 = request.form.get('help')
        action6 = request.form.get('dellog')

        if back:
            return redirect(url_for('index'))

        # 按车牌排序
        elif action1:
            parlog = ParkLog.query.order_by(ParkLog.carnum).all()

        # 按时间排序
        elif action2:
            parlog = ParkLog.query.order_by(ParkLog.time).all()

        # 按状态排序
        elif action3:
            parlog = ParkLog.query.order_by(ParkLog.status).all()

        # 查询
        elif action4:
            if not searchcarn:
                flash('错误的输入')  # 显示错误提示
                return redirect(url_for('log'))  # 重定向回主页
            if ParkLog.query.filter(ParkLog.carnum.like('%'+searchcarn+'%')).count():
                parlog = ParkLog.query.filter(ParkLog.carnum.like('%'+searchcarn+'%')).all()
                len = ParkLog.query.filter(ParkLog.carnum.like('%'+searchcarn+'%')).count()

            elif ParkLog.query.filter(ParkLog.time.like('%'+searchcarn+'%')).count():
                parlog = ParkLog.query.filter(ParkLog.time.like('%'+searchcarn+'%')).all()
                len = ParkLog.query.filter(ParkLog.time.like('%'+searchcarn+'%')).count()

            elif ParkLog.query.filter(ParkLog.status == searchcarn).count():
                parlog = ParkLog.query.filter(ParkLog.status == searchcarn).all()
                len = ParkLog.query.filter(ParkLog.status == searchcarn).count()

        elif action5:
            flash('本系统使用的是模糊查询，可按车牌号、省份、日期、出入状态查找')
            flash('搜索 桂，就会搜索以桂为开头的车牌号的记录')
            flash('搜索 2021-12-06，就会搜索所有当天记录')

        # 清空记录
        elif action6:
            if searchcarn == 'xxx':
                flash('密码正确，删除所有出入记录')
                for m in parlog:
                    db.session.delete(m)
                db.session.commit()
                return redirect(url_for('log'))
            else:
                flash('删除记录需要管理员密码噢')
                return redirect(url_for('log'))

    return render_template('log.html',
                           user=user,
                           parlog=parlog,
                           len=len,
                           alllen=ParkLog.query.count()
                           )


if __name__ =="__main__":
    app.run(host='192.168.0.75', debug=True, port=8080)
