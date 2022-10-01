import json
import logging
import airtest.core.api as air

# logging.getLogger("airtest").setLevel(logging.INFO)

air.auto_setup(__file__)
air.ST.FIND_TIMEOUT_TMP = 1

resolution = air.G.DEVICE.get_current_resolution()
# resolution = [1920, 1080]
''' 默认分辨率 = 1920 * 1080 '''


def trans_position(p):
    """ 数值都是根据默认分辨率设置的，修改分辨率后需要重新计算坐标 """
    return (p[0] * resolution[0] / 1920, p[1] * resolution[1] / 1080)


NOP = (700, 900)
''' 无操作 / 确定 '''


def touch(p, times=1):
    if isinstance(p, str):
        air.touch(template(p), times=times)
    elif isinstance(p, tuple):
        air.touch(trans_position(p), times=times)
    else:
        air.touch(p, times=times)


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


def template(name, threshold=None, rgb=False):
    return air.Template(r'%s' % ('images\\' + name + '.png'),
                        threshold=threshold,
                        rgb=rgb,
                        resolution=resolution)


def sleep(time):
    air.sleep(time)


def swipe_screen():
    """ 向右滑动屏幕 """
    swipe((1800, 500), (950, 500), duration=.5)
    sleep(1)


class Auto_Prospective_Investment:
    def __init__(self):
        with open('defualt_setting.json', encoding='gbk') as f:
            data = json.load(f)
            self.guard_operator_exist = data['guard_operator_exist']
            ''' 是否有核心近卫 '''
            squad = data['squad']
            ''' 编队 = [近卫, 辅助, 医疗]，近卫非空，其余无所谓（如果能过的话） '''
        operator = json.load(open('operator.json', encoding='gbk'))
        squad = [operator[name] for name in squad[:3]]
        for info in squad:
            for str in ['recruit', 'assist']:
                if str in info:
                    info[str] = template(info[str], threshold=.8)
            info['class_img'] = template('职业-' + info['class'], threshold=.3)
        squad.extend([None] * (3 - len(squad)))
        self.squad = squad

        def trans(a, prefix, rgb=False):
            return {name: template(prefix + name, rgb=rgb) for name in a}

        with open('operation_tasks.json', encoding='gbk') as f:
            self.operation_task = json.load(f)
            ''' 作战关卡操作 '''

        node_list = ['不期而遇', '作战', '紧急作战', '诡意行商', '地区委托', '兴致盎然', '得偿所愿']
        self.node_list = trans(node_list, '节点-', rgb=True)
        ''' 节点名称列表 '''

        option_list = ['离开', '希望', '源石锭', '掷骰次数', '钥匙', '问号']
        self.option_list = trans(option_list, '选择-', rgb=True)
        ''' 事件选项列表 '''

        operation_list = ['共生', '蓄水池', '虫群横行', '射手部队']
        self.operation_list = trans(operation_list, '作战-')
        ''' 关卡名称列表 '''

    def run(self):
        while (True):
            # 开始探索
            air.wait(template('探索'))
            touch((1740, 880))
            sleep(1)
            # 选择指挥分队
            touch((1540, 872))
            sleep(.6)
            touch((1540, 872))
            sleep(.6)
            # 选择取长补短
            touch((1173, 875))
            sleep(.6)
            touch((1173, 875))
            sleep(1)
            # 招募干员
            self.recruit_operators()
            # 探索海洋
            touch((1800, 540))
            # 调整编队
            self.adjust_squad()
            # 第一关
            touch((600, 500))
            self.start_operation()
            # 遍历后续节点
            while self.next_step():
                pass
            # 退出
            if try_touch('退出'):
                sleep(.5)
                touch('放弃本次探索')
                sleep(.5)
                touch('确定-放弃')
            # 结算
            air.wait(template('下一步'))
            touch('下一步')
