from .ivtcard import *
from .ivtenum import *
from .ivtproperty import *
from .ivtweapon import *
from .ivtdebuff import ElementDebuffState
import numpy as np
import math
import random
import copy

CRITICAL_RNG = 0.0
TRIGGER_RNG = 0.0
HEADSHOT_RNG = 0.0

class MoveState:
    '''
    角色的行动状态
    '''
    def __init__(self):
        self.isMoving = False
        self.isInAir = False

class CardSetInfo:
    '''
    角色身上所装备的套装卡牌信息
    '''
    def __init__(self):
        self.cardSetCount = []
        for cardSet in CardSet:
            self.cardSetCount.append(0)

    def setCardSetCount(self, cardSet: CardSet, count: int):
        self.cardSetCount[cardSet.value] = count

    def getCardSetCount(self, cardSet: CardSet) -> int:
        return self.cardSetCount[cardSet.value]
    
class CharacterInfo:
    '''
    角色信息，不过目前仅启用技能强度作为属性
    '''
    def __init__(self):
        self.characterProperties = []
        for characterProperty in CharacterPropertyType:
            self.characterProperties.append(100.0)

    def setCharacterProperty(self, propertyType: CharacterPropertyType, value: float):
        self.characterProperties[propertyType.value] = value

    def getCharacterProperty(self, propertyType: CharacterPropertyType) -> float:
        return self.characterProperties[propertyType.value]

class TargetInfo:
    '''
    作为靶标的敌人信息
    '''
    def __init__(self):
        self.elementDebuffState = ElementDebuffState()
        self.material = EnemyMaterial.Void
        self.armor = 3430.0
        self.skillDebuff = {}
        self.headShotRate = 0.0
        for skillDebuff in SkillDebuff:
            self.skillDebuff[skillDebuff] = 0
    
    def addConstantElementDebuff(self, element, value: int):
        '''
        添加不会清空的元素异常状态
        '''
        if isinstance(element, DamageType):
            for _ in range(value):
                self.elementDebuffState.addDebuffByDamageType(element, 6)
        else:
            for _ in range(value):
                self.elementDebuffState.addDebuffByPropertyType(element, 6)

    def addSkillDebuff(self, skillDebuff: SkillDebuff, value: int):
        '''
        添加技能异常状态
        '''
        if skillDebuff in self.skillDebuff:
            self.skillDebuff[skillDebuff] += value
        else:
            raise ValueError(f"未知技能异常状态: {skillDebuff}")
        
    def getSkillDebuff(self, skillDebuff: SkillDebuff) -> int:
        '''
        获取技能异常状态值
        '''
        if skillDebuff in self.skillDebuff:
            return self.skillDebuff[skillDebuff]
        else:
            raise ValueError(f"未知技能异常状态: {skillDebuff}")

np_Adjustment = np.array([
	[1,		1,		1,		1], 	# Physics
	[1.25,	0.85,	1,		1], 	# Cold
	[1,		1,		0.75,	1.25], 	# Electric
	[0.85,	1.25,	1,		1], 	# Fire
	[1,		1,		1.25,	0.75],  # Poison
	[1.5,	0.5,	1,		1.5],  # Cracking
	[0.5,	1.5,	1,		1.75],  # Radiation
	[1,		1,		1.75, 0.5],  # Gas
	[1,     1.75,  0.5,   1.75],  # Magnetic
	[1.75,  1,     0.5,   1],    # Ether
	[0.5,   1,     1.5,   1]     # Virus
])

def DamageTakenByMaterial(damage : np.ndarray, enemyMaterial: EnemyMaterial):
	'''
	计算敌人受到的伤害
	:param damage: 伤害集合
	:param enemyMaterial: 敌人材质
	:return: 计算后的伤害集合
	'''
	return np.multiply(damage, np_Adjustment[:, enemyMaterial.value])

# 护甲减伤计算公式
def ArmorDamageReduction(armor: float) -> float:
    """
    计算护甲减伤
    :param armor: 护甲值
    :return: 减伤比例
    """
    return 1 - (armor / (800 + armor))

