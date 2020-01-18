

def concat(input, delimiter = ''):
    _message = ""
    if isinstance(input, list):
        for i in range(len(input)):
            if i < len(input) -1:
                _message += input[i] + delimiter
            else:
                _message += input[i]
        return _message
    else:
        return input