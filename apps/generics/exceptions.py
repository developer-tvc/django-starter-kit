class NotAllowedError(Exception):
    def __init__(self, message="You are not allowed to perform this operation."):
        self.message = message
        super().__init__(self.message)


class ExistsError(Exception):
    def __init__(self, message="This data already exists."):
        self.message = message
        super().__init__(self.message)


class NotExistsError(Exception):
    def __init__(self, message="This data does not exist."):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    def __init__(self, message="You are not allowed to perform this operation."):
        self.message = message
        super().__init__(self.message)
