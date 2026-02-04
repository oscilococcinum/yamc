from yamcsolve.SymPySolver import SymPySolver

def testSolving(eqList: list[str], resList: list[str]) -> None:
    testSolver: SymPySolver = SymPySolver()
    for i, j in zip(eqList, resList):
        id: int | None = testSolver.addEquation(i)
        assert id is int
        try:
            testSolver.recomputeEq(id)
            rEq: str = testSolver.getResult(id).getStream()
            print(f'{j == rEq}')
        except:
            print('No equation or result for this id')

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
    testSolving(equations, results)