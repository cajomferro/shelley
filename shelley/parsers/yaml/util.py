from yaml.constructor import SafeConstructor

from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.composer import *
from yaml.resolver import *


# Create custom safe constructor class that inherits from SafeConstructor
class MySafeConstructor(SafeConstructor):
    bool_values = {
        "yes": "yes",
        "no": "no",
        "true": True,
        "false": False,
        "on": "on",
        "off": "off",
    }

    # Create new method handle boolean logic
    def add_bool(self, node):
        value = self.construct_scalar(node)
        return self.bool_values[value.lower()]


# Inject the above boolean logic into the custom constuctor
MySafeConstructor.add_constructor("tag:yaml.org,2002:bool", MySafeConstructor.add_bool)  # type: ignore


class MySafeLoader(Reader, Scanner, Parser, Composer, MySafeConstructor, Resolver):
    def __init__(self, stream) -> None:
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        MySafeConstructor.__init__(self)
        Resolver.__init__(self)
