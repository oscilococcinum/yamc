from enum import Enum, auto
from typing import Protocol


class EqEvalType(Enum):
    Eval = auto()
    Solve = auto()
    Assign = auto()
    NoEval = auto()

class VisType(Enum):
    Text = auto()
    Latex = auto()
    Plot = auto()

class EquationLike(Protocol):
    def getStream(self) -> str: ...
    def setEvalType(self, evalType: EqEvalType): ...
    def getEvalType(self) -> EqEvalType: ...
    def setVisType(self, visType: VisType) -> None: ...
    def getVisType(self) -> VisType: ...

class Equation:
    def __init__(self, eq: str) -> None:
        self._stream: str = eq
        self._evalType: EqEvalType = EqEvalType.Eval
        self._visType: VisType = VisType.Text

    # Public
    def getStream(self) -> str:
        return self._stream
    
    def setEvalType(self, evalType: EqEvalType):
        self._evalType = evalType

    def getEvalType(self) -> EqEvalType:
        return self._evalType

    def setVisType(self, visType: VisType) -> None:
        self._visType = visType

    def getVisType(self) -> VisType:
        return self._visType

class NoneEquation:
    '''Object that stores either empty equation or error'''
    def __init__(self, eqError: str) -> None:
        self._stream: str = eqError
        self._evalType: EqEvalType = EqEvalType.NoEval
        self._visType: VisType = VisType.Text

    # Public
    def getStream(self) -> str:
        return self._stream

    def setEvalType(self, evalType: EqEvalType):
        self._evalType = evalType

    def getEvalType(self) -> EqEvalType:
        return self._evalType

    def setVisType(self, visType: VisType) -> None:
        self._visType = visType

    def getVisType(self) -> VisType:
        return self._visType