import json
import logging
import threading
import airtest.core.api as air

logging.getLogger("airtest").setLevel(logging.INFO)

air.auto_setup(__file__)
air.ST.FIND_TIMEOUT_TMP = 1
# air.ST.SAVE_IMAGE = False

resolution = air.G.DEVICE.get_current_resolution()
''' 默认分辨率 = 1920 * 1080 '''
NOP = (700, 900)
''' 无操作 / 确定 '''
default_sleep_time = json.load(open('default_setting.json',
                                    encoding='utf-8'))['default_sleep_time']
''' 默认等待时间：如果设备太卡，可以调大一点 '''


def trans_position(p):
    """ 数值都是根据默认分辨率设置的，对于不同分辨率的设备需要重新计算坐标 """
    return (p[0] * resolution[0] / 1920, p[1] * resolution[1] / 1080)


def touch(p, times=1):
    if isinstance(p, str):
        air.touch(template(p), times=times)
    elif isinstance(p, tuple):
        air.touch(trans_position(p), times=times)
    else:
        air.touch(p, times=times)
    sleep(default_sleep_time)


def exists(img):
    if isinstance(img, str):
        img = template(img)
    return air.exists(img)


def try_touch(img):
    pos = exists(img)
    if pos:
        air.touch(pos)
        return True
    return False


def swipe(p1, p2, duration=1):
    p1, p2 = map(trans_position, [p1, p2])
    air.swipe(p1, p2, duration)


def template(name, threshold=None, rgb=False, target_pos=0):
    return air.Template(r'%s' % ('images\\' + name + '.png'),
                        threshold=threshold,
                        rgb=rgb,
                        target_pos=target_pos,
                        resolution=[1920, 1080])


def sleep(time=default_sleep_time):
    air.sleep(time)


def swipe_screen():
    """ 向右滑动屏幕 """
    swipe((1800, 500), (950, 500), duration=.5)
    sleep(1)


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        return self.result


def check(dict):
    def check(name, img):
        return name if exists(img) else None

    dic = list(dict.items())
    if len(dic) > 4:
        for name, img in dic[:2]:
            res = check(name, img)
            if res is not None:
                return [res]
        dic = dic[2:]
    threads = [MyThread(check, args=item) for item in dic]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    res = [t.get_result() for t in threads]
    return [v for v in res if v if not None]


