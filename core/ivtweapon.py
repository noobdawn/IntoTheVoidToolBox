from .ivtenum import *
from .ivtproperty import WeaponPropertySnapshot
import copy

class Weapon:
    '''
    武器类，记叙了武器的类别、名称、基础属性等信息
    '''
    def __init__(self, name: str, basename: str, weaponType: WeaponType, subWeaponType: SubWeaponType, snapshot: WeaponPropertySnapshot):
        self.name = name
        self.basename = basename
        self.weaponType = weaponType
        self.subWeaponType = subWeaponType
        self.snapshot = snapshot

    def getBaseSnapshot(self) -> WeaponPropertySnapshot:
        '''
        获取武器的基础属性快照
        '''
        return copy.deepcopy(self.snapshot)