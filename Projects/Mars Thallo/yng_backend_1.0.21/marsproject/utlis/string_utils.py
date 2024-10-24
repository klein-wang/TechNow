from decimal import Decimal, getcontext, ROUND_HALF_UP


def strIsdigit(char):
    if char:
        valueTemp = char[1:] if '-' in char else char
        value = int(char) if valueTemp.isdigit() else float(char)
        return value
    return None


# 四舍五入
def numberToFixedStr(number, num=4):
    return substringToFixed(str(number), num)


def arrToSplInt(arr):
    subStr = ""
    for item in arr:
        subStr = subStr + str(item) + ","
    subStr = subStr[:-1]
    return subStr


# 标准拼接
def arrToSplString(arr, prefix=''):
    subStr = ""
    for item in arr:
        subStr = subStr + f"{prefix}'"+str(item)+"'" + ","
    subStr = subStr[:-1]
    return subStr


# 支持对中文字段的拼接
def arrToSplStringExt(arr):
    subStr = ""
    for item in arr:
        subStr = subStr + "N'"+str(item)+"'" + ","
    subStr = subStr[:-1]
    return subStr


def getDictStrValue(dic, key, default=''):
    return str(dic.get(key)) if dic.get(key) else default


# 取整,直接截取
def substringRoundOff(numberStr):
    if numberStr:
        if '.' in numberStr:
            arr = numberStr.split('.')
            return arr[0]
        else:
            return numberStr
    return ""


# 四舍五入
def substringToFixed(numberStr, num, default=''):
    try:
        if numberStr:
            qua = Decimal('0')
            if num > 0:
                qua = Decimal('0.{}'.format("0" * num))
            return str(Decimal(numberStr).quantize(qua, rounding=ROUND_HALF_UP))
    except Exception as e:
        # 报错就将原值返回去
        return numberStr
    return default


# 精度更高的计算 除法
def decimalDivideValue(value1, value2, num):
    getcontext().prec = 20
    if value1 and value2:
        number1 = Decimal(value1)
        number2 = Decimal(value2)
        if 0 == number2:
            return ''
        result = number1 / number2
        return substringToFixed(str(result), num)
    return ""


# 精度更高的计算 乘法
def decimalMultiValue(value1, value2, num):
    getcontext().prec = 20
    if value1 and value2:
        number1 = Decimal(value1)
        number2 = Decimal(value2)
        result = number1 * number2
        return substringToFixed(str(result), num)
    return ""


# 精度更高的计算 加法
def decimalAdditionValue(strList):
    if strList:
        decTotal = Decimal('0')
        for item in strList:
            if item:
                decTotal = decTotal + Decimal(item)
        return str(decTotal)
    return ""


# 精度更高的计算 减法
def decimalSubValue(value1, value2, num, default=''):
    getcontext().prec = 20
    if value1 is not None and value1 != '' and value2 is not None and value2 != '':
        number1 = Decimal(value1)
        number2 = Decimal(value2)
        result = number1 - number2
        return substringToFixed(str(result), num)
    return default


# 如果值为None则将值置为null
def coverNoValueToNone(obj, key):
    return "NULL" if obj.get(key) is None else obj.get(key)


# 四舍五入,保留4位有效数字
#    print(substringToFixed("1.2335", 4, default=''))
#    print(substringToFixed("12.233", 4, default=''))
#    print(substringToFixed("15713.5", 4, default=''))
#    print(substringToFixed("1571.2", 4, default=''))
#    print(substringToFixed("12345", 4, default=''))
# 1.234
# 12.23
# 12.20
# 15710
# 1571
# 12340
def effectiveDigitToFixed(numberStr, num, default=''):
    try:
        if numberStr:
            if '.' not in numberStr:
                return f"{numberStr}.{('0' * (num - len(numberStr)))}" if (num - len(numberStr)) > 0 else f"{numberStr[:num]}{('0' * (len(numberStr) - num))}"

            arr_spl = numberStr.split('.')
            sp0 = arr_spl[0]
            if len(sp0) - num >= 0:
                return f"{sp0[:num]}{('0' * (len(sp0) - num))}"

            sp1 = f"{arr_spl[1]}{('0' * (num - len(sp0) - len(arr_spl[1]) + 1))}" if (num - len(sp0)) > len(arr_spl[1]) else arr_spl[1] + "0"
            qua = Decimal('0.{}'.format("0" * (num - len(sp0))))
            return str(Decimal(f"{sp0}.{sp1}").quantize(qua, rounding=ROUND_HALF_UP))
    except Exception as e:
        # 报错就将原值返回去
        return numberStr
    return default


def is_number_by_str(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# 将decimal转为浮点类型
def coverDecimalToFloat(obj, key, default=None):
    return float(obj.get(key)) if obj.get(key) else default
