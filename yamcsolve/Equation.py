

class Equation:
    def __init__(self, eq: str) -> None:
        self._stream: str = eq

    # Public
    def getStream(self) -> str:
        return self._stream