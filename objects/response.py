class Response:

    def __init__(self):
        pass

    def __repr__(self):
        assert hasattr(self, "name"), "Ответ дан анонимно"
        return self.name