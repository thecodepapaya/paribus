def error_object(status: int, message: str, details: str | None = None):
    response = {"error": message}
    if details:
        response["details"] = details
    return (response, status)


def success_object(message: str, status: int = 200, details: str | None = None):
    response = {"message": message}
    if details:
        response["details"] = details
    return (response, status)


class InvalidCsvException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"InvalidCsvException: {self.message}"
