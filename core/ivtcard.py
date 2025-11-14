from .ivtenum import *
from .ivtproperty import WeaponProperty
import copy

class WeaponCardBase:
    '''
    执行卡的基础类
    '''
    def __init__(self):
        self.name = ""
        self.cost = 0
        self.slot = Slot.Jia

class WeaponCardExclusive(WeaponCardBase):
    '''
    独占类武器执行卡，只能根据名字装备在特定的武器上
    混淆武器执行卡和武器专属执行卡都属于这类
    '''
    def __init__(self, name: str, weaponName : str, slot : Slot, cost : int):
        super().__init__()
        self.name = name
        self.weaponName = weaponName
        self.slot = slot
        self.cost = cost

class WeaponCardWithProperty(WeaponCardBase):
    '''
    带属性条目的武器执行卡，普通执行卡和混淆执行卡都属于这类
    '''
    def __init__(self):
        pass

    def getPropertiesRef(self) -> list[WeaponProperty]:
        '''
        返回这张执行卡的属性
        '''
        return self.properties

    def getProperties(self) -> list[WeaponProperty]:  
        '''
        返回这张执行卡的属性的深拷贝
        '''
        return copy.deepcopy(self.properties)

class WeaponCardCommon(WeaponCardWithProperty):
    '''
    最常见的武器执行卡类型，普通武器执行卡
    '''
    def __init__(self, name: str, properties : list[WeaponProperty], weaponType : WeaponType, subWeaponType : SubWeaponType, cardSet : CardSet, slot : Slot, cost : int, isPrime : bool):
        self.name = name
        self.weaponType = weaponType
        self.subWeaponType = subWeaponType
        self.cardSet = cardSet
        self.slot = slot
        self.cost = cost
        self.properties = properties
        self.isPrime = isPrime


class WeaponCardRiven(WeaponCardWithProperty, WeaponCardExclusive):
    '''
    混淆武器执行卡
    '''
    def __init__(self, name: str, properties : list[WeaponProperty], weaponName : str, slot : Slot, cost : int):
        self.name = name
        self.weaponName = weaponName
        self.slot = slot
        self.cost = cost
        self.properties = properties

class WeaponCardSpecial(WeaponCardExclusive):
    '''
    武器专属执行卡
    '''
    def __init__(self, name: str, weaponName : str, slot : Slot, cost : int):
        super().__init__(name, weaponName, slot, cost)

def calculateRivenPropertyRange(propertyType: WeaponPropertyType, weaponType: WeaponType, rivenRange: WeaponRivenRange) -> tuple[float, float]:
    '''
    计算混淆执行卡的数值范围
    '''
    if propertyType not in RivenRangeDict or weaponType not in RivenRangeDict[propertyType]:
        raise ValueError(f"无法为属性类型 {propertyType} 和武器类型 {weaponType} 计算混淆执行卡属性范围。")
    
    baseValue = RivenRangeDict[propertyType][weaponType]
    if baseValue == 0:
        return (0, 0)
    
    baseValue *= WeaponRivenRangeParams[rivenRange]

    if baseValue < 0:
        return baseValue, 0
    else:
        return 0, baseValue