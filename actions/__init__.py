class Action:
    name = None

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Action):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Action type")

        return self.name == other.name

    # https://docs.python.org/3.1/reference/datamodel.html?highlight=hash#object.__hash__
    # https://stackoverflow.com/questions/1608842/types-that-define-eq-are-unhashable
    # https://stackoverflow.com/questions/8705378/pythons-in-set-operator
    def __hash__(self):
        return id(self.name)
