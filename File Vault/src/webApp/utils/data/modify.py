def pad(input, length):
    mod_value = length - len(input)
    if mod_value > 0:
        return input + (input[0])*mod_value
    elif mod_value < 0:
        return input[0:(mod_value*(-1))]
    else:
        return input