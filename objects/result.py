class Result:
    
    def __init__(self):
        pass

    def __repr__(self):
        assert hasattr(self, "name"), "Результат без имени?"
        return self.name
    
    def __eq__(self, name):
        return self.name == name