class AutoProspectiveInvestment:
    def __init__(self):
        self.guard_operator_exist = True
        ''' 是否有核心近卫，默认为有 '''
        squad = json.load(open('default_setting.json',
                               encoding='utf-8'))['squad']
        ''' 编队 = [近卫, 辅助, 医疗]，第一层实际上只要单近卫就行了 '''
        operator = json.load(open('operator.json', encoding='utf-8'))
        squad = [operator[name] for name in squad[:3]]
        for info in squad:
            for str in ['recruit', 'assist']:
                if str in info:
                    info[str] = template(info[str], threshold=.8)
            info['class_img'] = template('职业-' + info['class'], threshold=.3)
        self.squad = squad

        def trans(a, prefix, rgb=False, targat=0):
            return {
                name: template(prefix + name, rgb=rgb, target_pos=targat)
                for name in a
            }

        self.operation_task = json.load(
            open('operation_tasks.json', encoding='utf-8'))
        ''' 作战关卡操作 '''

        node_list = ['不期而遇', '作战', '地区委托', '兴致盎然', '得偿所愿', '诡意行商', '紧急作战']
        self.node_list = trans(node_list, '节点-', rgb=True)
        ''' 节点名称列表 '''

        option_list = ['离开', '希望', '源石锭', '掷骰次数', '钥匙', '问号']
        self.option_list = trans(option_list, '选择-', rgb=True)
        ''' 事件选项列表 '''

        operation_list = ['共生', '蓄水池', '虫群横行', '射手部队']
        self.operation_list = trans(operation_list, '作战-')
        ''' 关卡名称列表 '''

        recruitment = ['近卫', '辅助', '医疗']
        self.recruitment = trans(recruitment, '招募券-', targat=8)
        ''' 招募券 '''

    def run(self):
        support = True  # 更多支援
        start = template('开始探索')
        team = template('分队-指挥分队', target_pos=8)
        combination = template('组合-取长补短', target_pos=8)
        while (True):
            # 开始探索
            while not try_touch(start):
                touch(NOP, times=5)
            sleep(default_sleep_time * 2)
            # 如果存在更多支援
            if support:
                if exists('更多支援'):
                    touch((1000, 800))
                    touch((1000, 800))
                    try_touch('确认-藏品')
                support = False
            # 选择指挥分队
            touch(team)  # 指挥分队
            touch(team)  # 确认
            # 选择取长补短
            touch(combination)  # 取长补短
            touch(combination)  # 确认
            # 招募干员
            self.recruit_operators()
            # 探索海洋
            touch((1800, 540))  # 探索海洋
            # 调整编队
            self.adjust_squad()
            # 第一关
            touch((600, 480))  # 第一关
            self.start_operation()
            # 遍历后续节点
            while self.next_step():
                pass
            # 退出
            if try_touch('退出'):
                sleep(.5)
                touch('放弃本次探索')
                touch('确定-放弃')
            # 结算
            air.wait(template('下一步'))
            touch('下一步')
            touch(NOP, times=30)

    def quit_recruit(self, times=3):
        while times > 0 and try_touch('放弃'):
            times -= 1
            sleep()
            touch('确定-放弃')

    def recruit_operators(self):
        skip = (1830, 60)  # skip

        def recruit(recruit, operator, assist=False):
            air.wait(recruit)
            touch(recruit)  # 招募券
            sleep()
            if operator is None:
                self.quit_recruit(1)
                return
            cnt = 0
            if not assist:
                op = operator['recruit']
                while cnt < 4 and not try_touch(op):
                    swipe_screen()
                    cnt += 1
                if cnt >= 4:
                    assist = True
                    self.guard_operator_exist = False
                else:
                    touch((1800, 1000))  # 确认招募
            if assist:
                touch((1600, 50))  # 选择助战
                sleep(.5)
                op = operator['assist']
                while cnt < 7 and not try_touch(op):
                    touch((1800, 50))  # 更新助战列表
                    sleep(3)
                    cnt += 1
                if cnt >= 7:
                    touch((140, 50))  # 退出
                    self.quit_recruit(1)
                    return
                sleep(1)
                touch((1200, 770))  # 确认招募
            touch(skip)
            touch(skip)

        recruit(self.recruitment['近卫'], self.squad[0],
                not self.guard_operator_exist)
        recruit(self.recruitment['辅助'],
                None if len(self.squad) < 2 else self.squad[1])
        recruit(self.recruitment['医疗'],
                None if len(self.squad) < 3 else self.squad[2])
        return

    def adjust_squad(self):
        """ 调整编队 """
        air.wait(template('编队'))
        sleep()
        touch((1660, 1000))  # 编队
        touch((1500, 60))  # 快捷编队
        touch((800, 200))  # 近卫
        if self.squad[0]['skill_id'] == 2:
            touch((300, 800))  # 切换2技能
        if len(self.squad) > 1:
            touch((800, 400))  # 安塞尔
            if len(self.squad) > 2:
                touch((800, 600))  # 梓兰
        touch((1700, 1000))  # 确认
        touch((140, 50))  # 返回
        return

    def next_step(self):
        sleep(default_sleep_time * 4)
        for name in check(self.node_list):
            touch(self.node_list[name])
            if name == '不期而遇':
                self.excounter_chance_meeting()
            elif name == '地区委托':
                self.excounter_regional_entrustment()
            elif name == '兴致盎然':
                self.downtime_recreation()
            elif name == '得偿所愿':
                self.excounter_wish_fulfillment()
            elif name == '诡意行商':
                self.rogue_trader()
                return False
            elif name == '作战' or name == '紧急作战':
                if self.start_operation():
                    return False
            return True
        return False

    def start_operation(self):
        """ 开始行动 """
        res = check(self.operation_list)
        if len(res) == 0:
            return True
        res = res[0]
        touch('出发前往')
        touch('开始行动')
        try_touch('确定-钥匙')
        speed = template('2倍速')
        air.wait(speed)
        sleep(default_sleep_time * 4)
        air.touch(speed)
        cost = 10
        for op in self.squad:
            position = exists(op['class_img'])  # 找到职业图标
            if position is False:
                touch((110, 80))  # 设置
                touch((1100, 520))  # 放弃行动
                return True
            sleep(max(0, op['cost'] - cost) / 2)  # 等费用
            task = self.operation_task[res][op['class']]  # 某职业干员在该关卡的操作信息
            place = trans_position(task['place'])
            air.swipe(position, place,
                      duration=default_sleep_time / 2)  # 拖干员到位置
            dx, dy = task['direction']
            dst = (place[0] + dx * 200, place[1] + dy * 200)
            air.swipe(place, dst, duration=default_sleep_time / 3)  # 设置朝向
            cost += 8 - op['cost']
            if op['skill_click']:
                cost += op['skill_cd'] + 2
                skill = template('技能')
                air.wait(skill)
                pos = exists(skill)
                pos = pos[0], pos[1] + 0.1 * resolution[1]
                air.touch(pos)  # 点击干员
                touch((1300, 600))  # 开技能
        sleep(55)  # 等待战斗结束
        while not exists('成功通过'):
            sleep(5)
            if try_touch('联系中断'):
                return True
        sleep(2)
        touch(NOP)
        sleep(1)
        touch('收下源石锭')
        sleep(1.5)
        while not try_touch('不要了走了'):
            swipe_screen()
        touch('确定-离开')
        return False

    def excounter_chance_meeting(self):
        """ 不期而遇 """
        touch('出发前往')
        sleep(1)
        try_touch('确定-钥匙')
        touch(NOP, times=5)
        sleep(1)
        res = check(self.option_list)
        if len(res) == 0:
            touch((1800, 600))
        else:
            touch(self.option_list[res[0]])
        touch('确定-选择')
        touch(NOP, times=15)
        if len(res) == 0 or res == '问号':
            self.quit_recruit()
            touch(NOP, times=15)

    def excounter_wish_fulfillment(self):
        """ 得偿所愿 """
        touch('出发前往')
        sleep(1)
        try_touch('确定-钥匙')
        touch(NOP, times=2)
        sleep(1)
        touch('收藏品')
        touch('确定-选择')
        air.wait(template('确定-投掷'))
        touch('确定-投掷')
        touch(NOP, times=15)
        self.quit_recruit()
        touch(NOP, times=15)
        self.quit_recruit()
        touch(NOP, times=15)

    def downtime_recreation(self):
        """ 兴致盎然 """
        touch('出发前往')
        sleep(1)
        touch(NOP, times=5)
        touch('选择-离开')
        touch('确定-选择')
        touch(NOP, times=5)
        touch('选择-源石锭')
        touch('确定-选择')
        touch(NOP, times=5)

    def excounter_regional_entrustment(self):
        """ 地区委托 """
        touch('出发前往')
        sleep(1)
        touch(NOP, times=2)
        sleep(1)
        touch('选择-离开')
        touch('确定-选择')
        touch(NOP, times=15)

    def rogue_trader(self):
        """  诡意行商前瞻性投资 """
        touch('出发前往')
        sleep(1)
        if try_touch('前瞻性投资系统'):
            touch('投资入口')
            touch((1400, 740), times=50)  # 确认投资


script = AutoProspectiveInvestment()
script.run()

