from .ivtenum import DamageType, WeaponPropertyType

class ElementDebuff:
    '''
    元素异常状态
    '''
    def __init__(self, duration):
        self.duration = duration
        self.time = 0

class ElementDebuffQueue:
    '''
    单个元素异常的队列
    每次新增元素异常，若超过上限，则移除最早的一个
    '''
    def __init__(self, maxCount=-1, constantCount=0):
        '''
        maxCount: 最大数量，-1表示无限制
        constantCount: 常驻数量，不会被移除
        '''
        self.queue = []
        self.maxCount = maxCount
        self.constantCount = constantCount

    def getCount(self):
        '''
        获取当前元素异常的数量，为常驻数量加上队列中数量
        '''
        return min(len(self.queue) + self.constantCount, self.maxCount)

    def addDebuff(self, debuff: ElementDebuff):
        '''
        触发一次元素异常
        '''
        if self.maxCount < 0 or self.getCount() < self.maxCount:
            self.queue.append(debuff)
        else:
            self.queue.pop(0)
            self.queue.append(debuff)

    def tick(self, deltaTime):
        '''
        时间流逝
        '''
        removeList = []
        for debuff in self.queue:
            debuff.time += deltaTime
            if debuff.time >= debuff.duration:
                removeList.append(debuff)
        for debuff in removeList:
            self.queue.remove(debuff)

    def setConstantCount(self, count):
        '''
        设置常驻数量
        '''
        self.constantCount = count if self.maxCount < 0 else min(count, self.maxCount)

class ElementDebuffState:
    '''
    敌人身上所有元素异常状态的集合
    '''
    def __init__(self):
        self.elementDebuff = [
            None, # 动能伤害不造成异常
            ElementDebuffQueue(9), # 冰冻异常最高9层
            ElementDebuffQueue(), # 赛能
            ElementDebuffQueue(), # 热波
            ElementDebuffQueue(), # 创生
            ElementDebuffQueue(), # 裂化
            ElementDebuffQueue(10), # 辐射
            ElementDebuffQueue(), # 毒气
            ElementDebuffQueue(10), # 磁暴
            ElementDebuffQueue(10), # 以太
            ElementDebuffQueue(10), # 病毒
        ]

    def setConstantDebuffByDamageType(self, damageType: DamageType, count):
        '''
        设置常驻元素异常数量
        '''
        if damageType == DamageType.Physical:
            return
        self.elementDebuff[damageType.value].setConstantCount(count)

    def setConstantDebuffByPropertyType(self, propertyType: WeaponPropertyType, count):
        '''
        设置常驻元素异常数量
        '''
        damageType = propertyType.toDamageType()
        self.setConstantDebuffByDamageType(damageType, count)

    def clearDebuff(self):
        '''
        清除所有元素异常
        '''
        for debuffQueue in self.elementDebuff:
            if debuffQueue is not None:
                debuffQueue.queue.clear()

    def clearAllDebuff(self):
        '''
        清除所有元素异常，包括常驻数量
        '''
        for debuffQueue in self.elementDebuff:
            if debuffQueue is not None:
                debuffQueue.queue.clear()
                debuffQueue.constantCount = 0

    def addDebuffByDamageType(self, damageType: DamageType, duration):
        '''
        触发一次元素异常
        '''
        if damageType == DamageType.Physical:
            return
        debuff = ElementDebuff(duration)
        self.elementDebuff[damageType.value].addDebuff(debuff)

    def addDebuffByPropertyType(self, propertyType: WeaponPropertyType, duration):
        '''
        触发一次元素异常
        '''
        damageType = propertyType.toDamageType()
        self.addDebuffByDamageType(damageType, duration)