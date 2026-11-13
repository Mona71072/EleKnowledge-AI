"""Error type shared by the input and output validators of the rewrite Lambda."""


class ApiError(Exception):
    """An error that maps to one HTTP status and the unified {error, message} envelope."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(code)
        self.status = status
        self.code = code
        self.message = message
