import math
import re

def to_hex(string):
    return "".join([hex(ord(c))[2:].zfill(2) for c in string])

def to_dec(string):
    return "".join([str(ord(c)) + ' ' for c in string])

def trim(string):
    return re.sub('\s{2,}|\t|\n|\r',' ',string)

def escape(string):
    return re.sub('"','`',string)
    
def width_specifier(string, width, trim=True , **params):
    MAX_TOLERANCE = 3
    result = []
    if trim:
        string = trim(string)
    string = escape(string)
    if len(string) < width:
        return [string]
    if width is 0:
        return [string]
    elif width <= MAX_TOLERANCE:
        MAX_TOLERANCE = 0
    while true:
        if re.search('[\S]', string[width]) is True:
            result.append(string[:width])
            string = string[width:]
        else:
            flag = False
            for index in reversed(string[(width-MAX_TOLERANCE):width]):
                if re.search('[\S]', string[width]) is True:
                    result.append(string[:index])
                    string = string[index:]
                    flag = True
                    break
                else:
                    pass
            if flag is False:
                result.append(string[:width])
                string = string[width:]
        if len(string) is 0:
            return result
        else:
            pass
