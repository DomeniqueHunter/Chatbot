
from plugins.Ranch.Logic import Logic


def test_is_moo():
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
        "[sub]M[/sub]o[sup]OᴼO[/sup]o[sub]Oₒo[/sub]O[sup]oᴼO[/sup]o[sub]Oₒo[/sub]O[sup]oᴼO[/sup]o",
        ]
    
    for moo in moos:
        print(L.is_moo(moo), "-", moo)
    
    
if __name__ == "__main__":
    test_is_moo()
    
