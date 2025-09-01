from numpy import ndarray, array, transpose, linspace, arange, append
import sympy as sc
import re


def contains_alpha(s: str) -> bool:
    """
    Check if the string contains at least one letter (a-z or A-Z).
    
    :param s: Input string
    :return: True if the string contains any alphabetic character, False otherwise
    """
    return bool(re.search(r'[a-zA-Z]', s))


def insert_multiplication(eq: str) -> str:
    # Insert * between a digit and a letter (e.g., 2x → 2*x)
    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)

def evalEq(eq: str) -> float:
    return eval(eq)

def algEvalEq(eq: str) -> str:
    eq = insert_multiplication(eq)
    symbols: list = [char for char in eq if char.isalpha()]
    for i in symbols:
        exec(f"{i} = sc.Symbol('{i}')")
    return eval(eq)

def integ(eq: str, d_: str) -> str:
    eq = insert_multiplication(eq)
    symbols: list = [char for char in eq if char.isalpha()]
    for i in symbols:
        exec(f"{i} = sc.Symbol('{i}')")
    exp = sc.simplify(eq)
    d_ = d_.replace('d', '')
    d_ = sc.simplify(d_)
    return str(sc.integrate(exp, d_))

def diff(eq: str, d_: str, n: int = 1) -> str:
    eq = insert_multiplication(eq)
    symbols: list = [char for char in eq if char.isalpha()]
    for i in symbols:
        exec(f"{i} = sc.Symbol('{i}')")
    exp = sc.simplify(eq)
    d_ = d_.replace('d', '')
    d_ = sc.simplify(d_)
    return str(sc.diff(exp, d_, n))

#def csvToTable(path:str) -> str:
#    path = path.removeprefix('csv:')
#    with open(path, 'r') as file:
#        stream: str = file.read()
#    table: list = stream.split('\n')
#    table = [x.split(',') for x in table]
#    eq = f'{[[float(x) for x in i] for i in table]}'
#    return eval(eq)

def generalEval(eq: str, optionalVarDict: dict = {}) -> (str | float):
    
    eq = insert_multiplication(eq)
    tmp_list = list(eq)
    result = [optionalVarDict.get(ch, ch) for ch in tmp_list]
    eq = ''.join(result)

#    if bool(re.search(r'^d.*d.*$', eq)):
#        suffix = re.search(r'd.*$')[0]
#        diffEq = eq.removeprefix('d')
#        diffEq = eq.removesuffix(suffix)
#        d_ = suffix.removeprefix('d')
#        if re.search(r'\d$', d_):
#            n = int(re.search(r'\d$', d_)[0])
#        else: n = 1
#        d_ = re.search(r'.$', d_)[0]
#        return diff(diffEq, d_, n)

    if contains_alpha(eq):
        return algEvalEq(eq)
    else:
        return evalEq(eq)

if __name__ == '__main__':
    print(evalEq('2**-5*3+3'))
    print(algEvalEq('2x*8y+20'))
    print(integ('2x*8y+20', 'dy'))
    print(diff('2y**5+6y', 'dy', 1))
    print(diff('2y**5+6y', 'dy', 2))
    #print(generalEval('S2x*8y+20dy'))
    #print(generalEval('D2y**5+6yd2y'))
    #print(generalEval('2y**5+6x', {'x':'15a'}))
    #print(generalEval('S2y**5+6xda', {'x':'15a'}))
    #print(generalEval('SS2y**5+6xda', {'x':'15a'}))