# 
def WeakArmor(armor: float, radiationCount: int = 0, fireCount: int = 0, useNianSkill = False, NianSkillStrength: float = 100) -> float:
    """
    使用辐射和热波伤害削弱护甲
    :param armor: 护甲值
    :param radiationCount: 辐射伤害数量
    :param fireCount: 热波伤害数量
    :param useNianSkill: 是否使用年春秋技能
    :param NianSkillStrength: 年春秋技能强度
    :return: 削弱后的护甲值
    """
    skillWeak = 0
    if useNianSkill:
        skillWeak = NianSkillStrength / 100.0 * 0.6     # 年春秋技能削弱护甲60%, 取决于技能强度
        skillWeak *= 100
        skillWeak = round(skillWeak) / 100.0
    fireWeak = 0.5 if fireCount > 0 else 0              # 热波伤害削弱护甲50%
    radiationWeak = 0
    if radiationCount > 0:
        radiationWeak = 0.16 + (radiationCount - 1) * 0.06    # 辐射伤害削弱护甲16%，每层叠加辐射伤害额外增加6%
        radiationWeak = min(radiationWeak, 0.7)         # 最大削弱比例为70%
    return max(armor * (1 - skillWeak) * (1 - fireWeak) * (1 - radiationWeak), 0)

def GetCriticalMultiplier(criticalChance: float, criticalDamage: float, coldDebuff: int = 0) -> tuple:
    '''
    计算暴击倍率
    :param criticalChance: 暴击几率
    :param criticalDamage: 暴击伤害
    :param coldDebuff: 冰冻异常状态层数
    :return: (未暴击伤害倍率，暴击伤害倍率）
    '''
    coldCriticalDamage = 0
    if coldDebuff > 0:
        coldCriticalDamage = 0.1 + (coldDebuff - 1) * 0.05  # 冰冻debuff增加敌人受到的暴击伤害10%，每层叠加冰冻敌人受到的暴击伤害额外增加5%
    # 如果暴击几率为0，则直接返回1.0
    if criticalChance <= 0:
        return 1, 1
    elif criticalChance <= 1.0:
        return 1.0, criticalDamage + coldCriticalDamage
    else:
        lowerCriticalLevel = int(criticalChance)
        upperCriticalLevel = lowerCriticalLevel + 1
        return lowerCriticalLevel * (criticalDamage + coldCriticalDamage), upperCriticalLevel * (criticalDamage + coldCriticalDamage)

def GetExternalDamageMultiplier(invasionAuraNum: int, reverseSetNum: int, sniperComboMulti: float = 1.0, isMoving: bool = False) -> float:
    '''
    获取外部伤害加成倍率
    :param ctx: 当前环境上下文
    :return: 外部伤害加成倍率
    '''
    if not isMoving:
        reverseSetNum = 0   # 逆转套装仅在移动时生效
    return 1 + invasionAuraNum * 0.3 + reverseSetNum * 0.3 + (sniperComboMulti - 1)  # 光环、逆转和狙击枪连击的伤害加成

def VulnerableVirusMultiplier(virusDebuff: int) -> float:
    """
    计算易伤病毒倍率
    :param ctx: 当前环境上下文
    :return: 易伤病毒倍率
    """
    if virusDebuff > 0:
        return 1.75 + 0.25 * virusDebuff  # 易伤病毒倍率为2，每层叠加病毒额外增加0.25
    return 1.0

def TriggerElementDebuff(damage : np.ndarray) -> DamageType:
    '''
    根据元素在伤害中的占比触发元素异常
    '''
    dmg = damage.copy()
    # 动能伤害不参与异常触发
    dmg[WeaponPropertyType.Physics.value] = 0.0
    totalElementDamage = dmg.sum()
    
    # 如果没有元素伤害，直接返回None
    if totalElementDamage == 0:
        return None
    
    # 提取元素伤害部分
    elementDamage = dmg[WeaponPropertyType.Cold.value:WeaponPropertyType.Virus.value + 1]
    
    # 计算概率分布并累加
    probabilities = elementDamage / totalElementDamage
    cumulative_probs = np.cumsum(probabilities)
    
    # 生成随机数并使用searchsorted快速查找
    currentRandom = random.random()
    index = np.searchsorted(cumulative_probs, currentRandom, side='right')
    
    # 转换回DamageType
    return DamageType(index + WeaponPropertyType.Cold.value)

