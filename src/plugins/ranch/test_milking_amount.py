
import random


def calc_lvl_bonus(lvl):
    if lvl < 200:
        m = lvl // 10
        return 1 + (m / 100)
    
    return 1.2


def variant_default(multiplier=1, milk=100, lvl=100):
    max_milk = int(milk * multiplier)
    amount = int(random.uniform(0.2 * max_milk, max_milk))
    
    return amount


def variant_default_no_int(multiplier=1, milk=100, lvl=100):
    max_milk = milk * multiplier
    amount = int(random.uniform(0.2 * max_milk, max_milk))
    
    return amount


def variant_a(multiplier=1, milk=100, lvl=100):
    max_milk = int(milk * multiplier)
    amount = int(random.uniform(0.2 * max_milk, max_milk) * calc_lvl_bonus(lvl))
    
    return amount


def variant_b(multiplier=1, milk=100, lvl=100):
    max_milk = int(milk * multiplier * calc_lvl_bonus(lvl))
    amount = int(random.uniform(0.2 * max_milk, max_milk))

    return amount


def main():
    tank_0 = []
    tank_1 = []
    tank_a = []
    tank_b = []
    
    milk = 100
    multiplier = 1
    lvl = 100
    
    samples = 35_000
    
    for _ in range(samples):
        tank_0.append(variant_default(multiplier, milk, lvl))
        tank_1.append(variant_default(multiplier, milk, lvl))
        tank_a.append(variant_a(multiplier, milk, lvl))
        tank_b.append(variant_b(multiplier, milk, lvl))
    
    print(f"Tank 0: {sum(tank_0)} {min(tank_0)} {max(tank_0)}")
    print(f"Tank 1: {sum(tank_1)} {min(tank_1)} {max(tank_1)}")
    print(f"Tank A: {sum(tank_a)} {min(tank_a)} {max(tank_a)}")
    print(f"Tank B: {sum(tank_b)} {min(tank_b)} {max(tank_b)}")
    
    dA = sum(tank_a) / sum(tank_0)
    dB = sum(tank_b) / sum(tank_0)
    d1 = sum(tank_1) / sum(tank_0)
    
    print(f"dA: {dA}, dB: {dB}, d1: {d1}")
    

if __name__ == "__main__":
    main()
