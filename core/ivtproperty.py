from .ivtenum import WeaponPropertyType
import numpy as np
import copy

class PropertyData:
    '''
    属性对，包含基础值和加成值
    '''
    def __init__(self):
        self.__datas = np.zeros((len(WeaponPropertyType), 2), dtype=np.float64)

    def __add__(self, other):
        self.__datas += other.__datas
        return self
    
    def getDamageArray(self) -> np.ndarray:
        '''
        获取伤害属性数组
        '''
        damage_array = np.zeros(10, dtype=np.float64)
        for i in range(10):
            damage_array[i] = self.__datas[i][0] * (1 + self.__datas[i][1] / 100)
        return damage_array
    
    def getValue(self, propertyType : WeaponPropertyType) -> float:
        '''
        获取指定类型的属性值
        '''
        idx = propertyType.value
        return self.__datas[idx][0]
    
    def getAddon(self, propertyType : WeaponPropertyType) -> float:
        '''
        获取指定类型的属性加成值
        '''
        idx = propertyType.value
        return self.__datas[idx][1]
    
    def get(self, propertyType : WeaponPropertyType) -> float:
        '''
        获取指定类型的属性总值
        '''
        idx = propertyType.value
        return self.__datas[idx][0] * (1 + self.__datas[idx][1] / 100)
    
    def setFinalValue(self, propertyType : WeaponPropertyType, finalValue : float):
        '''
        直接设置属性的最终值，计算出基础值
        仅用于百分比转化为实际数值的情况
        '''
        idx = propertyType.value
        self.__datas[idx][0] = finalValue
        self.__datas[idx][1] = 0.0

class WeaponProperty(PropertyData):
    '''
    武器属性条目    
    为了方便计算，属性以numpy数组的形式存储
    '''
    def __init__(self, propertyType : WeaponPropertyType, value: float = 0.0, addon: float = 0.0, from_mod=False):
        super().__init__()
        self.__datas[propertyType.value][0] = value
        self.__datas[propertyType.value][1] = addon
        self.propertyType = propertyType
        self.from_mod = from_mod

    def get(self) -> float:
        '''
        获取属性的总值
        '''
        return self.__datas[self.propertyType.value][0] * (1 + self.__datas[self.propertyType.value][1] / 100)
    
    def clear(self):
        '''
        清除属性值
        '''
        self.__datas[self.propertyType.value][0] = 0.0
        self.__datas[self.propertyType.value][1] = 0.0

    def getValue(self) -> float:
        '''
        获取属性的基础值
        '''
        return self.__datas[self.propertyType.value][0]
    
    def getAddon(self) -> float:
        '''
        获取属性的加成值
        '''
        return self.__datas[self.propertyType.value][1]

    def __add__(self, other):
        if self.propertyType != other.propertyType:
            raise ValueError("无法将不同类型的属性相加")
        if other.getValue() != 0.0 and self.getValue() != 0.0:
            raise ValueError("属性不能同时拥有基础值和加成")
        self.__datas[self.propertyType.value][0] += other.getValue()
        self.__datas[self.propertyType.value][1] += other.getAddon()
        return self
    
    def switchPropertyType(self, newPropertyType : WeaponPropertyType):
        '''
        切换属性类型
        '''
        self.propertyType = newPropertyType
    
    @classmethod
    def createModProperty(cls, propertyType : WeaponPropertyType, addon: float):
        '''
        创建一个仅有加成的属性条目
        '''
        return cls(propertyType, 0.0, addon, from_mod=True)
    
    def __str__(self):
        addon = self.getAddon()
        if self.from_mod:
            if addon > 0:
                return f"{self.propertyType}: +{addon}%（来自执行卡）"
            else:
                return f"{self.propertyType}: {addon}%（来自执行卡）"
        else:
            return f"{self.propertyType}: {self.get()}"
        
    def setFinalValue(self, finalValue):
        return super().setFinalValue(self.propertyType, finalValue)
        
