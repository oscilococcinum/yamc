from numpy import (
        ndarray, array, transpose,
        linspace, arange, append,
        meshgrid, e, pi)
from sympy import (
        sympify, lambdify, solve,
        simplify, integrate, diff, latex,
        Symbol, symbols, log, sin, cos, sinh,
        cosh, tan, tanh, asin, acos, asinh,
        acosh, ln, sqrt)
from sympy.physics.units import (
        Quantity, convert_to, meter, kilogram,
        second, ampere, kelvin, mol, candela,
        newton, pascal, m, kg, s, A, K, mole, cd, N, Pa)
from sympy.physics.units.systems.si import SI
from sympy.parsing.sympy_parser import (
        parse_expr, 
        standard_transformations, 
        implicit_multiplication_application)
from sympy import sympify
import re
from yamcsolve.PlotData import PlotData
from yamcsolve.Equation import Equation

SI_UNITS: list = ["m", "kg", "s", "A", "K", "mol", "cd"]
SI_EXTENDED: dict = {'kg*m*s**-1': "N"}
FUNCTIONS: dict = { # Math functions
                    'log':log, 'sin':sin, 'cos':cos, 'sinh':sinh, 'cosh':cosh, 'tan':tan, 'tanh':tanh,
                    'asin':asin, 'acos':acos, 'asinh':asinh, 'acosh':acosh, 'ln':ln, 'sqrt':sqrt, 'solve':solve,
                    'D': diff, 'I': integrate,
                    # Units
                    'm':m, 'kg':kg,'s':s, 'A':A,
                    'K':K, 'mole':mole, 'cd':cd, 'N':N, 'Pa':Pa,
                    # Sympy functions
                    'convertUnits':convert_to, 'lt': latex
                    }
EVAL_REGEX: str = r'([^|]*)\|?(.*)?$'

#def parseEq(eq: str) -> str:
#    try:
#        transformations = (standard_transformations + (implicit_multiplication_application,))
#        result: str = parse_expr(eq, transformations=transformations)
#        return str(result)
#    except Exception as e:
#        print(f"Error: {str(e)}")
#        return eq

def getUnsignedSymbols(eq) -> list[str]:
    res: list = re.findall(r'[a-zA-Z]+', eq)
    res = list(set(res))
    res = [x for x in res if x not in FUNCTIONS]
    return res

def getSymbols(eq) -> list[str]:
    res: list = re.findall(r'[a-zA-Z]+', eq)
    return list(set([x for x in res if x not in FUNCTIONS]))

def symPySolve(eq: str) -> str:
    syms = getSymbols(eq)
    syms02 = getSymbols(eq)
    for i in syms02:
        if i not in FUNCTIONS.keys():
            exec(f"{i} = Symbol('{i}')")
    try:
        equation = sympify(eq, locals=FUNCTIONS)
        return str(equation)
    except Exception as e:
        return f'Error: {str(e)}'

class SymPySolver:
    '''Singelton Solver object. It handles all solving and storing of app data'''
    def __init__(self) -> None:
        self._equations: dict[int, Equation] = {}
        self._results: dict[int, Equation] = {}
        self._plotData: dict[int, PlotData] = {}

    # Public
    def recomputeAll(self) -> None:
        pass

    def recomputeEq(self, id: int) -> None:
        try:
            eq = self._equations[id].getStream()
            self._results[id] = Equation(symPySolve(eq))
        except Exception as e:
            print(f'recomputeEq failed due to: {e}')

    def addEquation(self, eq: str) -> int | None:
        lastKey = len(self._equations.keys())
        try:
            self._equations[lastKey + 1] = Equation(eq)
            return lastKey + 1
        except Exception as e:
            print(f'addEquation failed due to: {e}')

    def popEquation(self, id: int) -> None:
        try:
            self._equations.pop(id)
            self._results.pop(id)
        except Exception as e:
            print(f'popEquation failed due to: {e}')

    def getPlotData(self, id: int) -> PlotData | None:
        pass

    def getEquation(self, id: int) -> Equation | None:
        try:
            return self._equations[id]
        except Exception as e:
            print(f'getEquation failed due to: {e}')

    def getResult(self, id: int) -> Equation | None:
        try:
            return self._results[id]
        except Exception as e:
            print(f'getResult failed due to: {e}')