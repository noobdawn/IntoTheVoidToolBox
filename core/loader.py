import json
import os
from .ivtcard import WeaponCardCommon, WeaponCardRiven, WeaponCardSpecial
from .ivtenum import WeaponPropertyType, WeaponType, SubWeaponType, CardSet, Slot, SubWeaponTypeToMagazine
from .ivtproperty import WeaponProperty
from .ivtweapon import Weapon

COMMON_CARD_JSON_PATH = 'data/cards.json'
RIVEN_CARD_JSON_PATH = 'data/rivens.json'
SPECIAL_CARD_JSON_PATH = 'data/specials.json'
WEAPON_JSON_PATH = 'data/weapons.json'

ALL_CARDS = None
ALL_WEAPONS = None

def load_cards():
    global ALL_CARDS
    if ALL_CARDS is None:
        ALL_CARDS = _load_common_cards() + _load_riven_cards() + _load_special_cards()
    return ALL_CARDS

def _load_common_cards():
    try:
        with open(COMMON_CARD_JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"载入普通执行卡失败: {e}")
        return []

    common_cards = []
    for cardData in data:
        # 解析属性
        properties = []
        for propData in cardData.get('properties', []):
            try:
                propertyType = WeaponPropertyType[propData['type']]
                propertyValue = propData['value']
                properties.append(WeaponProperty.createModProperty(propertyType, propertyValue))
            except (KeyError, ValueError) as e:
                print(f"警告: 在卡牌 '{cardData['name']}' 中遇到未知的属性类型 '{propData.get('type')}'。已跳过。")
                continue

        # 解析武器类型
        try:
            weaponType = WeaponType.fromString(cardData.get('mainWeapon', 'All'))
        except KeyError as e:
            weaponType = WeaponType.All
        try:
            subWeaponType = SubWeaponType.fromString(cardData.get('subWeapon', 'All'))
        except KeyError as e:
            subWeaponType = SubWeaponType.All

        # 解析卡牌套装
        cardSetStr = cardData.get('cardSet')
        cardSet = CardSet[cardSetStr] if cardSetStr and cardSetStr in CardSet.__members__ else CardSet.Unset

        # 解析极性
        slotValue = cardData.get('slot', 0)
        slot = Slot(slotValue)

        card = WeaponCardCommon(
            name=cardData['name'],
            properties=properties,
            weaponType=weaponType,
            subWeaponType=subWeaponType,
            cardSet=cardSet,
            slot=slot,
            cost=cardData.get('cost', 0),
            isPrime=cardData.get('isPrime', False)
        )
        common_cards.append(card)
    return common_cards

def _load_riven_cards():
    try:
        with open(RIVEN_CARD_JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"载入裂隙执行卡失败: {e}")
        return []

    riven_cards = []
    for cardData in data:
        # 解析属性
        properties = []
        for propData in cardData.get('properties', []):
            try:
                propertyType = WeaponPropertyType[propData['type']]
                propertyValue = propData['value']
                properties.append(WeaponProperty.createModProperty(propertyType, propertyValue))
            except (KeyError, ValueError) as e:
                print(f"警告: 在裂隙卡牌 '{cardData['name']}' 中遇到未知的属性类型 '{propData.get('type')}'。已跳过。")
                continue

        # 解析极性
        slotValue = cardData.get('slot', 0)
        slot = Slot(slotValue)

        # 解析武器名称
        weaponName = cardData.get('weaponName')
        if not weaponName:
            print(f"警告: 裂隙卡牌缺少武器名称。已跳过。")
            continue

        card = WeaponCardRiven(
            name=cardData['name'],
            properties=properties,
            weaponName=weaponName,
            slot=slot,
            cost=cardData.get('cost', 0)
        )
        riven_cards.append(card)
    return riven_cards

def _load_special_cards():
    try:
        with open(SPECIAL_CARD_JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"载入专属执行卡失败: {e}")
        return []

    special_cards = []
    for cardData in data:
        # 解析极性
        slotValue = cardData.get('slot', 0)
        slot = Slot(slotValue)

        card = WeaponCardSpecial(
            name=cardData['name'],
            weaponName=cardData['weaponName'],
            slot=slot,
            cost=cardData.get('cost', 0)
        )
        special_cards.append(card)
    return special_cards

def load_weapons():
    global ALL_WEAPONS
    if ALL_WEAPONS is None:
        ALL_WEAPONS = _load_weapon_data()
    return ALL_WEAPONS

def _load_weapon_data():
    try:
        with open(WEAPON_JSON_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"载入武器数据失败: {e}")
        return []

    from .ivtweapon import Weapon
    from .ivtproperty import WeaponPropertySnapshot

    weapons = []
    for weaponData in data:
        try:
            weaponType = WeaponType.fromString(weaponData.get('weaponType', 'All'))
        except KeyError as e:
            weaponType = WeaponType.All
        try:
            subWeaponType = SubWeaponType.fromString(weaponData.get('subWeaponType', 'All'))
        except KeyError as e:
            subWeaponType = SubWeaponType.All

        name = weaponData['name']
        basename = weaponData['basename']

        # 解析属性
        # 对于弱点伤害属性需要特殊处理，确保每把武器都有该属性
        properties = []
        bSetHeadshot = False
        for propData in weaponData.get('properties', []):
            try:
                propertyType = WeaponPropertyType[propData['type']]
                propertyValue = propData['value']
                if propertyType == WeaponPropertyType.Headshot:
                    properties.append(WeaponProperty.createBasePropertyWithAddon(propertyType, 100.0, propertyValue))
                    bSetHeadshot = True
                else:
                    properties.append(WeaponProperty.createBaseProperty(propertyType, propertyValue))
            except (KeyError, ValueError) as e:
                print(f"警告: 在武器 '{name}' 中遇到未知的属性类型 '{propData.get('type')}'。已跳过。")
                continue
        if not bSetHeadshot:
            properties.append(WeaponProperty.createBasePropertyWithAddon(WeaponPropertyType.Headshot, 100.0, 0.0))


        weapon = Weapon(
            name=name,
            basename=basename,
            weaponType=weaponType,
            subWeaponType=subWeaponType,
            snapshot=WeaponPropertySnapshot(properties, [])
        )
        weapons.append(weapon)
    return weapons