#             air.wait(template('确定-结算'))
#             touch('确定-结算')
            touch(NOP, times=30)

    def quit_recruit(self):
        while try_touch('放弃'):
            sleep(.5)
            touch('确定-放弃')
            sleep(1)

    def recruit_operators(self):
        skip = (1830, 60)
        sleep_time = .6  # 网络不好调大点

        def recruit(recruit, operator, assist=False):
            touch(recruit)  # 招募券
            sleep(sleep_time)
            if operator is None:
                self.quit_recruit()
                return
            cnt = 0
            if assist:
                touch((1600, 50))  # 选择助战
                operator = operator['assist']
                while not try_touch(operator) and cnt < 7:
                    touch((1800, 50))  # 更新助战列表
                    sleep(4)
                if cnt > 7:
                    touch((140, 50))
                    sleep(.3)
                    self.quit_recruit()
                    return
                sleep(sleep_time)
                touch((1200, 770))  # 确认招募
            else:
                operator = operator['recruit']
                while not try_touch(operator) and cnt < 4:
                    swipe_screen()
                    cnt += 1
                if cnt > 3:
                    self.quit_recruit()
                    return
                sleep(sleep_time)
                touch((1800, 1000))  # 确认招募
            sleep(sleep_time)
            touch(skip)
            sleep(sleep_time)
            touch(skip)
            sleep(sleep_time / 2)

        for i in range(3):
            recruit((530 + 435 * i, 800), self.squad[i], i == 0
                    and not self.guard_operator_exist)
        return

    def adjust_squad(self):
        """ 调整编队 """
        air.wait(template('编队'))
        sleep(1)
        touch((1660, 1000))  # 编队
        sleep(.3)
        touch((1500, 60))  # 快捷编队
        sleep(.3)
        touch((800, 200))  # 近卫
        sleep(.3)
        if self.squad[0]['skill_id'] == 2:
            touch((300, 800))  # 切换2技能
            sleep(.3)
        touch((800, 400))  # 安塞尔 or 梓兰
        sleep(.3)
        touch((800, 600))  # 梓兰 or 安塞尔
        sleep(.3)
        touch((1700, 1000))  # 确认
        sleep(.3)
        touch((140, 50))  # 返回
        return

    def next_step(self):
        sleep(2)
        for name, img in self.node_list.items():
            if try_touch(img):
                sleep(.5)
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
        result = None
        for name, img in self.operation_list.items():
            if air.exists(img):
                result = name
                break
        if result is None:
            return True
        touch('出发前往')
        sleep(.5)
        touch('开始行动')
        sleep(.5)
        try_touch('确定-钥匙')
        speed = template('2倍速')
        air.wait(speed)
        sleep(2)
        air.touch(speed)
        sleep(.5)
        cost = 12
        for op in self.squad:
            if op is None:
                continue
            sleep(max(0, op['cost'] - cost) / 2)
            position = air.exists(op['class_img'])
            if position is False:
                touch((110, 80))
                sleep(.5)
                touch((1100, 520))
                sleep(.5)
                return True
            task = self.operation_task[result][op['class']]
            place = trans_position(task['place'])
            air.swipe(position, place, duration=.1)  # 拖干员到位置
            air.swipe(place, vector=task['direction'], duration=.05)  # 设置朝向
            cost += 8 - op['cost']
            if op['skill_click'] and 'click' in task:
                sleep(op['skill_cd'] / 2)
                cost += op['skill_cd'] + 3
                touch(task['click'])  # 点击干员
                touch((1300, 600))  # 开技能
        sleep(40)  # 等待战斗结束
        while not exists('成功通过'):
            sleep(5)
            if try_touch('联系中断'):
                return True
        sleep(2)
        touch(NOP)
        sleep(1)
        touch('收下源石锭')
        sleep(.5)
        while not try_touch('不要了走了'):
            swipe_screen()
        sleep(.5)
        touch('确定-离开')
        sleep(.5)
        return False

    def excounter_chance_meeting(self):
        """ 不期而遇 """
        touch('出发前往')
        sleep(1.5)
        touch(NOP, times=2)
        sleep(1.5)
        found = False
        for img in self.option_list.values():
            if try_touch(img):
                found = True
                break
        if not found:
            touch((1800, 600))
        sleep(.5)
        touch('确定-选择')
        sleep(1)
        touch(NOP, times=15)
        self.quit_recruit()
        touch(NOP, times=15)

    def excounter_wish_fulfillment(self):
        """ 得偿所愿 """
        touch('出发前往')
        sleep(1)
        touch(NOP)
        sleep(1)
        touch('收藏品')
        sleep(.5)
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
        touch(NOP)
        sleep(1)
        touch('选择-离开')
        sleep(.5)
        touch('确定-选择')
        sleep(1)
        touch('选择-源石锭')
        sleep(1)
        touch('确定-选择')

    def excounter_regional_entrustment(self):
        """ 地区委托 """
        touch('出发前往')
        sleep(1)
        touch(NOP)
        sleep(1)
        touch('选择-离开')
        sleep(.5)
        touch('确定-选择')
        sleep(.5)
        touch(NOP, times=15)

    def rogue_trader(self):
        """  诡意行商前瞻性投资 """
        touch('出发前往')
        sleep(1)
        if try_touch('前瞻性投资系统'):
            sleep(.5)
            touch('投资入口')
            sleep(.5)
            touch((1400, 740), times=50)
            sleep(1)


