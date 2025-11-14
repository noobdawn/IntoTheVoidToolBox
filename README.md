# IntoTheVoidToolBox：《驱入虚空》工具箱

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

[English](README_en.md) | [中文](README.md)

## 📖 概述

欢迎使用《驱入虚空》工具箱！

本工具旨在提供《驱入虚空（Into the Void）》游戏外的功能支持，目前本工具箱提供基础的武器执行卡配装功能，日后可能会提供其他功能，例如人物执行卡配装等。

**免责声明**：本工具为个人开发，与《驱入虚空》开发商杭州紧张树科技有限公司没有任何联系。

## ✨ 功能页简介

### 🔫 武器执行卡配装

在此处安装和卸载执行卡，尝试不同的执行卡搭配，选择不同的伤害计算方式以查看执行卡的提升幅度。

### 💎 自制混淆执行卡编辑器

可录入自定义的混淆执行卡，帮助计算执行卡收益。

## 🎯 使用方法

1. **添加自定义混淆执行卡**
   - 进入"自制混淆执行卡"页面
   - 填写卡牌名称、选择武器类型、词缀数量和极性
   - 添加属性并设置数值
   - 点击保存按钮

2. **配置武器构建**
   - 进入"武器配卡"页面
   - 从下拉菜单中选择目标武器，或输入文本以自动补全
   - 设置靶标类型、护甲等级等环境参数
   - 配置角色增益效果（如技能增伤等）

3. **选择执行卡**
   - 在下方的执行卡列表中浏览可用的执行卡
   - 查看每张卡在当前配装下的增幅效果
   - 点击空白执行卡槽位后，选择执行卡即可装配
   - 右键点击已装配的执行卡可以卸下

4. **查看伤害分析**
   - 选择不同的 DPS 统计方法进行比较

## 📚 依赖

本项目依赖以下主要库：

- **PyQt5**：跨平台 GUI 框架
- **PyQt-Fluent-Widgets**：Fluent Design 风格的 UI 组件库
- **pynput**：键盘和鼠标输入监听
- **numpy**：高性能数值计算库

详细依赖列表请参见 [requirements.txt](requirements.txt)。

## 🛠️ 开发说明

### 项目结构

```
IntoTheVoidToolBox/
├── assets/              # 资源文件
│   ├── images/          # 轮播图图片
│   ├── splash/          # 启动画面
│   └── ui/              # UI 素材
├── core/                # 核心业务逻辑
│   ├── ivtcard.py       # 执行卡数据结构
│   ├── ivtcontext.py    # 全局上下文管理
│   ├── ivtdps.py        # 伤害计算引擎
│   ├── ivtenum.py       # 枚举类型定义
│   ├── ivtproperty.py   # 属性系统
│   ├── ivtweapon.py     # 武器系统
│   └── loader.py        # 数据加载器
├── data/                # 数据文件
│   ├── cards.json       # 执行卡数据
│   ├── rivens.json      # 混淆执行卡数据
│   ├── specials.json    # 特殊执行卡数据
│   └── weapons.json     # 武器数据
├── tools/               # 工具脚本
│   └── weapon_my_ocr.py # OCR 识别工具
├── ui/                  # 用户界面
│   ├── components/      # UI 组件
│   ├── edit_riven_page.py    # 混淆执行卡编辑页面
│   ├── home_page.py          # 主页
│   ├── main_window.py        # 主窗口
│   └── weapon_build_page.py  # 武器配装页面
└── start.py             # 程序入口
```

## 📋 TODO 列表

等待2.0更新再说