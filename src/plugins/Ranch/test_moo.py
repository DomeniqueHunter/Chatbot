
from plugins.Ranch.Logic import Logic


def test():
    L = Logic(None)
    
    moos = [
        "Mo",
        "mo",
        "moo",
        "Moo",
        "moo~",
        "Moo Moo",
        "moo Moo~",
        "MooOoOoO~ moo! mo.",
        "moMooomoMoomoo Moo",
        "moMooomoMoomoo Mo",
        "mo moo moomoo",
        "moomoo",
        "moomoo!",
        "MooMooooMoo!?!",
        ]
    
    for moo in moos:
        print(L.is_moo(moo), "-", moo)
    
    
if __name__ == "__main__":
    test()