def save_weapon(weapon : Weapon) -> bool:
    weaponData = {
        'name': weapon.name,
        'basename': weapon.basename,
        'weaponType': weapon.weaponType.name,
        'subWeaponType': weapon.subWeaponType.name,
        'properties': [{'type': prop.propertyType.name, 'value': prop.baseValue} for prop in weapon.snapshot.getBasePropertiesRef()]
    }

    allWeapons = []
    # 1. 读取现有数据
    if os.path.exists(WEAPON_JSON_PATH):
        try:
            with open(WEAPON_JSON_PATH, 'r', encoding='utf-8') as file:
                content = file.read()
                if content:
                    allWeapons = json.loads(content)
                if not isinstance(allWeapons, list):
                    return False
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"读取现有武器数据失败: {e}")
            return False
    # 2. 添加新武器
    allWeapons.append(weaponData)
    # 3. 写回文件   
    try:
        with open(WEAPON_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(allWeapons, file, ensure_ascii=False, indent=4)

        # 4. 更新全局缓存
        global ALL_WEAPONS
        ALL_WEAPONS = allWeapons
        return True
    except IOError as e:
        print(f"保存武器数据失败: {e}")
        return False

def save_riven_card(card : WeaponCardRiven) -> bool:
    cardData = {
        'name': card.name,
        'properties': [{'type': prop.propertyType.name, 'value': prop.getAddon()} for prop in card.getPropertiesRef()],
        'cost': card.cost,
        'slot': card.slot.value,
        'weaponName': card.weaponName
    }

    allRivenCards = []
    # 1. 读取现有数据
    if os.path.exists(RIVEN_CARD_JSON_PATH):
        try:
            with open(RIVEN_CARD_JSON_PATH, 'r', encoding='utf-8') as file:
                content = file.read()
                if content:
                    allRivenCards = json.loads(content)
                if not isinstance(allRivenCards, list):
                    return False
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"读取现有混淆执行卡数据失败: {e}")
            return False
    # 2. 添加新卡
    allRivenCards.append(cardData)
    # 3. 写回文件   
    try:
        with open(RIVEN_CARD_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(allRivenCards, file, ensure_ascii=False, indent=4)

        # 4. 更新全局缓存
        global ALL_CARDS
        ALL_CARDS = allRivenCards
        return True
    except IOError as e:
        print(f"保存混淆执行卡数据失败: {e}")
        return False
    
def delete_riven_card(card: WeaponCardRiven) -> bool:
    '''
    删除混淆执行卡
    '''
    allRivenCards = []
    # 1. 读取现有数据
    if os.path.exists(RIVEN_CARD_JSON_PATH):
        try:
            with open(RIVEN_CARD_JSON_PATH, 'r', encoding='utf-8') as file:
                content = file.read()
                if content:
                    allRivenCards = json.loads(content)
                if not isinstance(allRivenCards, list):
                    return False
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"读取现有混淆执行卡数据失败: {e}")
            return False
    # 2. 删除指定卡
    allRivenCards = [cardData for cardData in allRivenCards if cardData.get('name') != card.name or cardData.get('weaponName') != card.weaponName]
    # 3. 写回文件
    try:
        with open(RIVEN_CARD_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(allRivenCards, file, ensure_ascii=False, indent=4)
        # 4. 更新全局缓存
        global ALL_CARDS
        ALL_CARDS = allRivenCards
        return True
    except IOError as e:
        print(f"保存混淆执行卡数据失败: {e}")
        return False
    
class Config:
    '''
    全局配置类，保存应用配置
    '''
    def __init__(self):
        self.uiScale = 1.0  # 界面缩放比例
        self.subWeaponTypeMagazine = SubWeaponTypeToMagazine.copy()

CONFIG_INI_PATH = 'data/config.ini'
CONFIG = Config()

def load_config():
    global CONFIG
    if not os.path.exists(CONFIG_INI_PATH):
        save_config(CONFIG)
        return CONFIG
    try:
        with open(CONFIG_INI_PATH, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                kv = line.strip().split('=')
                if len(kv) != 2:
                    continue
                key = kv[0].strip()
                value = kv[1].strip()
                if key == 'uiScale':
                    CONFIG.uiScale = float(value)
                if key.startswith('subWeaponTypeMagazine_'):
                    subWeaponTypeStr = key[len('subWeaponTypeMagazine_'):]
                    try:
                        subWeaponType = SubWeaponType[subWeaponTypeStr]
                        CONFIG.subWeaponTypeMagazine[subWeaponType] = int(value)
                    except KeyError:
                        continue
    except (FileNotFoundError, ValueError) as e:
        print(f"加载配置失败: {e}")
    return CONFIG

def save_config(config : Config):
    '''
    保存配置
    '''
    try:
        with open(CONFIG_INI_PATH, 'w', encoding='utf-8') as file:
            file.write(f"uiScale={config.uiScale}\n")
            for subWeaponType, magazine in config.subWeaponTypeMagazine.items():
                file.write(f"subWeaponTypeMagazine_{subWeaponType.name}={magazine}\n")
        return True
    except IOError as e:
        print(f"保存配置失败: {e}")
        return False