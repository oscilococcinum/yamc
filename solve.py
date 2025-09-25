from numpy import ndarray, array, transpose, linspace, arange, append, meshgrid, e, pi
from sympy import sympify, lambdify, solve, simplify, N, integrate, diff, latex, Symbol, symbols, log, sin, cos, sinh, cosh, tan, tanh, asin, acos, asinh, acosh, ln, sqrt
from sympy.physics.units.systems.si import SI
from sympy.physics.units import Quantity, convert_to, meter, kilogram, second, ampere, kelvin, mol, candela, newton, pascal
import re


SI_UNITS: list = ["m", "kg", "s", "A", "K", "mol", "cd"]
SI_EXTENDED: dict = {'kg*m*s**-1':"N"}
FUNCTIONS: list[str] = ['log', 'sin', 'cos', 'sinh', 'cosh', 'tan', 'tanh', 'asin', 'acos', 'asinh', 'acosh', 'ln', 'sqrt']

def get_symbols(eq) -> list[str]:
    return re.findall(r'[a-zA-Z]+', eq)

#def insert_multiplication(eq: str) -> str:
#    if isinstance(eq, tuple):
#        eq = eq[0]
#    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)

def insert_par_before_div(eq: str) -> str:
    return re.sub(r'(\/)(.*$)', r'\1(\2)', eq)


class Evaluate():
    varDict: dict = {}
    def __init__(self, input: str = '') -> None:
        self.additionalData: dict = {}
        self.typeDict: dict = {'plotting3D': [r'^.*=?3d\((.*)\)\((.*)\)$', self.plotter3d],
                      'plotting2D': [r'^.*=?2d\((.*)\)\((.*)\)$', self.plotter2d],
                      'differtiation': [r'^.*=?diff\((.*)\)\((.*)\)$', self.differtiator],
                      'integration': [r'^.*=?int\((.*)\)\((.*)\)$', self.integrator],
                      'evaluation': [r'.*', self.evaluator]}
        self.input: str = input
        self.definition: bool = self.isDefinition()
        self.type: str = self.getEqType()
        self.equation: str = self.getEquation()
        self.parameters: (list | None) = self.getParametrs()
        self.varName: (str | None) = self.getVarName()
        self.result: str = self.typeDict[self.type][1]()


    def getEqType(self) -> str:
        if re.search(self.typeDict['plotting3D'][0], self.input): return 'plotting3D'
        elif re.search(self.typeDict['plotting2D'][0], self.input): return 'plotting2D'
        elif re.search(self.typeDict['differtiation'][0], self.input): return 'differtiation'
        elif re.search(self.typeDict['integration'][0], self.input): return 'integration'
        else: return 'evaluation'

    def isDefinition(self) -> bool:
        return bool(re.findall(r'=', self.input))

    def getEquation(self) -> str:
        if self.isDefinition():
            eq:str = re.split(r'=', self.input)[1]
            res: (tuple | str) = re.findall(self.typeDict[self.type][0], eq)[0]
        else:
            res: (tuple | str) = re.findall(self.typeDict[self.type][0], self.input)[0]
        if isinstance(res, tuple):
            return res[0]
        else:
            return res

    def getParametrs(self) -> (list | None):
        if self.isDefinition():
            eq:str = re.split(r'=', self.input)[1]
            res: (tuple | str) = re.findall(self.typeDict[self.type][0], eq)[0]
        else:
            res: (tuple | str) = re.findall(self.typeDict[self.type][0], self.input)[0]
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

    def plotter3d(self):
        eq = self.equation
        syms = get_symbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = get_symbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insert_par_before_div(eq)
        sympy_equation = simplify(eq)
        args: list = [x for x in list(set(syms02)) if x not in FUNCTIONS]
        numpy_equation = lambdify(args, sympy_equation)
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
            varDict[self.varName]=str(equation)
        self.additionalData['X'] = X
        self.additionalData['Y'] = Y
        return equation

    def plotter2d(self):
        eq = self.equation
        syms = get_symbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = get_symbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insert_par_before_div(eq)
        sympy_equation = simplify(eq)
        args: list = [x for x in list(set(syms02)) if x not in FUNCTIONS]
        numpy_equation = lambdify(args, sympy_equation)
        if self.parameters:
            x = linspace(self.parameters[0], self.parameters[1], int(self.parameters[2]))
        else:
            x = linspace(-100, 100, 10)
        self.additionalData['X'] = x
        equation = numpy_equation(x)
        if self.definition and self.varName:
            varDict[self.varName]=str(equation)
        return equation

    def differtiator(self):
        eq = self.equation
        syms = get_symbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = get_symbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insert_par_before_div(eq)
        d_ = simplify('x')
        equation = diff(simplify(eq), d_)
        if self.definition and self.varName:
            varDict[self.varName]=str(equation)
        return equation
        
    def integrator(self):
        eq = self.equation
        syms = get_symbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = get_symbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insert_par_before_div(eq)
        d_ = simplify('x')
        equation = integrate(simplify(eq), d_)
        if self.definition and self.varName:
            varDict[self.varName]=str(equation)
        return equation

    def evaluator(self) -> str:
        eq = self.equation
        syms = get_symbols(eq)
        varDict = type(self).varDict
        for i in syms:
            if i in varDict.keys() and i not in FUNCTIONS:
                eq = eq.replace(i, f'({str(varDict[i])})')
        syms02 = get_symbols(eq)
        for i in syms02:
            if i not in FUNCTIONS:
                exec(f"{i} = Symbol('{i}')")
        eq = insert_par_before_div(eq)
        equation = simplify(eq)
        if self.definition and self.varName:
            varDict[self.varName]=str(equation)
        return equation
    

    
if __name__=='__main__':
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
    a=0