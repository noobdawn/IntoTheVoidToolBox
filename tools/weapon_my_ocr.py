import sys
import os
import time
import io
from PIL import Image, ImageGrab
import numpy as np

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import easyocr
import json
from core.loader import save_weapon
from core.ivtweapon import Weapon
from core.ivtenum import WeaponPropertyType, WeaponType, SubWeaponType, CardSet, Slot, WeaponPropertyTypeToString
from core.ivtproperty import WeaponProperty

reader = easyocr.Reader(['ch_sim', 'en'])
last_weapon_ocr_name = None
current_properties = {}
json_object = {}
weapon_json_filepath = "D:\\Github\\IntoTheVoidToolBox\\data\\weapons.json"

def get_clipboard_image():
    """从剪贴板获取图片"""
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            return image
        return None
    except Exception as e:
        print(f"获取剪贴板图片时出错: {e}")
        return None
    
def clear_clipboard():
    """清空剪贴板"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
        print("剪贴板已清空")
    except ImportError:
        # 如果没有win32clipboard，使用另一种方法
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.update()
            root.destroy()
            print("剪贴板已清空")
        except Exception as e:
            print(f"清空剪贴板时出错: {e}")

clear_clipboard()

while True:
    import time
    time.sleep(1)
    image = get_clipboard_image()
    if image is not None:
        img_array = np.array(image)
        results = reader.readtext(img_array)

        if results:
            weapon_ocr_name = results[0][1]

            if weapon_ocr_name != last_weapon_ocr_name and last_weapon_ocr_name is not None:
                # 立刻将当前武器保存
                json_object["name"] = last_weapon_ocr_name
                if " " in last_weapon_ocr_name:
                    basename = last_weapon_ocr_name.split(' ')[1]
                else:
                    basename = last_weapon_ocr_name
                json_object["basename"] = basename
                json_object["weaponType"] = "TODO_weaponType"
                json_object["subWeaponType"] = "TODO_subWeaponType"
                if "私法" in last_weapon_ocr_name:
                    json_object["isPrime"] = True
                else:
                    json_object["isPrime"] = False
                json_object["properties"] = []
                for prop_type, value in current_properties.items():
                    prop_dict = {
                        "type": prop_type.name,
                        "value": value
                    }
                    json_object["properties"].append(prop_dict)

                # 打开json，读取已有数据
                try:
                    with open(weapon_json_filepath, 'r', encoding='utf-8') as f:
                        weapons_data = json.load(f)
                except FileNotFoundError:
                    raise Exception("未找到武器数据文件 weapons.json")
                
                # weapons_data是一个list，检查是否已有该武器
                weapon_exists = False
                for weapon in weapons_data:
                    if weapon["name"] == json_object["name"]:
                        weapon_exists = True
                        break
                if not weapon_exists:
                    weapons_data.append(json_object)
                    with open(weapon_json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(weapons_data, f, ensure_ascii=False, indent=4)
                    print(f"已保存武器: {json_object['name']}")
                    
                current_properties = {}
                json_object = {}
            
            last_weapon_ocr_name = weapon_ocr_name

            for res in results:
                text = res[1]
                for prop_type in WeaponPropertyType:
                    if prop_type == WeaponPropertyType.AllDamage:
                        continue
                    prop_str = WeaponPropertyTypeToString.get(prop_type, "")
                    if prop_str in text or (prop_type == WeaponPropertyType.MultiStrike and "射击" in text):
                        value_index = results.index(res) + 1
                        # 如果置信小于0.2，则再+1
                        if value_index < len(results) and (results[value_index][2] < 0.2 or '十' in results[value_index][1]):
                            value_index += 1
                        if value_index < len(results):
                            value_text = results[value_index][1]
                            try:
                                if prop_type in [WeaponPropertyType.TriggerChance, WeaponPropertyType.CriticalChance, WeaponPropertyType.CriticalDamage, WeaponPropertyType.Headshot, WeaponPropertyType.DebuffDuration, WeaponPropertyType.ReloadTime]:
                                    value = float(value_text[:-1])
                                else:
                                    value = float(value_text)
                                current_properties[prop_type] = value
                            except ValueError:
                                print(f"无法将属性值转换为数字: {value_text}")
                                # 触发windows警告声
                                import winsound
                                winsound.MessageBeep()


        clear_clipboard()

            


                                