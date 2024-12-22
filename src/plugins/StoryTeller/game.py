import random


class Commands:
    INSERT = 0
    FUCK_HARD = 1
    FUCK_SLOW = 2
    CUM = 3
    HOLD_ON = 4
    PULL_OUT = 9


class Game:
    
    def __init__(self, user):
        self.user = user
        self.stage = 0
        self.points = 0
        self.running = True
    
    def options(self):
        if self.stage == 0:
            return [(Commands.INSERT, "insert", 1)]
        elif 1 <= self.stage <= 3:
            return [(Commands.FUCK_HARD, "fuck hard", 1), (Commands.PULL_OUT, "pull out", 1)]
        elif 4 <= self.stage <= 6:
            return [(Commands.FUCK_SLOW, "fuck slow", .95), (Commands.CUM, "cum", 1), (Commands.PULL_OUT, "pull out", .6)]
        elif 7 <= self.stage <= 10:
            return [(Commands.FUCK_SLOW, "fuck slow", .95), (Commands.CUM, "cum", .8), (Commands.PULL_OUT, "pull out", .3)]
        else:  # > 10
            return [(Commands.HOLD_ON, "fuck slow", .6), (Commands.CUM, "cum", .7), (Commands.PULL_OUT, "pull out", 0)]
            
    def current_page(self):
        if not self.running: return self.end_page()
        message = f"You are on stage {self.stage}\n"
        
        usage = ""
        for option in self.options():
            nr, label, chance = option
            usage += f"{nr} - {label} ({int(chance*100)}%)\n"
        
        return message + usage
    
    def end_page(self):
        message = f"Game Over at {self.stage} with {self.points} points!"
        return message
    
    def _roll(self, n:float) -> bool:
        return random.uniform(0, 100) < n * 100
    
    def choice(self, option:int):
        if not self.running: return self.end_page()
        
        for opt in self.options():
            nr, label, chance = opt
            if nr == option:
                break
        else:
            # no option found
            return "no valid option!"
        
        match nr:
            case Commands.INSERT:
                message = "you inserted your cock in a warm throbbing sheat"
                self.stage += 1
                return message
            
            case Commands.FUCK_HARD:
                if self._roll(chance):
                    self.stage += 1
                    self.points += 1
                    return f"you pount that warm pussy hard"
                
            case Commands.FUCK_SLOW:
                if self._roll(chance):
                    self.stage += 1
                    self.points += 1
                    return f"you moan and fuck the pussy careful"
                else:
                    self.running = False
                    self.points += 1
                    return f"you came early and ended your run"
                
            case Commands.CUM:
                if self._roll(chance):
                    self.running = False
                    self.points += self.stage
                    return f"you shoot your load in that warm pussy and pull your cock out! (You earned {self.points} points this run!)"
                else:
                    self.running = False
                    self.points += 2
                    return f"you come in that warm throbbing pussy and lose your control, the sheath sucks you in and churns you to cum!"
            
            case Commands.PULL_OUT:
                if self._roll(chance):
                    self.running = False
                    return f"you pulled out and ended the session"
                
                else:
                    self.running = False
                    self.points += 1
                    return f"you tried to pull out but wre too weat, the hole sucked you in!"
                
            case Commands.HOLD_ON:
                if self._roll(chance):
                    self.stage += 1
                    return f"you hold on the handle bard and try not to get swallowed by the warm pussy. It sucks your cock hard and clearly trys to eat you!"
                
                else:
                    self.running = False
                    self.points += 2
                    return f"the warm hole swallowed you whole and churned you to cum!"
            
        return "no option"
    
    
def main():
    game = Game("user")
    
    print(game.current_page())
    
    print(game.choice(1))
    print(game.choice(0))
    print(game.current_page())
    
    print(game.choice(1))
    print(game.current_page())
    
    print(game.choice(1))
    print(game.current_page())
    
    print(game.choice(1))
    print(game.current_page())
    
    print(game.choice(2))
    print(game.current_page())
    
    print(game.choice(2))
    print(game.current_page())
    
    print(game.choice(2))
    print(game.current_page())
    
    print(game.choice(2))
    print(game.current_page())
    
    print(game.choice(2))
    print(game.current_page())
    
    print(game.choice(3))
    print(game.current_page())
    
    # success = [game._roll(.95) for _ in range(1_000_000)]
    # print(sum(success))
    
    
if __name__ == "__main__":
    main()
