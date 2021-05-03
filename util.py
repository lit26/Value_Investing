
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

def numberCovert(num):
    """covert number(str) to number(float)
    Args:
        num(str): number of string
    Return:
        num(float): number of string
    """
    if num == '-':
        return None
    elif num[-1] == '%':
        return float(num[:-1]) / 100
    elif num[-1] == 'B':
        return float(num[:-1]) * 1000000000
    elif num[-1] == 'M':
        return float(num[:-1]) * 1000000
    elif num[-1] == 'K':
        return float(num[:-1]) * 1000
    else:
        return float(''.join(num.split(',')))