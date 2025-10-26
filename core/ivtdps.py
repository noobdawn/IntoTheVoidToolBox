from .ivtcard import *
from .ivtenum import *
from .ivtproperty import *
from .ivtweapon import *
from .ivtdebuff import ElementDebuffState

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
        for skillDebuff in SkillDebuff:
            self.skillDebuff[skillDebuff] = 0
    
    def addConstantElementDebuff(self, element, value: int):
        '''
        添加不会清空的元素异常状态
        '''
        if isinstance(element, DamageType):
            self.elementDebuffState.addDebuffByDamageType(element, value)
        else:
            self.elementDebuffState.addDebuffByPropertyType(element, value)

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
        