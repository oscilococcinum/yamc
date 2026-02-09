from enum import Enum, auto


class EqEvalType(Enum):
    Eval = auto() # 25*a+19*b
    Solve = auto() # 35*x+8 = 5
    Assign = auto() # x:= 15*y
    NoEval = auto()

class VisType(Enum):
    Text = auto()
    Latex = auto()
    Plot = auto()

class Equation:
    def __init__(self, eq: str) -> None:
        self._evalType: EqEvalType = EqEvalType.Eval
        self._visType: VisType = VisType.Text
        self._stream: str = eq
        self._myVarName: str | None = None
        self._varsIDepOn: list[str] = []
        self._isDependent: bool = False
        self._hasCyclicDepInfo: bool = False
        self._isChanged: bool = False
        self._recalculationReq: bool = False

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

    def getMyVarName(self) -> str | None:
        return self._myVarName

    def getVarsIDepOn(self) -> list[str]:
        return self._varsIDepOn

    def setIsDependent(self, isDep: bool) -> None:
        self._isDependent = isDep

    def setHasCyclicDepInfo(self, hasCyclicDep: bool) -> None:
        self._hasCyclicDepInfo = hasCyclicDep

    def getHasCyclicDepInfo(self) -> bool:
        return self._hasCyclicDepInfo

    def getIsChanged(self) -> bool:
        return self._isChanged

    def setIsChanged(self, isChanged: bool) -> None:
        self._isChanged = isChanged

    def setRecalculationReq(self, recReq: bool) -> None:
        self._recalculationReq = recReq

    def getRecalculationReq(self) -> bool:
        return self._recalculationReq

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