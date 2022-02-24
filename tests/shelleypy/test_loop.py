import pytest
from pathlib import Path
from shelley.shelleypy.checker.checker import PyVisitor
from shelley.shelleypy.checker.checker import extract_node
from shelley.ast.visitors.shelley2lark import Shelley2Lark

app_v1_py = """
@claim("system check G (main -> F (main & END));")
@system(uses={"v": "Valve"})
class App:
    def __init__(self):
        self.v = Valve()

    @operation(initial=True, final=True, next=[])
    def main(self):
        for _ in range(10):
            self.v.on()
            wait()
            self.v.off()
        return ""
"""

def test_app_v1() -> None:
    """

    """

    svis = PyVisitor(external_only=False)
    svis.find(extract_node(app_v1_py))

    visitor = Shelley2Lark(components=svis.device.components)
    svis.device.accept(visitor)

    lark_code = visitor.result.strip()

    expected_lark_code = """
App (v: Valve) {
 initial final main ->  {
  loop {v.on; v.off; }
 }

}
""".strip()

    assert lark_code == expected_lark_code