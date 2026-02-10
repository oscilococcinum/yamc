from sympy import symbols, Eq, solve #type: ignore
from sympy.parsing.sympy_parser import (
    parse_expr,# standard_transformations,
#    implicit_multiplication_application, convert_xor
)
import re
from yamcsolve.PlotData import PlotData
from yamcsolve.Equation import Equation, NoneEquation
from yamcsolve.Equation import EqEvalType

#m = re.split(r'(?<![<>!]):?=', s_norm)
ASSIGN_REGEX: str = r'(?<![<>!]):='
SOLVE_REGEX: str = r'(?<![<>!])='

class SymPySolver:
    '''Singelton Solver object. It handles all solving and storing of app data'''
    def __init__(self) -> None:
        self._equations: dict[int, Equation] = {}
        self._varDict: dict[str, str] = {}
        self._plotData: dict[int, PlotData] = {}

    # Public
    def recomputeAll(self) -> None:
        pass

    def evalEq(self, id: int) -> None:
        self.updateVarDict()
        eq = self._equations[id]
        eqStream = eq.getStream()
        try:
            if len(re.split(ASSIGN_REGEX, eqStream)) == 2:
                self.assignSolve(eq, self._varDict)
            elif len(re.split(SOLVE_REGEX, eqStream)) == 2:
                pass
            else:
                self.evalSolve(eq, self._varDict)
        except Exception as e:
            print(f'recomputeEq failed due to: {e}')

    def addEquation(self, id: int, eq: str) -> None:
        newEq = Equation(eq)
        self._equations[id] = newEq
    
    def popEquation(self, id: int) -> None:
        try:
            self._equations.pop(id)
        except Exception as e:
            print(f'popEquation failed due to: {e}')

    def getFreeId(self) -> int:
        lastKey = len(self._equations.keys())
        return lastKey + 1

    def getPlotData(self, id: int) -> PlotData | None:
        pass

    def getEquation(self, id: int) -> Equation:
        try:
            return self._equations[id]
        except Exception as e:
            return NoneEquation(f'{e}')

    def getAllEquations(self) -> list[Equation]:
        return list(self._equations.values())

    def getAllEquationsStream(self) -> list[str]:
        return [i.getStream() for i in self._equations.values()]

    def updateVarDict(self) -> None:
        self._varDict.clear()
        for i in self._equations.values():
            varName = i.getMyVarName()
            if varName:
                self._varDict[varName] = i.getResultStream()

    # Static methods
    @staticmethod
    def assignSolve(eq: Equation, varDict: dict[str, str]) -> None:
        eq.setEvalType(EqEvalType.Assign)
        eqStream: str = eq.getStream()
        asSplit: list[str] = re.split(ASSIGN_REGEX, eqStream)
        lh = asSplit[0]
        rh = asSplit[1]
        eq.setMyVarName(lh)
        eq.setResultStream(parse_expr(rh, varDict, evaluate=True))

    @staticmethod
    def solveSolve(eq: Equation) -> None:
        pass

    @staticmethod
    def evalSolve(eq: Equation, varDict: dict[str, str]) -> None:
        eq.setEvalType(EqEvalType.Eval)
        eqStream: str = eq.getStream()
        eq.setResultStream(parse_expr(eqStream, varDict, evaluate=True))