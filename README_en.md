# IntoTheVoidToolBox

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

[English](README_en.md) | [中文](README.md)

## 📖 Overview

Welcome to the IntoTheVoidToolBox!

This tool provides external utility features for the game "Into the Void". Currently, it offers basic weapon execution card loadout functionality, with potential future additions such as character execution card loadouts.

**Disclaimer**: This tool is independently developed and has no affiliation with the game's developer, Hangzhou Jinzhang Shu Technology Co., Ltd.

## ✨ Feature Pages Overview

### 🔫 Weapon Execution Card Loadout

Install and uninstall execution cards here, experiment with different execution card combinations, and choose different damage calculation methods to view the improvement percentage of execution cards.

### 💎 Custom Riven Execution Card Editor

Record custom riven execution cards to help calculate execution card benefits.

## 🎯 Usage

1. **Add Custom Riven Execution Cards**
   - Navigate to "Custom Riven Execution Card" page
   - Fill in card name, select weapon type, number of affixes, and polarity
   - Add properties and set values
   - Click save button

2. **Configure Weapon Build**
   - Navigate to "Weapon Loadout" page
   - Select target weapon from dropdown menu, or input text for auto-completion
   - Set environment parameters such as target type, armor level, etc.
   - Configure character buff effects (e.g., skill damage boost)

3. **Select Execution Cards**
   - Browse available execution cards in the list below
   - View each card's amplification effect in current loadout
   - Click on an empty execution card slot, then select a card to equip it
   - Right-click on equipped cards to unequip

4. **View Damage Analysis**
   - Choose different DPS calculation methods for comparison

## 📚 Dependencies

This project depends on the following main libraries:

- **PyQt5**: Cross-platform GUI framework
- **PyQt-Fluent-Widgets**: Fluent Design style UI component library
- **pynput**: Keyboard and mouse input monitoring
- **numpy**: High-performance numerical computing library

See [requirements.txt](requirements.txt) for the complete dependency list.

## 🛠️ Development

### Project Structure

```
IntoTheVoidToolBox/
├── assets/              # Resource files
│   ├── images/          # Carousel images
│   ├── splash/          # Splash screen
│   └── ui/              # UI assets
├── core/                # Core business logic
│   ├── ivtcard.py       # Execution card data structures
│   ├── ivtcontext.py    # Global context management
│   ├── ivtdps.py        # Damage calculation engine
│   ├── ivtenum.py       # Enumeration type definitions
│   ├── ivtproperty.py   # Property system
│   ├── ivtweapon.py     # Weapon system
│   └── loader.py        # Data loader
├── data/                # Data files
│   ├── cards.json       # Execution card data
│   ├── rivens.json      # Riven execution card data
│   ├── specials.json    # Special execution card data
│   └── weapons.json     # Weapon data
├── tools/               # Utility scripts
│   └── weapon_my_ocr.py # OCR recognition tool
├── ui/                  # User interface
│   ├── components/      # UI components
│   ├── edit_riven_page.py    # Riven card editor page
│   ├── home_page.py          # Home page
│   ├── main_window.py        # Main window
│   └── weapon_build_page.py  # Weapon loadout page
└── start.py             # Program entry point
```

## 📋 TODO List

Wait for 2.0 update! 
