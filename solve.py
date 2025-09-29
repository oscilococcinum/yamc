from numpy import (
        ndarray, array, transpose,
        linspace, arange, append,
        meshgrid, e, pi)
from sympy import (
        sympify, lambdify, solve,
        simplify, N, integrate, diff, latex,
        Symbol, symbols, log, sin, cos, sinh,
        cosh, tan, tanh, asin, acos, asinh,
        acosh, ln, sqrt)
from sympy.physics.units import (
        Quantity, convert_to, meter, kilogram,
        second, ampere, kelvin, mol, candela,
        newton, pascal)
from sympy.physics.units.systems.si import SI
import re


SI_UNITS: list = ["m", "kg", "s", "A", "K", "mol", "cd"]
SI_EXTENDED: dict = {'kg*m*s**-1': "N"}
FUNCTIONS: list[str] = ['log', 'sin', 'cos', 'sinh', 'cosh', 'tan', 'tanh',
                        'asin', 'acos', 'asinh', 'acosh', 'ln', 'sqrt']
DIFF_REGEX: str = r'^.*=?diff\((.*)\)\((.*)\)$'
INT_REGEX: str = r'^.*=?int\((.*)\)\((.*)\)$'
EVAL_REGEX: str = r'.*'

def getSymbols(eq) -> list[str]:
    return re.findall(r'[a-zA-Z]+', eq)


def insertParBeforeDiv(eq: str) -> str:
    return re.sub(r'(\/)(.*$)', r'\1(\2)', eq)


class Evaluate():
    varDict: dict = {}

    def __init__(self, input: str = '', plotting: bool = False) -> None:
        self.additionalData: dict = {}
        self.input: str = input
        self.definition: bool = self.isDefinition()
        self.type: str = self.getEqType()
        self.equation: str = self.getEquation()
        self.parameters: (list | None) = self.getParametrs()
        self.varName: (str | None) = self.getVarName()
        self.result: str = self.solve()
        self.unsingedSymbols: int = len(getSymbols(self.result))
        self.plotting = plotting
        if plotting:
            self.evalPlotData()

    def solve(self) -> str:
        eq = self.equation
        syms = getSymbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = getSymbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insertParBeforeDiv(eq)
        match self.type:
            case 'differtiation':
                d_ = sympify('x')
                equation = diff(sympify(eq), d_)
                if self.definition and self.varName:
                    varDict[self.varName] = str(equation)
                return str(equation)
            case 'integration':
                d_ = sympify('x')
                equation = integrate(sympify(eq), d_)
                if self.definition and self.varName:
                    varDict[self.varName] = str(equation)
                return str(equation)
            case _: # Evaluation
                equation = sympify(eq)
                if self.definition and self.varName:
                    varDict[self.varName] = str(equation)
                return str(equation)

    def evalPlotData(self):
        self.additionalData['plotResult'] = self.plotter()

    def getEqType(self) -> str:
        if re.search(DIFF_REGEX, self.input):
            return 'differtiation'
        elif re.search(INT_REGEX, self.input):
            return 'integration'
        else:
            return 'evaluation'

    def isDefinition(self) -> bool:
        return bool(re.findall(r'=', self.input))

    def getEquation(self) -> str:
        if self.isDefinition():
            eq: str = re.split(r'=', self.input)[1]
            match self.type:
                case 'differtiation':
                    res: (tuple | str) = re.findall(DIFF_REGEX, eq)[0]
                case 'integration':
                    res: (tuple | str) = re.findall(INT_REGEX, eq)[0]
                case _: # evaluation
                    res: (tuple | str) = re.findall(EVAL_REGEX, eq)[0]
        else:
            match self.type:
                case 'differtiation':
                    res: (tuple | str) = re.findall(DIFF_REGEX, self.input)[0]
                case 'integration':
                    res: (tuple | str) = re.findall(INT_REGEX, self.input)[0]
                case _: # evaluation
                    res: (tuple | str) = re.findall(EVAL_REGEX, self.input)[0]
        if isinstance(res, tuple):
            return res[0]
        else:
            return res

    def getParametrs(self) -> (list | None):
        if self.isDefinition():
            eq: str = re.split(r'=', self.input)[1]
            match self.type:
                case 'differtiation':
                    res: (tuple | str) = re.findall(DIFF_REGEX, eq)[0]
                case 'integration':
                    res: (tuple | str) = re.findall(INT_REGEX, eq)[0]
                case _: # evaluation
                    res: (tuple | str) = re.findall(EVAL_REGEX, eq)[0]
        else:
            match self.type:
                case 'differtiation':
                    res: (tuple | str) = re.findall(DIFF_REGEX, self.input)[0]
                case 'integration':
                    res: (tuple | str) = re.findall(INT_REGEX, self.input)[0]
                case _: # evaluation
                    res: (tuple | str) = re.findall(EVAL_REGEX, self.input)[0]
        if isinstance(res, tuple) and res[1]:
            params: str = res[1]
            resList = params.split(',')
            resList = [float(x) for x in resList]
            return resList
        else:
            return None

    def getVarName(self) -> (str | None):
        if self.isDefinition():
            return (re.split(r'=', self.input)[0]).strip()
        else:
            return None

    def plotter(self):
        eq = self.equation
        syms = getSymbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = getSymbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insertParBeforeDiv(eq)
        sympy_equation = simplify(eq)
        args: list = [x for x in list(set(syms02)) if x not in FUNCTIONS]
        numpy_equation = lambdify(args, sympy_equation, 'numpy')
        match self.unsingedSymbols:
            case 2:
                if self.parameters:
                    X, Y = meshgrid(linspace(self.parameters[0],
                                             self.parameters[1],
                                             int(self.parameters[2])),
                                    linspace(self.parameters[0],
                                             self.parameters[1],
                                             int(self.parameters[2])))
                else:
                    X, Y = meshgrid(linspace(-100, 100, 10), linspace(-100, 100, 10))
                equation = numpy_equation(X, Y)
                if self.definition and self.varName:
                    varDict[self.varName] = str(equation)
                self.additionalData['X'] = X
                self.additionalData['Y'] = Y
            case _:
                if self.parameters:
                    x = linspace(self.parameters[0],
                                 self.parameters[1],
                                 int(self.parameters[2]))
                else:
                    x = linspace(-100, 100, 10)
                self.additionalData['X'] = x
                equation = numpy_equation(x)
                if self.definition and self.varName:
                    varDict[self.varName] = str(equation)
        return equation


if __name__ == '__main__':
    eva = Evaluate('2x+8*6x')
    eva01 = Evaluate('b=2x+8*6x')
    eva02 = Evaluate('D(2x+8*6x)(x)')
    eva03 = Evaluate('c=I(2x+8*6x)(x)')
    eva04 = Evaluate('P(2x+8*6x)(x)')
    eva05 = Evaluate('P3D(2x+8*6y)(x,y)')
    eva06 = Evaluate('l=P3D(2x+8*6y)(x,y)')
    eva07 = Evaluate('y=2x+8*6x')
    eva08 = Evaluate('t=2x+8*6x')
    eva09 = Evaluate('t=2sin(x)+8*6cos(x)')

    b = N(simplify('2*x*cos(15)'))
    res = eva09.result
    a = 0
