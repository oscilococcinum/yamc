from sympy import symbols, Eq, solve #type: ignore
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)
import re
from yamcsolve.PlotData import PlotData
from yamcsolve.Equation import Equation, NoneEquation
from yamcsolve.Equation import EqEvalType, VisType
from typing import Protocol

#m = re.split(r'(?<![<>!]):?=', s_norm)
ASSIGN_REGEX: str = r'(?<![<>!]):='
SOLVE_REGEX: str = r'(?<![<>!])='

class EquationLike(Protocol):
    def getStream(self) -> str: ...
    def setEvalType(self, evalType: EqEvalType): ...
    def getEvalType(self) -> EqEvalType: ...
    def setVisType(self, visType: VisType) -> None: ...
    def getVisType(self) -> VisType: ...
    def getMyVarName(self) -> str | None: ...
    def getVarsIDepOn(self) -> list[str]: ...
    def setIsDependent(self, isDep: bool) -> None: ...
    def setHasCyclicDepInfo(self, hasCyclicDep: bool) -> None: ...
    def getHasCyclicDepInfo(self) -> bool: ...
    def getIsChanged(self) -> bool: ...
    def setIsChanged(self, isChanged: bool) -> None: ...
    def setRecalculationReq(self, recReq: bool) -> None: ...
    def getRecalculationReq(self) -> bool: ...

def symPySolve(eq: EquationLike, varDict: dict[str, EquationLike]) -> EquationLike:
    eqStream: str = eq.getStream()
    #asSplit: list[str] = re.split(ASSIGN_REGEX, eqStream)
    #solSplit: list[str] = re.split(SOLVE_REGEX, eqStream)
    return(Equation(parse_expr(eqStream, varDict)))

class SymPySolver:
    '''Singelton Solver object. It handles all solving and storing of app data'''
    def __init__(self) -> None:
        self._equations: dict[int, EquationLike] = {}
        self._results: dict[int, EquationLike] = {}
        self._varDict: dict[str, EquationLike] = {}
        self._plotData: dict[int, PlotData] = {}

    # Public
    def recomputeAll(self) -> None:
        pass

    def evalEq(self, id: int) -> None:
        try:
            eq = self._equations[id]
            self._results[id] = symPySolve(eq)
        except Exception as e:
            print(f'recomputeEq failed due to: {e}')

    def addEquation(self, id: int, eq: str) -> None:
        newEq = Equation(eq)
        self._equations[id] = newEq
    
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