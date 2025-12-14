

def parsed(op:str, msg:str | None="") -> tuple[str,str]: 
    return op, msg


def test():
    messages = [
        "PIN",
        "MSG {data}",
        ]
    
    for message in messages:
        print(message)
        data = message.split(" ", 1)
        op, msg = parsed(*data)
        print(f"op: '{op}', msg: '{msg}'")


if __name__ == "__main__":
    test()