class DPSRequest:
    '''
    发起一次DPS计算请求所需的所有信息
    包括武器基本信息、所有的卡牌、角色信息和环境信息
    '''
    def __init__(self, weapon: Weapon, cards: list[WeaponCardWithProperty]):
        self.weapon = weapon
        self.cards = cards
        self.moveState = MoveState()
        self.cardSetInfo = CardSetInfo()
        self.characterInfo = CharacterInfo()
        self.targetInfo = TargetInfo()
        self.damageOnGui = self.weapon.snapshot.getTotalDamageArray().sum() # 面板伤害
        self.firstCriticalDamage = 0.0
        self.firstUncriticalDamage = 0.0
        self.firstCriticalDamageHeadshot = 0.0
        self.firstUncriticalDamageHeadshot = 0.0
        self.magazineDps = 0
        self.magazineDamage = 0
        self.averageDps = 0
        self.finalSnapshot = None

    '''
    从一个DPSRequest创建一个新的DPSRequest
    使用深拷贝确保新请求与原请求完全独立，互不影响
    '''
    @classmethod
    def createNewOne(cls, other: 'DPSRequest') -> 'DPSRequest':
        newRequest = cls(weapon=other.weapon, cards=copy.deepcopy(other.cards))
        newRequest.moveState = other.moveState
        newRequest.cardSetInfo = other.cardSetInfo
        newRequest.characterInfo = other.characterInfo
        newRequest.targetInfo = copy.deepcopy(other.targetInfo)
        return newRequest

    def calculate(self):
        '''
        执行DPS计算
        '''
        # 先获取执行卡的所有属性加成
        allPropertiesFromCards = []
        for card in self.cards:
            if card is not None and isinstance(card, WeaponCardWithProperty):
                allPropertiesFromCards.extend(card.getProperties())
        # 将空中才生效的属性视情况合并或剔除
        if not self.moveState.isInAir:
            allPropertiesFromCards = [prop for prop in allPropertiesFromCards if not prop.propertyType.isAirProperty()]
        else:
            for prop in allPropertiesFromCards:
                prop.convertToNotAirProperty()
        # 再获取武器的所有基础属性
        allPropertiesFromWeapon = []
        baseSnapshot = self.weapon.getBaseSnapshot()
        for weaponProperty in WeaponPropertyType:
            propValue = baseSnapshot.getPropertyValue(weaponProperty)
            if propValue != 0:
                allPropertiesFromWeapon.append(WeaponProperty.createBaseProperty(weaponProperty, propValue))
        # 创建最终属性快照
        finalSnapshot = WeaponPropertySnapshot(weaponProperties=allPropertiesFromWeapon,
                                               cardProperties=allPropertiesFromCards)
        # 需要判断是否应该进行鬼卡的动能转换
        ghostCardCount = self.cardSetInfo.getCardSetCount(CardSet.Ghost)
        for card in self.cards:
            if isinstance(card, WeaponCardCommon) and card.cardSet == CardSet.Ghost:
                ghostCardCount += 1
        if ghostCardCount > 0:
            finalSnapshot.applyGhostCardConversion(ghostCardCount)
        # 获取面板伤害
        weaponDamage = finalSnapshot.getTotalDamageArray()
        self.damageOnGui = weaponDamage.sum()
        # 初始化随机数
        global CRITICAL_RNG, TRIGGER_RNG, HEADSHOT_RNG
        CRITICAL_RNG = 0.0
        TRIGGER_RNG = 0.0
        HEADSHOT_RNG = 0.0
        random.seed(0)
        # 清除元素异常
        self.targetInfo.elementDebuffState.clearDebuff()
        # 初始化造成的伤害
        damageTaken = 0.0
        # 计算实际发射的子弹数
        magazine = finalSnapshot.getPropertyValue(WeaponPropertyType.MagazineSize)
        multiStrike = finalSnapshot.getPropertyValue(WeaponPropertyType.MultiStrike)
        totalShots = int(magazine * multiStrike)
        # 计算外部伤害加成
        externalDamageMultiplier = GetExternalDamageMultiplier(
            invasionAuraNum=self.cardSetInfo.getCardSetCount(CardSet.Invasion),
            reverseSetNum=self.cardSetInfo.getCardSetCount(CardSet.Reverse),
            isMoving=self.moveState.isMoving
        )
        # 计算暴击率
        criticalChance = finalSnapshot.getPropertyValue(WeaponPropertyType.CriticalChance) / 100.0
        criticalDamage = finalSnapshot.getPropertyValue(WeaponPropertyType.CriticalDamage) / 100.0
        # 计算触发率
        triggerChance = finalSnapshot.getPropertyValue(WeaponPropertyType.TriggerChance) / 100.0
        # 计算爆头伤害加成
        headShot = finalSnapshot.getPropertyValue(WeaponPropertyType.Headshot) / 100.0
        for _ in range(totalShots):
            damageTaken += self._calculateDmageOnce(weaponDamage,
                                                    externalDamageMultiplier=externalDamageMultiplier,
                                                    criticalChance=criticalChance,
                                                    criticalDamage=criticalDamage,
                                                    triggerChance=triggerChance,
                                                    headShot=headShot,
                                                    criticalFlag=0,
                                                    triggerFlag=0,
                                                    headShotFlag=0)
        
        random.seed(0)
        self.targetInfo.elementDebuffState.clearDebuff()
        # 计算首发暴击伤害和非暴击伤害
        self.firstCriticalDamage = self._calculateDmageOnce(weaponDamage,
                                                            externalDamageMultiplier=externalDamageMultiplier,
                                                            criticalChance=criticalChance,
                                                            criticalDamage=criticalDamage,
                                                            triggerChance=triggerChance,
                                                            headShot=headShot,
                                                            criticalFlag=1,
                                                            triggerFlag=-1,
                                                            headShotFlag=-1)
        random.seed(0)
        self.targetInfo.elementDebuffState.clearDebuff()
        self.firstUncriticalDamage = self._calculateDmageOnce(weaponDamage,
                                                            externalDamageMultiplier=externalDamageMultiplier,
                                                            criticalChance=criticalChance,
                                                            criticalDamage=criticalDamage,
                                                            triggerChance=triggerChance,
                                                            criticalFlag=-1,
                                                            triggerFlag=-1,
                                                            headShotFlag=-1)
        random.seed(0)
        self.targetInfo.elementDebuffState.clearDebuff()
        self.firstCriticalDamageHeadshot = self._calculateDmageOnce(weaponDamage,
                                                            externalDamageMultiplier=externalDamageMultiplier,
                                                            criticalChance=criticalChance,
                                                            criticalDamage=criticalDamage,
                                                            triggerChance=triggerChance,
                                                            headShot=headShot,
                                                            criticalFlag=1,
                                                            triggerFlag=-1,
                                                            headShotFlag=1)
        random.seed(0)
        self.targetInfo.elementDebuffState.clearDebuff()
        self.firstUncriticalDamageHeadshot = self._calculateDmageOnce(weaponDamage,
                                                            externalDamageMultiplier=externalDamageMultiplier,
                                                            criticalChance=criticalChance,
                                                            criticalDamage=criticalDamage,
                                                            triggerChance=triggerChance,
                                                            headShot=headShot,
                                                            criticalFlag=-1,
                                                            triggerFlag=-1,
                                                            headShotFlag=1)

        # 输出结果
        self.magazineDamage = damageTaken
        attackSpeed = finalSnapshot.getPropertyValue(WeaponPropertyType.AttackSpeed)
        self.magazineDps = damageTaken * attackSpeed / magazine
        reloadTime = finalSnapshot.getPropertyValue(WeaponPropertyType.ReloadTime)
        self.averageDps = self.magazineDamage / (magazine / attackSpeed + reloadTime)
        self.finalSnapshot = finalSnapshot

    def _calculateDmageOnce(self, weaponDamage: np.ndarray, externalDamageMultiplier: float = 1.0, 
                            criticalChance: float = 0.0, criticalDamage: float = 0.0, triggerChance: float = 0.0,
                            headShot : float = 0.0, criticalFlag: int = 0, triggerFlag: int = 0, headShotFlag: int = 0) -> float:
        '''
        计算单次伤害
        :param weaponDamage: 武器伤害数组
        :param externalDamageMultiplier: 外部伤害加成倍率
        :param criticalChance: 暴击几率
        :param criticalDamage: 暴击伤害
        :param triggerChance: 触发几率
        :param headShot: 爆头伤害加成
        :param criticalFlag: 暴击标志，-1表示强行不暴击，1表示强行暴击，0表示随机判定
        :param triggerFlag: 触发标志，-1表示强行不触发，1表示强行触发，0表示随机判定
        :param headShotFlag: 爆头标志，-1表示强行不爆头，1表示强行爆头，0表示随机判定
        :return: 计算后的伤害值
        '''
        # 计算暴击倍率
        uncriticalMultiplier, criticalMultiplier = GetCriticalMultiplier(
            criticalChance=criticalChance,
            criticalDamage=criticalDamage,
            coldDebuff=self.targetInfo.elementDebuffState.getDebuffByDamageType(DamageType.Cold)
        )
        # 计算减伤
        damageAfterReduction = DamageTakenByMaterial(weaponDamage, self.targetInfo.material).sum()
        # 计算护甲减伤
        fireDebuff = self.targetInfo.elementDebuffState.getDebuffByDamageType(DamageType.Fire)
        radiationDebuff = self.targetInfo.elementDebuffState.getDebuffByDamageType(DamageType.Radiation)
        useNianSkill = self.targetInfo.getSkillDebuff(SkillDebuff.Qianyinfeidan) > 0
        realArmor = WeakArmor(
            armor=self.targetInfo.armor,
            radiationCount=radiationDebuff,
            fireCount=fireDebuff,
            useNianSkill=useNianSkill,
            NianSkillStrength=self.characterInfo.getCharacterProperty(CharacterPropertyType.SkillStrength)
        )
        armorReduction = ArmorDamageReduction(realArmor)
        damageAfterReduction *= armorReduction
        # 计算易伤病毒倍率
        vulnerableVirusMultiplier = VulnerableVirusMultiplier(
            virusDebuff=self.targetInfo.elementDebuffState.getDebuffByDamageType(DamageType.Virus)
        )
        damageAfterReduction *= vulnerableVirusMultiplier
        # 计算是否暴击
        global CRITICAL_RNG
        if criticalFlag == 1:
            damageAfterReduction *= criticalMultiplier
        elif criticalFlag == -1:
            damageAfterReduction *= uncriticalMultiplier
        else:
            CRITICAL_RNG += criticalChance
            if CRITICAL_RNG >= 1.0:
                damageAfterReduction *= criticalMultiplier
                CRITICAL_RNG = math.fmod(CRITICAL_RNG, 1.0)
            else:
                damageAfterReduction *= uncriticalMultiplier
        # 计算是否爆头
        global HEADSHOT_RNG
        if headShotFlag == 1:
            damageAfterReduction *= (1 + headShot)
        elif headShotFlag == -1:
            pass
        else:
            HEADSHOT_RNG += self.targetInfo.headShotRate
            if HEADSHOT_RNG >= 1.0:
                damageAfterReduction *= (1 + headShot)
                HEADSHOT_RNG = math.fmod(HEADSHOT_RNG, 1.0)        
        # 计算外部伤害加成
        damageAfterReduction *= externalDamageMultiplier
        # 计算触发和持续伤害
        dotDamageTaken = 0.0
        global TRIGGER_RNG
        isTrigger = False
        if triggerFlag == 1:
            isTrigger = True
        elif triggerFlag == -1:
            isTrigger = False
        else:
            TRIGGER_RNG += triggerChance
            if TRIGGER_RNG >= 1.0:
                isTrigger = True
                TRIGGER_RNG = math.fmod(TRIGGER_RNG, 1.0)
        if isTrigger:
            debuffProperty = TriggerElementDebuff(weaponDamage)
            if debuffProperty is not None and debuffProperty != DamageType.Physics:
                self.targetInfo.elementDebuffState.addDebuffByDamageType(debuffProperty, 6)
                # 如果是伤害类的Debuff，则其持续伤害总量计入到damageTaken中
                DoTMultiplier = 0.0
                if debuffProperty == DamageType.Fire or debuffProperty == DamageType.Electric or debuffProperty == DamageType.Gas:
                    # 热波、赛能、毒气元素异常的持续伤害倍率为 0.5，持续6秒
                    DoTMultiplier = 0.5
                elif debuffProperty == DamageType.Cracking:
                    # 裂化的伤害倍率为 0.35，持续6秒
                    DoTMultiplier = 0.35
                if DoTMultiplier > 0:
                    DoTDamage = weaponDamage.sum() * externalDamageMultiplier * DoTMultiplier
                    dotDamageTaken += DoTDamage * armorReduction * vulnerableVirusMultiplier
        # 返回总伤害
        return damageAfterReduction + dotDamageTaken