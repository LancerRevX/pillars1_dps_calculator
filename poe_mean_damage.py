from statistics import mean
from dataclasses import dataclass

COMMON = 0
FINE = 1
EXCEPTIONAL = 2
SUPERB = 3
LEGENDARY = 4


class DR:
    CRUSH = 0
    PIERCE = 1
    SLASH = 2
    FIRE = 3
    CORRODE = 4
    FREEZE = 5
    SHOCK = 6

    def __init__(self, base, other=None):
        if other is None:
            other = {}
        self.drs = other
        self.base = base

    def __getitem__(self, item):
        if self.drs.get(item):
            return self.drs[item]
        else:
            return self.base


@dataclass
class Enemy:
    dr: DR


class Armor:
    BREASTPLATE = 0

    def __init__(self, type, durganized=False):
        self.type = type
        self.durganized = durganized

    @property
    def speed_factor(self):
        speed_factor = 1
        if self.type == self.BREASTPLATE:
            speed_factor -= 0.4
        if self.durganized:
            speed_factor += 0.15
        return speed_factor

class Weapon:
    VERYSMALL_ONEHANDED = -1
    SMALL_ONEHANDED = 0
    BIG_ONEHANDED = 1
    TWOHANDED = 2

    def __init__(self, type, damage_types, crit_bonus=False, durganized=False, attack_speed=False):
        self.type = type
        self.damage_types = damage_types
        self.crit_bonus = crit_bonus
        self.durganized = durganized
        self.attack_speed = attack_speed

    @property
    def attack_time(self):
        if self.type == self.VERYSMALL_ONEHANDED:
            return 19.1
        if self.type == self.SMALL_ONEHANDED:
            return 20
        if self.type == self.BIG_ONEHANDED or self.type == self.TWOHANDED:
            return 30


class Rogue:
    def __init__(
            self, *,
            might=10, dexterity=10,
            armor: Armor, gloves_of_swift_action=False,
            dual_wield_talent=False, vulnerable_attack=False):
        self.might = might
        self.dexterity = dexterity
        self.armor = armor
        self.swift_action = gloves_of_swift_action
        self.dual_wielding = False
        self.right_weapon = None
        self.left_weapon = None
        self.dual_wield_talent = dual_wield_talent
        self.vulnerable_attack = vulnerable_attack

    def give_weapons(self, right: Weapon, left: Weapon = None):
        self.dual_wielding = bool(left)
        self.right_weapon = right
        self.left_weapon = left

    def get_dps(self, enemy: Enemy):
        attack_speed_mult = 1

    def get_attack_duration(self, weapon):
        return weapon.attack_time / (1.0 + (self.dexterity - 10) / 33.3)

    def get_recovery_duration(self, weapon):
        attack_speed_mult = 1
        if self.swift_action:
            attack_speed_mult *= 1.15
        if weapon.durganized:
            attack_speed_mult *= 1.15
        if self.dual_wielding and self.dual_wield_talent:
            attack_speed_mult += 0.2
        if self.vulnerable_attack:
            attack_speed_mult -= 0.2
        attack_speed_mult -= 1
        speed_coef = self.armor.speed_factor + attack_speed_mult + 0 if self.dual_wielding else -0.5
        return self.get_attack_duration(weapon) * max(0, 1 - 2 * speed_coef) / 1.2


def get_dps(
        damage_min: int, damage_max: int,
        frames_per_attack: int,
        damage_reduction: int,
        dr_bypass: int,
        lash: float,
        quality: int,
        might: int,
        *,
        crit=True,
        deathblows=True,
        sneak_attack=True,
        sabre=False,
        reckless_assault=True,
        crit_bonus=False):
    base_damage = mean((damage_min, damage_max))
    damage_multiplier = 1
    damage_multiplier += (might - 10) * 0.03
    if (quality == FINE): damage_multiplier += 0.15
    if (quality == EXCEPTIONAL): damage_multiplier += 0.3
    if (quality == SUPERB): damage_multiplier += 0.45
    if (quality == LEGENDARY): damage_multiplier += 0.55
    if (crit):
        damage_multiplier += 0.5
        if (crit_bonus): damage_multiplier += 0.5
    if (sneak_attack): damage_multiplier += 0.5
    if (sabre): damage_multiplier += 0.2
    if (reckless_assault): damage_multiplier += 0.2
    if (deathblows): damage_multiplier += 1.0
    print('Damage multiplier =', damage_multiplier)
    modified_damage = base_damage * damage_multiplier
    print('Modified damage =', modified_damage)
    lash_damage = modified_damage * lash - damage_reduction / 4
    print('Lash damage =', lash_damage)
    hit_damage = modified_damage - (damage_reduction - dr_bypass) + lash_damage
    print('Hit damage =', hit_damage)
    time_for_attack = (frames_per_attack / 30)
    print('Attack time =', time_for_attack)
    dps = hit_damage / time_for_attack
    print('DPS =', dps)
    return dps


if __name__ == '__main__':
    doc_plate = Armor(Armor.BREASTPLATE, True)
    doc = Rogue(
        might=14,
        dexterity=11,
        armor=doc_plate,
        gloves_of_swift_action=True,
        dual_wield_talent=False,
        vulnerable_attack=False)
    sword = Weapon(
        Weapon.BIG_ONEHANDED,
        [DR.SLASH, DR.PIERCE],
        crit_bonus=False,
        durganized=False,
        attack_speed=False)
    print(doc.get_recovery_duration(sword))
