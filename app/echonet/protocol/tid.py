class TransactionId:
    """トランザクションID"""

    @property
    def value(self) -> int:
        """値"""
        return self._value

    def __init__(self, value: int = 0x0000):
        self._value = value

    def increment(self):
        self._value = (self._value + 1) & 0xFFFF