class WeaponPropertySnapshot:
    '''
    武器属性条目集合
    '''
    def __init__(self, properties : list[WeaponProperty] = [], update_now=True):
        self.__basePropertyData = PropertyData()
        for prop in properties:
            self.__basePropertyData += prop
        self.__finalPropertyData = None
        if update_now:
            self.update([])

    def getBaseTotalDamageArray(self) -> np.ndarray:
        '''
        获取来自武器本身的伤害属性数组
        '''
        return self.__basePropertyData.getDamageArray()
    
    def getTotalDamageArray(self) -> np.ndarray:
        '''
        获取最终的伤害属性数组
        '''
        if self.__finalPropertyData is None:
            return self.__basePropertyData.getDamageArray()
        return self.__finalPropertyData.getDamageArray()

    def getPropertyValue(self, propertyType : WeaponPropertyType) -> float:
        '''
        获取指定类型的属性值
        '''
        return self.__basePropertyData.get(propertyType)
        
    def update(self, propertyArray : list[WeaponProperty]):
        '''
        更新属性快照
        '''
        self.__finalPropertyData = copy.deepcopy(self.__basePropertyData)
        baseDamageArray = self.getBaseTotalDamageArray()
        baseDamage = np.sum(baseDamageArray)
        # 先计算非元素伤害的属性        
        variableElementDamageArray = []
        constantElementDamageArray = []
        for weaponProperty in propertyArray:
            if weaponProperty.propertyType.isElementDamage():
                if weaponProperty.propertyType.isBaseElementDamage():
                    variableElementDamageArray.append(weaponProperty)
                else:
                    constantElementDamageArray.append(weaponProperty)
            else:
                self.__basePropertyData += weaponProperty
        # 将元素伤害类词条从百分比转化为实际的伤害数值
        for weaponProperty in variableElementDamageArray:
            finalValue = weaponProperty.addon * baseDamage / 100.0
            weaponProperty.setFinalValue(finalValue)
        for weaponProperty in constantElementDamageArray:
            finalValue = weaponProperty.addon
            weaponProperty.setFinalValue(finalValue)
        # 将枪械本身的元素伤害属性添加到variableElementDamageArray末尾，然后清空快照中所有元素伤害属性
        for propertyTypeValue in range(10):
            propertyType = WeaponPropertyType(propertyTypeValue)
            if self.__basePropertyData.get(propertyType) != 0:
                value = self.__basePropertyData.getValue(propertyType)
                addon = self.__basePropertyData.getAddon(propertyType)
                weaponBaseDamageProperty = WeaponProperty(propertyType, value, addon)
                variableElementDamageArray.append(weaponBaseDamageProperty)
                self.__basePropertyData.setFinalValue(propertyType, 0.0)
        # 按照顺序开始复合元素伤害
        # 裂化 = 热波 + 冰冻
        # 辐射 = 赛能 + 创生
        # 以太 = 热波 + 赛能
        # 病毒 = 冰冻 + 创生
        # 磁暴 = 赛能 + 冰冻
        # 毒气 = 创生 + 热波
        # 如果一种基本元素加成多次出现，且之前出现的已经参与了伤害复合，那么后出现的加成会自动加入到前面的复合伤害当中
        FinalDamageArray = []
        def _findElementDamage(propertyType: WeaponPropertyType) -> WeaponProperty | None:
            for weaponProperty in FinalDamageArray:
                if weaponProperty.propertyType == propertyType:
                    return True, property
            return False, None
        
        def _findElementDamageComposed(propertyType: WeaponPropertyType):
            property = None
            find = False
            if propertyType == WeaponPropertyType.Fire:
                find, property = _findElementDamage(WeaponPropertyType.Cracking)
                if not find:
                    find, property = _findElementDamage(WeaponPropertyType.Gas)
                    if not find:
                        find, property = _findElementDamage(WeaponPropertyType.Ether)
            elif propertyType == WeaponPropertyType.Cold:
                find, property = _findElementDamage(WeaponPropertyType.Cracking)
                if not find:
                    find, property = _findElementDamage(WeaponPropertyType.Magnetic)
                    if not find:
                        find, property = _findElementDamage(WeaponPropertyType.Virus)
            elif propertyType == WeaponPropertyType.Electric:
                find, property = _findElementDamage(WeaponPropertyType.Radiation)
                if not find:
                    find, property = _findElementDamage(WeaponPropertyType.Magnetic)
                    if not find:
                        find, property = _findElementDamage(WeaponPropertyType.Ether)
            elif propertyType == WeaponPropertyType.Poison:
                find, property = _findElementDamage(WeaponPropertyType.Virus)
                if not find:
                    find, property = _findElementDamage(WeaponPropertyType.Gas)
                    if not find:
                        find, property = _findElementDamage(WeaponPropertyType.Radiation)
            return find, property
        
        for weaponProperty in variableElementDamageArray:
            damageType = weaponProperty.propertyType
            damageValue = weaponProperty.getValue()
            # 先检查是否有同类型的元素伤害已经存在
            find, existingProperty = _findElementDamage(damageType)
            if find:
                # 如果有，直接添加到已有的元素伤害上
                existingProperty += weaponProperty
                continue
            # 如果没有，检查是否有该元素参与的复合元素伤害已经存在
            find, existingProperty = _findElementDamageComposed(damageType)
            if find:
                # 如果有，将当前元素伤害加到已有的复合元素伤害上
                existingProperty += weaponProperty
                continue
            # 如果都没有，则检查是否有可复合的元素伤害存在
            if damageType == WeaponPropertyType.Fire:
                find, property = _findElementDamage(WeaponPropertyType.Cold)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Cracking)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Electric)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Ether)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Poison)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Gas)
                    continue
            elif damageType == WeaponPropertyType.Cold:
                find, property = _findElementDamage(WeaponPropertyType.Fire)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Cracking)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Electric)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Magnetic)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Poison)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Virus)
                    continue
            elif damageType == WeaponPropertyType.Electric:
                find, property = _findElementDamage(WeaponPropertyType.Fire)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Ether)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Cold)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Magnetic)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Poison)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Radiation)
                    continue
            elif damageType == WeaponPropertyType.Poison:
                find, property = _findElementDamage(WeaponPropertyType.Fire)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Gas)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Cold)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Virus)
                    continue
                find, property = _findElementDamage(WeaponPropertyType.Electric)
                if find:
                    currentValue = weaponProperty.getValue()
                    weaponProperty.setFinalValue(currentValue + damageValue)
                    weaponProperty.switchPropertyType(WeaponPropertyType.Radiation)
                    continue
            # 如果都没有，则作为新的元素伤害加入最终伤害数组
            FinalDamageArray.append(weaponProperty)

        # 那些不参与复合的元素伤害直接加入最终伤害数组
        for weaponProperty in constantElementDamageArray:
            FinalDamageArray.append(weaponProperty)

        # 计算动能伤害
        physicalAddon = self.__finalPropertyData.getAddon(WeaponPropertyType.PhysicalDamage)
        if physicalAddon != 0.0:
            finalPhysicalDamage = baseDamage * physicalAddon / 100.0
            self.__finalPropertyData.setFinalValue(WeaponPropertyType.PhysicalDamage, finalPhysicalDamage)

        # 将最终的元素伤害加入快照
        for weaponProperty in FinalDamageArray:
            self.__finalPropertyData += weaponProperty

        # 最后将对所有伤害进行AllDamage的加成
        allDamageAddon = self.__finalPropertyData.getAddon(WeaponPropertyType.AllDamage)
        for propertyTypeValue in range(10):
            propertyType = WeaponPropertyType(propertyTypeValue)
            baseValue = self.__finalPropertyData.getValue(propertyType)
            if baseValue != 0.0:
                finalValue = baseValue * (1 + allDamageAddon / 100.0)
                self.__finalPropertyData.setFinalValue(propertyType, finalValue)


    def update_ghost(self):
        '''
        更新属性快照（幽灵版，仅更新基础属性，不计算元素伤害复合）
        '''
        self.__finalPropertyData = copy.deepcopy(self.__basePropertyData)