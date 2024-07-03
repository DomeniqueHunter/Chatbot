

def worker_multiplier(lvl):
    if lvl < 200:
        m = lvl // 10
        return 1 + (m / 100)
    
    return 1.2
    

def main():
    for lvl in [0, 1, 5, 10, 15, 20, 50, 99, 100, 101, 150, 190, 199, 200, 201, 1000]:
        print(lvl, worker_multiplier(lvl))


if __name__ == "__main__":
    main()
