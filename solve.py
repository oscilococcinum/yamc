from numpy import ndarray, array, transpose, linspace, arange, append, pi, e
from sympy import sympify, simplify, integrate, diff, latex, Symbol, log, sin, cos, sinh, cosh, tan, tanh, asin, acos, asinh, acosh, ln, sqrt
import re


unit_dict: dict = {"m":"m", "kg":"kg", "s":"s", "A":"A", "K":"K", "mol":"mol", "cd":"cd"}

def contains_symbols(s: str) -> bool:
    """Check if the string contains at least one letter (a-z or A-Z)."""
    return bool(re.search(r'[a-zA-Z]', s))

def contains_units(s: str) -> bool:
    """Check if the string contains at least one unit ([a-z or A-Z])."""
    return bool(re.search(r'\[[a-zA-Z]\]', s))

def insert_multiplication(eq: str) -> str:
    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)

def insert_unit_multiplication(eq: str) -> str:
    return re.sub(r'(\d)([\[a-zA-Z\]])', r'\1*\2', eq)

def evalEq(eq: str) -> float:
    return eval(eq)

def evalAlgEq(eq: str) -> str:
    eq = insert_multiplication(eq)
    symbols: list = [char for char in eq if char.isalpha()]
    for i in symbols:
        exec(f"{i} = Symbol('{i}')")
    return eval(eq)

def integ(eq: str, d_: str) -> str:
    eq = insert_multiplication(eq)
    symbols: list = [char for char in eq if char.isalpha()]
    for i in symbols:
        exec(f"{i} = Symbol('{i}')")
    exp = simplify(eq)
    d_ = d_.replace('d', '')
    d_ = simplify(d_)
    return str(integrate(exp, d_))

def differ(eq: str, d_: str) -> str:
    eq = insert_multiplication(eq)
    d_ = d_.removeprefix('d')
    if bool(re.findall(r'^\d+', d_)):
        n: int = int(re.findall(r'^\d+', d_)[0])
    else: n = 1
    d_ = re.findall(r'\D*$', d_)[0]
    d_ = simplify(d_)
    symbols: list = [char for char in eq if char.isalpha()]
    for i in symbols:
        exec(f"{i} = Symbol('{i}')")
    exp = simplify(eq)
    return str(diff(exp, d_, n))

def mat(eq: str, domian: ndarray) -> ndarray:
    return array([eval(eq) for x in domian])

def generalEval(eq: str, optionalVarDict: dict = {}, operation:str = '', additional: ndarray = array([])) -> (str | float | ndarray):
    eq = insert_multiplication(eq)
    tmp_list: list[str] = re.split(r'(\+|\-|\*|\/)', eq)
    result = [str(optionalVarDict.get(ch, ch)) for ch in tmp_list]
    eq = ''.join(result)

    if operation == 'integration':
        return integ(eq, additional[0])
    elif operation == 'differentiation':
        return differ(eq, additional[0])
    elif operation == 'ploting':
        return mat(eq, additional)
    elif contains_symbols(eq):
        return evalAlgEq(eq)
    else:
        return evalEq(eq)