def debug1():
    print(1)
    if try_touch('退出'):
        print(2)
        sleep(.5)
        touch('放弃本次探索')
        sleep(.5)
        touch('确定-放弃')
    # 结算
    air.wait(template('下一步'))
    touch('下一步')
    air.wait(template('确定-结算'))
    touch('确定-结算')
    sleep(1)
    touch(NOP)
    sleep(1)
    

def debug2():
    script = Auto_Prospective_Investment()
    script.rogue_trader()
    

def debug3():
    script = Auto_Prospective_Investment()
    found = False
    for img in script.option_list.values():
        if try_touch(img):
            found = True
            break
    if not found:
        touch((1800, 600))
    sleep(.5)
    touch('确定-选择')
    sleep(1)
    touch(NOP, times=15)
    script.quit_recruit()
    touch(NOP, times=15)


script = Auto_Prospective_Investment()
script.run()

# debug2()
# debug1()
import json
import logging
import airtest.core.api as air

# logging.getLogger("airtest").setLevel(logging.INFO)

air.auto_setup(__file__)
air.ST.FIND_TIMEOUT_TMP = 1

resolution = air.G.DEVICE.get_current_resolution()
# resolution = [1920, 1080]
''' 默认分辨率 = 1920 * 1080 '''


def trans_position(p):
    """ 数值都是根据默认分辨率设置的，修改分辨率后需要重新计算坐标 """
    return (p[0] * resolution[0] / 1920, p[1] * resolution[1] / 1080)


NOP = (700, 900)
''' 无操作 / 确定 '''


def touch(p, times=1):
    if isinstance(p, str):
        air.touch(template(p), times=times)
    elif isinstance(p, tuple):
        air.touch(trans_position(p), times=times)
    else:
        air.touch(p, times=times)


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


def template(name, threshold=None, rgb=False):
    return air.Template(r'%s' % ('images\\' + name + '.png'),
                        threshold=threshold,
                        rgb=rgb,
                        resolution=resolution)


def sleep(time):
    air.sleep(time)


def swipe_screen():
    """ 向右滑动屏幕 """
    swipe((1800, 500), (950, 500), duration=.5)
    sleep(1)


