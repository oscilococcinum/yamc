from numpy import ndarray, array, transpose, linspace, arange, append, meshgrid, e, pi
from sympy import sympify, lambdify, solve, simplify, integrate, diff, latex, Symbol, symbols, log, sin, cos, sinh, cosh, tan, tanh, asin, acos, asinh, acosh, ln, sqrt
from sympy.physics.units.systems.si import SI
from sympy.physics.units import Quantity, convert_to, meter, kilogram, second, ampere, kelvin, mol, candela, newton, pascal
import re


SI_UNITS: list = ["m", "kg", "s", "A", "K", "mol", "cd"]
SI_EXTENDED: dict = {'kg*m*s**-1':"N"}

def deter_plot_type(eq) -> int:
    eq = insert_multiplication(eq)
    syms = re.findall(r'[a-zA-Z]+', eq)
    return len(syms)

def contains_symbols(s: str) -> bool:
    """Check if the string contains at least one letter (a-z or A-Z)."""
    return bool(re.search(r'[a-zA-Z]', s))

def contains_units(s: str) -> bool:
    """Check if the string contains at least one unit ([a-z or A-Z])."""
    return bool(re.search(r'\[[a-zA-Z0-9]+\]', s))

def insert_multiplication(eq: str) -> str:
    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)

def insert_par_before_div(eq: str) -> str:
    return re.sub(r'(\/)(.*$)', r'\1(\2)', eq)

def insert_units_multiplication(eq: str) -> str:
    return re.sub(r'([a-zA-Z0-9]+)(\[\w+?\])', r'\g<1>*\g<2>', eq)

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

def mat_contour(eq: str, domian: ndarray):
    X, Y = meshgrid(domian[0], domian[1])
    x, y = symbols('x y')
    expr = sympify(eq)
    f = lambdify((x, y), expr, modules='numpy')
    X, Y = meshgrid(X, Y)
    Z = f(X, Y)
    return Z, X, Y

def generalEval(eq: str, optionalVarDict: dict = {}, operation:str = '', additional: ndarray = array([])) -> (str | float | ndarray | tuple):
    eq = insert_multiplication(eq)
    tmp_list: list[str] = re.split(r'(\+|\-|\*|\/)', eq)
    result = [str(optionalVarDict.get(ch, ch)) for ch in tmp_list]
    eq = ''.join(result)
    eq = insert_par_before_div(eq)

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