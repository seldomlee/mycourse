#-- coding:UTF-8 --
# author: Na0h
# app.py


import os
import sys
import datetime
import re
import random

import click
from flask import request, Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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


login_manager = LoginManager(app) # 实例化扩展类

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

login_manager.login_view = 'login'
login_manager.login_message = ""
# ================================command=====================================

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    # flask initdb --drop
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


def ctcarn():
    str = ['京', '津', '冀', '晋', '内蒙古', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '川', '蜀', '贵', '黔', '云', '滇', '渝', '藏', '陕', '秦', '甘', '陇', '青', '宁', '新', '港', '澳', '台']
    str1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    str2 = str1 + "1234567890"
    num = str[random.randint(0, 21)] + str1[random.randint(0, 25)] + "." + "".join(random.sample(str2, 5))
    return num


# 创建sqlite数据库文件
@app.cli.command()
def forge():
    db.create_all()

    # 插入数据
    for m in range(10):
        car = Car(carnum=ctcarn(), time=datetime.datetime.now().replace(microsecond=0))
        db.session.add(car)
    for i in range(5):
        car2 = WaitCar(carnum=ctcarn(), time=datetime.datetime.now().replace(microsecond=0))
        db.session.add(car2)
    for j in range(20):
        s = ['in', 'out']
        parlog = ParkLog(carnum=ctcarn(), status=s[random.randint(0, 1)], time=datetime.datetime.now().replace(microsecond=0))
        db.session.add(parlog)

    user = User(username='admin', name='Admin')
    user.set_password('admin123')  # 设置密码
    db.session.add(user)
    db.session.commit()
    click.echo('Done.')


# 在命令行返回一批车牌号
@app.cli.command()
def aa():
    str = ['京', '津', '冀', '晋', '内蒙古', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '川', '蜀', '贵', '黔', '云', '滇', '渝', '藏', '陕', '秦', '甘', '陇', '青', '宁', '新', '港', '澳', '台']
    str1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    str2 = str1 + "1234567890"
    for i in range(30):
        num = str[random.randint(0, 21)] + str1[random.randint(0, 25)] + "." + "".join(random.sample(str2, 5))
        click.echo(num)

# 创建admin用户
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')


# ================================类=====================================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Car(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    carnum = db.Column(db.String(20))
    time = db.Column(db.DateTime)


class WaitCar(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    carnum = db.Column(db.String(20))
    time = db.Column(db.DateTime)


class ParkLog(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    carnum = db.Column(db.String(20))
    status = db.Column(db.String(20))
    time = db.Column(db.DateTime)


# ================================方法=====================================

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
    str = ['京', '津', '冀', '晋', '内蒙古', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '川', '蜀', '贵', '黔', '云', '滇', '渝', '藏', '陕', '秦', '甘', '陇', '青', '宁', '新', '港', '澳', '台']
    if len(carnum) < 11:
        if carnum[0:3] == '内蒙古':
            if re.match('[A-Z]?\.[a-zA-Z0-9]{5}', carnum[3:]):
                return False
        elif carnum[0] in str:
            if re.match('[A-Z]?\.[a-zA-Z0-9]{5}', carnum[1:]):
                return False
    return True

# ================================页面=====================================

# 主页
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    maxc = 10    # 定义停车场最大车辆数
    page1 = int(request.args.get('page1', 1))
    page2 = int(request.args.get('page2', 1))
    a = Car.query.paginate(page1, per_page=5, error_out=False)
    b = WaitCar.query.paginate(page2, per_page=5, error_out=False)
    if page1 > a.pages or page1 < 1:
        page1 = 1
    if page2 > b.pages or page2 < 1:
        page2 = 1

    while (maxc - Car.query.count()) > 0 and WaitCar.query.count() > 0:
        chepavement(maxc)

    # 获取页面表单传输
    if request.method == 'POST':
        carnum = request.form.get('carnum')
        action1 = request.form.get('parkcar')
        action2 = request.form.get('getcar')
        action3 = request.form.get('tolog')
        action4 = request.form.get('searchcarb')
        action5 = request.form.get('logout')

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

            car = Car.query.filter(Car.carnum.like(carnum)).first()
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

        elif action5:
            return redirect(url_for('logout'))

    user = User.query.first()
    cars = Car.query.paginate(page1, per_page=5, error_out=False)
    wcars = WaitCar.query.paginate(page2, per_page=5, error_out=False)
    return render_template('index.html',
                           user=user,
                           cars=cars,
                           wcars=wcars,
                           clen=Car.query.count(),
                           len=WaitCar.query.count(),
                           carn=Car.query.count(),
                           last=(maxc - Car.query.count()),
                           time=datetime.datetime.now().replace(microsecond=0)
                           )


@app.route("/log", methods=['GET', 'POST'])
@login_required
def log():
    flag = 1
    page = int(request.args.get('page', 1))
    a = ParkLog.query.paginate(page, per_page=10, error_out=False)
    if page > a.pages or page < 1:
        page = 1

    pagination = ParkLog.query.paginate(page, per_page=10, error_out=False)

    if request.method == 'POST':
        back = request.form.get('backindex')
        searchcarn = request.form.get('searchcarnum')

        asearch = request.form.get('searchcarb')
        ahelps = request.form.get('help')
        adelalog = request.form.get('dellog')

        if back:
            return redirect(url_for('index'))

        elif asearch:
            if not searchcarn:
                flash('错误的输入')  # 显示错误提示
                return redirect(url_for('log'))  # 重定向回主页
            if ParkLog.query.filter(ParkLog.carnum.like('%'+searchcarn+'%')).count():
                pagination = ParkLog.query.filter(ParkLog.carnum.like('%'+searchcarn+'%')).paginate(page, per_page=ParkLog.query.filter(ParkLog.carnum.like('%'+searchcarn+'%')).count(), error_out=False)
                flag = 0

            if ParkLog.query.filter(ParkLog.time.like('%'+searchcarn+'%')).count():
                pagination = ParkLog.query.filter(ParkLog.time.like('%'+searchcarn+'%')).paginate(page, per_page=ParkLog.query.filter(ParkLog.time.like('%'+searchcarn+'%')).count(), error_out=False)
                flag = 0

            if ParkLog.query.filter(ParkLog.status == searchcarn).count():
                pagination = ParkLog.query.filter(ParkLog.status == searchcarn).paginate(page, per_page=ParkLog.query.filter(ParkLog.status == searchcarn).count(), error_out=False)
                flag = 0

        elif ahelps:
            flash('本系统使用的是模糊查询；eg：搜索 桂，就会搜索以桂为开头的车牌号的记录；搜索 2021-12-06，就会搜索当天所有记录')

        # 清空记录
        elif adelalog:
            parlog = ParkLog.query.order_by(ParkLog.status).all()
            if check_password_hash(User.query.first().password_hash, searchcarn):
                # 检查输入框中字符和用户密码的哈希值是否相等
                flash('密码正确，删除所有出入记录')
                for m in parlog:
                    db.session.delete(m)
                db.session.commit()
                return redirect(url_for('log'))
            else:
                flash('删除记录需要密码噢')
                return redirect(url_for('log'))

    return render_template('log.html', user=User.query.first(), pagination=pagination, flag=flag)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('错误的输入')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('登录成功~')
            return redirect(url_for('index'))  # 重定向到主页

        flash('无效的用户名或密码')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    # flash('请登录~')
    return redirect(url_for('index'))  # 重定向回首页


if __name__ =="__main__":
    app.run(debug=True, port=8080)
