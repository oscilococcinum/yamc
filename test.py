from yamcsolve.SymPySolver import SymPySolver
from yamcsolve.ActiveSolvers import ActiveSolver


def testSolving(solver: SymPySolver, eqList: list[str], resList: list[str]) -> None:
    testSolver: SymPySolver = solver
    for i, j in zip(eqList, resList):
        id: int = testSolver.addEquation(i)
        testSolver.evalEq(id)
        rEq: str = testSolver.getResult(id).getStream()
        print(f'{j == rEq}')

if __name__ == '__main__':
    equations = [
      "x + 5 - 12",
      "2*x - 14",
      "x - 3 - 9",
      "4*x + 2 - 18"
    ]
    results = [
      "x - 7",
      "2*x - 14",
      "x - 12",
      "4*x - 16"
    ]
    testSolving(ActiveSolver, equations, results)

    print(ActiveSolver.getAllEquationsStream())
    