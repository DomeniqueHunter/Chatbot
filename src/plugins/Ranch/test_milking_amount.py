
import random


def calc_lvl_bonus(lvl):
    if lvl < 200:
        m = lvl // 10
        return 1 + (m / 100)
    
    return 1.2


def variant_a(multiplier=1, milk=100, lvl=100):
    max_milk = int(milk * multiplier)
    amount = int(random.uniform(0.2 * max_milk, max_milk) * calc_lvl_bonus(lvl))
    
    return amount


def variant_b(multiplier=1, milk=100, lvl=100):
    max_milk = int(milk * multiplier * calc_lvl_bonus(lvl))
    amount = int(random.uniform(0.2 * max_milk, max_milk))

    return amount


def main():
    tank_a = []
    tank_b = []
    
    for _ in range(350000):
        tank_a.append(variant_a())
        tank_b.append(variant_b())
        
    print(f"Tank A: {sum(tank_a)} {min(tank_a)} {max(tank_a)}")
    print(f"Tank B: {sum(tank_b)} {min(tank_b)} {max(tank_b)}")
    
    d = sum(tank_b)/sum(tank_a)
    print(f"factor: {d}")
    

if __name__ == "__main__":
    main()