class Auto_Prospective_Investment:
    def __init__(self):
        with open('defualt_setting.json', encoding='gbk') as f:
            data = json.load(f)
            self.guard_operator_exist = data['guard_operator_exist']
            ''' 是否有核心近卫 '''
            squad = data['squad']
            ''' 编队 = [近卫, 辅助, 医疗]，近卫非空，其余无所谓（如果能过的话） '''
        operator = json.load(open('operator.json', encoding='gbk'))
        squad = [operator[name] for name in squad[:3]]
        for info in squad:
            for str in ['recruit', 'assist']:
                if str in info:
                    info[str] = template(info[str], threshold=.8)
            info['class_img'] = template('职业-' + info['class'], threshold=.3)
        squad.extend([None] * (3 - len(squad)))
        self.squad = squad

        def trans(a, prefix, rgb=False):
            return {name: template(prefix + name, rgb=rgb) for name in a}

        with open('operation_tasks.json', encoding='gbk') as f:
            self.operation_task = json.load(f)
            ''' 作战关卡操作 '''

        node_list = ['不期而遇', '地区委托', '作战', '紧急作战', '诡意行商', '兴致盎然', '得偿所愿']
        self.node_list = trans(node_list, '节点-', rgb=True)
        ''' 节点名称列表 '''

        option_list = ['离开', '希望', '源石锭', '掷骰次数', '钥匙', '问号']
        self.option_list = trans(option_list, '选择-', rgb=True)
        ''' 事件选项列表 '''

        operation_list = ['共生', '蓄水池', '虫群横行', '射手部队']
        self.operation_list = trans(operation_list, '作战-')
        ''' 关卡名称列表 '''

    def run(self):
        while (True):
            # 开始探索
            air.wait(template('探索'))
            touch((1740, 880))
            sleep(1)
            # 选择指挥分队
            touch((1540, 872))
            sleep(.6)
            touch((1540, 872))
            sleep(.6)
            # 选择取长补短
            touch((1173, 875))
            sleep(.6)
            touch((1173, 875))
            sleep(1)
            # 招募干员
            self.recruit_operators()
            # 探索海洋
            touch((1800, 540))
            # 调整编队
            self.adjust_squad()
            # 第一关
            touch((600, 500))
            self.start_operation()
            # 遍历后续节点
            while self.next_step():
                pass
            # 退出
            if try_touch('退出'):
                sleep(.5)
                touch('放弃本次探索')
                sleep(.5)
                touch('确定-放弃')
            # 结算
            air.wait(template('下一步'))
            touch('下一步')
            #             air.wait(template('确定-结算'))
            #             touch('确定-结算')
            touch(NOP, times=30)

    def quit_recruit(self):
        while try_touch('放弃'):
            sleep(.5)
            touch('确定-放弃')
            sleep(1)

    def recruit_operators(self):
        skip = (1830, 60)
        sleep_time = .6  # 网络不好调大点

        def recruit(recruit, operator, assist=False):
            touch(recruit)  # 招募券
            sleep(sleep_time)
            if operator is None:
                self.quit_recruit()
                return
            cnt = 0
            if assist:
                touch((1600, 50))  # 选择助战
                operator = operator['assist']
                while not try_touch(operator) and cnt < 7:
                    touch((1800, 50))  # 更新助战列表
                    sleep(4)
                if cnt > 7:
                    touch((140, 50))
                    sleep(.3)
                    self.quit_recruit()
                    return
                sleep(sleep_time)
                touch((1200, 770))  # 确认招募
            else:
                operator = operator['recruit']
                while not try_touch(operator) and cnt < 4:
                    swipe_screen()
                    cnt += 1
                if cnt > 3:
                    self.quit_recruit()
                    return
                sleep(sleep_time)
                touch((1800, 1000))  # 确认招募
            sleep(sleep_time)
            touch(skip)
            sleep(sleep_time)
            touch(skip)
            sleep(sleep_time / 2)

        for i in range(3):
            recruit((530 + 435 * i, 800), self.squad[i], i == 0
                    and not self.guard_operator_exist)
        return

    def adjust_squad(self):
        """ 调整编队 """
        air.wait(template('编队'))
        sleep(1)
        touch((1660, 1000))  # 编队
        sleep(.3)
        touch((1500, 60))  # 快捷编队
        sleep(.3)
        touch((800, 200))  # 近卫
        sleep(.3)
        if self.squad[0]['skill_id'] == 2:
            touch((300, 800))  # 切换2技能
            sleep(.3)
        touch((800, 400))  # 安塞尔 or 梓兰
        sleep(.3)
        touch((800, 600))  # 梓兰 or 安塞尔
        sleep(.3)
        touch((1700, 1000))  # 确认
        sleep(.3)
        touch((140, 50))  # 返回
        return

    def next_step(self):
        sleep(2)
        for name, img in self.node_list.items():
            if try_touch(img):
                sleep(.5)
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
        result = None
        for name, img in self.operation_list.items():
            if air.exists(img):
                result = name
                break
        if result is None:
            return True
        touch('出发前往')
        sleep(1)
        touch('开始行动')
        sleep(.5)
        try_touch('确定-钥匙')
        speed = template('2倍速')
        air.wait(speed)
        sleep(2)
        air.touch(speed)
        sleep(.5)
        cost = 12
        for op in self.squad:
            if op is None:
                continue
            sleep(max(0, op['cost'] - cost) / 2)
            position = air.exists(op['class_img'])
            if position is False:
                touch((110, 80))
                sleep(.5)
                touch((1100, 520))
                sleep(.5)
                return True
            task = self.operation_task[result][op['class']]
            place = trans_position(task['place'])
            air.swipe(position, place, duration=.1)  # 拖干员到位置
            dx, dy = task['direction']
            air.swipe(place, (place[0] + dx, place[1] + dy), duration=.05)  # 设置朝向
            cost += 8 - op['cost']
            if op['skill_click'] and 'click' in task:
                sleep(op['skill_cd'] / 2)
                cost += op['skill_cd'] + 3
                touch(task['click'])  # 点击干员
                touch((1300, 600))  # 开技能
        sleep(40)  # 等待战斗结束
        while not exists('成功通过'):
            sleep(5)
            if try_touch('联系中断'):
                return True
        sleep(2)
        touch(NOP)
        sleep(1)
        touch('收下源石锭')
        sleep(.5)
        while not try_touch('不要了走了'):
            swipe_screen()
        sleep(.5)
        touch('确定-离开')
        sleep(.5)
        return False

    def excounter_chance_meeting(self):
        """ 不期而遇 """
        touch('出发前往')
        sleep(1.5)
        touch(NOP, times=2)
        sleep(1.5)
        found = False
        for img in self.option_list.values():
            if try_touch(img):
                found = True
                break
        if not found:
            touch((1800, 600))
        sleep(.5)
        touch('确定-选择')
        sleep(1)
        touch(NOP, times=15)
        self.quit_recruit()
        touch(NOP, times=15)

    def excounter_wish_fulfillment(self):
        """ 得偿所愿 """
        touch('出发前往')
        sleep(1)
        touch(NOP)
        sleep(1)
        touch('收藏品')
        sleep(.5)
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
        touch(NOP)
        sleep(1)
        touch('选择-离开')
        sleep(.5)
        touch('确定-选择')
        sleep(1)
        touch('选择-源石锭')
        sleep(1)
        touch('确定-选择')

    def excounter_regional_entrustment(self):
        """ 地区委托 """
        touch('出发前往')
        sleep(1)
        touch(NOP)
        sleep(1)
        touch('选择-离开')
        sleep(.5)
        touch('确定-选择')
        sleep(.5)
        touch(NOP, times=15)

    def rogue_trader(self):
        """  诡意行商前瞻性投资 """
        touch('出发前往')
        sleep(1)
        if try_touch('前瞻性投资系统'):
            sleep(.5)
            touch('投资入口')
            sleep(.5)
            touch((1400, 740), times=50)
            sleep(1)


def debug1():
    print(1)
    if try_touch('退出'):
        print(2)
        sleep(.5)
        touch('放弃本次探索')
        sleep(.5)
        touch('确定-放弃')
    # 结算
    air.wait(template('下一步'))
    touch('下一步')
    air.wait(template('确定-结算'))
    touch('确定-结算')
    sleep(1)
    touch(NOP)
    sleep(1)


def debug2():
    script = Auto_Prospective_Investment()
    script.rogue_trader()


def debug3():
    script = Auto_Prospective_Investment()
    found = False
    for img in script.option_list.values():
        if try_touch(img):
            found = True
            break
    if not found:
        touch((1800, 600))
    sleep(.5)
    touch('确定-选择')
    sleep(1)
    touch(NOP, times=15)
    script.quit_recruit()
    touch(NOP, times=15)


script = Auto_Prospective_Investment()
script.run()

# debug2()
# debug1()
