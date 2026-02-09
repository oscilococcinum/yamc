from sympy import symbols, Eq, solve #type: ignore
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)
import re
from yamcsolve.PlotData import PlotData
from yamcsolve.Equation import EquationLike, Equation, NoneEquation


# Parser setup to support "2x", "x^2", "sin x"
TRANSFORMS = (
    standard_transformations
    + (implicit_multiplication_application, convert_xor)
)

def parse_side(text, local_dict=None):
    """Parse one side of an equation or a standalone expression."""
    return parse_expr(text, transformations=TRANSFORMS, local_dict=local_dict or {})

def parse_equation_or_expr(s: str, local_dict=None):
    """
    Returns (expr_or_eq, var_candidates).
    - If 's' contains '=', returns Eq(lhs, rhs).
    - Else returns a plain Expr (to be interpreted as expr == 0 if solving).
    """
    # Normalize whitespace
    s_norm = s.strip()

    # Split on a single '=' that is not part of '>=', '<=', '!=', ':='.
    # (If you plan to support inequalities, extend this.)
    # We also allow ':=' for definitions; we still treat it as an equation here.
    m = re.split(r'(?<![<>!]):?=', s_norm)
    if len(m) == 2:
        lhs_text, rhs_text = m[0].strip(), m[1].strip()
        lhs = parse_side(lhs_text, local_dict)
        rhs = parse_side(rhs_text, local_dict)
        return Eq(lhs, rhs), (lhs.free_symbols | rhs.free_symbols)
    else:
        expr = parse_side(s_norm, local_dict)
        return expr, expr.free_symbols

def solve_from_string(s: str, var: str | None = None, local_dict: dict | None = None):
    """
    Solve from a string. Examples:
      - 'x^2 = 4' with var='x'
      - 'x^2 - 4' with var='x' (interpreted as x^2 - 4 = 0)
    If var is None and exactly one symbol is present, that symbol is used.
    """
    obj, symset = parse_equation_or_expr(s, local_dict)

    # Choose variable
    if var is not None:
        x = symbols(var) if isinstance(var, str) else var
        vars_ = [x]
    else:
        if len(symset) == 1:
            vars_ = [next(iter(symset))]
        else:
            # Let solve infer, but it's better to require a var in multi-symbol cases
            vars_ = list(symset)

    # Build equation if we got a plain expression
    if not isinstance(obj, Eq):
        # interpret as obj = 0
        eq = Eq(obj, 0)
    else:
        eq = obj

    # If exactly one variable, call solve(eq, var); else solve(eq)
    if len(vars_) == 1:
        return solve(eq, vars_[0])
    else:
        return solve(eq)

class SymPySolver:
    '''Singelton Solver object. It handles all solving and storing of app data'''
    def __init__(self) -> None:
        self._equations: dict[int, Equation] = {}
        self._results: dict[int, Equation] = {}
        self._plotData: dict[int, PlotData] = {}

    # Public
    def recomputeAll(self) -> None:
        pass

    def evalEq(self, id: int) -> None:
        try:
            eq = self._equations[id].getStream()
            self._results[id] = Equation(symPySolve(eq))
        except Exception as e:
            print(f'recomputeEq failed due to: {e}')

    def addEquation(self, id: int, eq: str) -> None:
        self._equations[id] = Equation(eq)
    
    def getFreeId(self) -> int:
        lastKey = len(self._equations.keys())
        return lastKey + 1

    def popEquation(self, id: int) -> None:
        try:
            self._equations.pop(id)
            self._results.pop(id)
        except Exception as e:
            print(f'popEquation failed due to: {e}')

    def getPlotData(self, id: int) -> PlotData | None:
        pass

    def getEquation(self, id: int) -> EquationLike:
        try:
            return self._equations[id]
        except Exception as e:
            return NoneEquation(f'{e}')

    def getResult(self, id: int) -> EquationLike:
        try:
            return self._results[id]
        except Exception as e:
            return NoneEquation(f'{e}')
        
    def getAllEquations(self) -> list[EquationLike]:
        return list(self._equations.values())

    def getAllEquationsStream(self) -> list[str]:
        return [i.getStream() for i in self._equations.values()]