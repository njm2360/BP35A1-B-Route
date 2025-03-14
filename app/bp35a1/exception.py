class BP35A1Exception(Exception):
    def __init__(self, message: str, code: str = None):
        self.code = code
        self.message = message
        super().__init__(f"Error {self.code}: {self.message}")


class TxProhibisionError(BP35A1Exception):
    def __init__(self):
        super().__init__(message="Transmit prohibition error.")


class PANAConnectError(BP35A1Exception):
    def __init__(self):
        super().__init__(message="PANA connect error.")


class CommandError(BP35A1Exception):
    def __init__(self, code: str):
        match code:
            case "ER04":
                message = "The specified command is not supported."
            case "ER05":
                message = (
                    "The number of arguments for the specified command is incorrect."
                )
            case "ER06":
                message = "The argument format or value range for the specified command is incorrect."
            case "ER09":
                message = "A UART input error has occurred."
            case "ER10":
                message = "The specified command was accepted, but the execution result failed."
            case _:
                message = "Unknown command error."

        super().__init__(message=message, code=code)
