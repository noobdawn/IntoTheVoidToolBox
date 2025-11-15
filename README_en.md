# IntoTheVoidToolBox — "Into the Void" Toolbox

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

[English](README_en.md) | [中文](README.md)

## 📖 Overview

Welcome to the "Into the Void" Toolbox!

This tool aims to provide out-of-game functional support for the game "Into the Void". Currently, this toolbox offers basic weapon execution card loadout functionality. Other features, such as character execution card loadouts, may be provided in the future.

**Disclaimer**: This tool is developed by an individual and has no affiliation with the developer of "Into the Void", Hangzhou Jinzhangshu Technology Co., Ltd.

## ✨ Feature Introduction

### 🔫 Weapon Execution Card Loadout

Install and uninstall execution cards here, experiment with different card combinations, and select various damage calculation methods to see the improvement from the cards.

Currently, it only supports execution card loadouts for three weapon types: rifles, pistols, and shotguns. Bows and launchers are not yet supported due to their charging mechanics; melee weapons are also not supported because they do not consume ammo, lack a multishot mechanic, and have unique attack modes like sword waves.

Note that the damage calculation here only considers the output within a single magazine. For weapons with low status chance, the DPS from elemental status effects may be inaccurate. For weapons with low magazine capacity, the DPS may also be skewed due to random factors like critical hits. Additionally, status duration is not considered, so weapons with low status chance and large magazine capacity might have their DPS overestimated.

### 💎 Custom Riven Card Editor

You can input custom riven cards to help calculate their benefits.

The affix types and bonus ranges are not restricted, so you can consider inputting special riven cards to simulate the effects of other cards, such as the "Vigilante Armaments" for machine guns.

## 🎯 How to Use

1.  **Add a Custom Riven Card**
    *   Go to the "Custom Riven Card" page.
    *   Fill in the card name, select the weapon type, number of affixes, and polarity.
    *   Add properties and set their values.
    *   Click the save button.

2.  **Configure Weapon Build**
    *   Go to the "Weapon Loadout" page.
    *   Select the target weapon from the dropdown menu or enter text for auto-completion.
    *   Set environmental parameters such as target type, armor level, etc.
    *   Configure character buffs (e.g., skill damage increase).

3.  **Select Execution Cards**
    *   Browse available execution cards in the list below.
    *   View the enhancement effect of each card in the current loadout.
    *   Click on an empty execution card slot, then select a card to equip it.
    *   Right-click on an equipped execution card to unequip it.

4.  **View Damage Analysis**
    *   Select different DPS calculation methods for comparison.

## 📚 Dependencies

This project relies on the following main libraries:

*   **PyQt5**: A cross-platform GUI framework.
*   **PyQt-Fluent-Widgets**: A UI component library with a Fluent Design style.
*   **pynput**: A library for monitoring keyboard and mouse input.
*   **numpy**: A high-performance numerical computing library.

For a detailed list of dependencies, please see [requirements.txt](requirements.txt).

## 📋 TODO List

Waiting for the 2.0 update. I will decide on further updates based on whether it's fun.

*   [x] Calculation support for melee weapons.
*   [x] Calculation support for bows, launchers, etc.
*   [x] Equivalent magazine capacity calculation for weapons with unlimited ammo.
*   [x] DPS calculation including weak point damage.
*   [x] Skill damage support for some popular characters.
*   [x] Support for changes in version 2.0.
