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
import re


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

def getUnsignedSymbols(eq) -> list[str]:
    res: list = re.findall(r'[a-zA-Z]+', eq)
    res = list(set(res))
    res = [x for x in res if x not in FUNCTIONS]
    return res

def getSymbols(eq) -> list[str]:
    res: list = re.findall(r'[a-zA-Z]+', eq)
    return list(set([x for x in res if x not in FUNCTIONS]))

class Evaluate():
    varDict: dict = {}

    def __init__(self, input: str = '') -> None:
        self._additionalData: dict = {}
        self._input: str = input
        self._definition: bool = self._isDefinition()
        self._equation: str = self._getEquation()
        self._parameters: (list | None) = self._getParametrs()
        self._varName: str = self._getVarName()
        self._latex: str = ''
        self._result: str = self._solve()
        self._unsingedSymbols: int = len(getUnsignedSymbols(self._result))

    ### Public
    def eval(self, input: str):
        self.__init__(input)

    def evalPlotData(self):
        self._additionalData['plotResult'] = self._plotter()

    def getResult(self) -> str:
        return self._result

    def getVarName(self) -> str:
        return self._varName

    def getLatex(self) -> str:
        return self._latex

    def getUnsingedSymsCount(self) -> int:
        return self._unsingedSymbols

    def getAddData(self, key: str) -> int:
        return self._additionalData[key]

    ### Internal
    def _setLatex(self, latex: str):
        self._latex = latex

    def _solve(self) -> str:
        eq = self._equation
        syms = getSymbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS.keys():
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = getSymbols(eq)
        for i in syms02:
            if i not in FUNCTIONS.keys():
                exec(f"{i} = Symbol('{i}')")
        try:
            equation = sympify(eq, locals=FUNCTIONS)
            self._setLatex(f'={latex(equation)}')
            if self._definition and self._varName:
                varDict[self._varName] = str(equation)
            return str(equation)
        except Exception as e:
            return f'Error: {str(e)}'

    def _isDefinition(self) -> bool:
        return bool(re.findall(r'=', self._input))

    def _getEquation(self) -> str:
        if self._isDefinition():
            eq: str = re.split(r'=', self._input)[1]
            res: (tuple | str) = re.findall(EVAL_REGEX, eq)[0]
        else:
            res: (tuple | str) = re.findall(EVAL_REGEX, self._input)[0]
        if isinstance(res, tuple):
            return res[0]
        else:
            return res

    def _getParametrs(self) -> (list | None):
        if self._isDefinition():
            eq: str = re.split(r'=', self._input)[1]
        else:
            eq = self._input
        res: (tuple | str) = re.findall(EVAL_REGEX, eq)[0]
        if isinstance(res, tuple) and res[1]:
            params: str = res[1]
            resList = params.split(' ')
            resList = [float(x) for x in resList]
            return resList
        else:
            return None

    def _getVarName(self) -> str:
        if self._isDefinition():
            return (re.split(r'=', self._input)[0]).strip()
        else:
            return ''

    def _plotter(self):
        eq = self._equation
        syms = getSymbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = getSymbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        sympy_equation = simplify(eq)
        args: list = [x for x in list(set(syms02)) if x not in FUNCTIONS]
        numpy_equation = lambdify(args, sympy_equation, 'numpy')
        match self._unsingedSymbols:
            case 2:
                if self._parameters:
                    X, Y = meshgrid(linspace(self._parameters[0],
                                             self._parameters[1],
                                             int(self._parameters[2])),
                                    linspace(self._parameters[0],
                                             self._parameters[1],
                                             int(self._parameters[2])))
                else:
                    X, Y = meshgrid(linspace(-100, 100, 10), linspace(-100, 100, 10))
                equation = numpy_equation(X, Y)
                self._additionalData['X'] = X
                self._additionalData['Y'] = Y
            case _:
                if self._parameters:
                    x = linspace(self._parameters[0],
                                 self._parameters[1],
                                 int(self._parameters[2]))
                else:
                    x = linspace(-100, 100, 10)
                self._additionalData['X'] = x
                equation = numpy_equation(x)
        return equation
