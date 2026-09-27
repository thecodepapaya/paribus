def error_object(status: int, message: str, details: str | None = None):
    response = {"error": message}
    if details:
        response["details"] = details
    return (response, status)


def success_object(status: int, message: str, details: str | None = None):
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


class MaxCsvLimitException(Exception):
    def __init__(self, count):
        self.message = f"Max allowed 20 entries, uploaded {count} entries in CSV"
        self.count = count
        super().__init__(self.message)

    def __str__(self):
        return f"MaxCsvLimitException: {self.message}"
