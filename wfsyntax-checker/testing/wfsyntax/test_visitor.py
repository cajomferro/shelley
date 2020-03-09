import unittest
from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from ast.visitors import PrettyPrintVisitor, CheckWFSyntaxVisitor


class TestDevice(unittest.TestCase):

    def setUp(self) -> None:
        self.declared_devices = {}

        self.d_led = create_device_led()
        self.declared_devices[self.d_led.name] = self.d_led

        self.d_button = create_device_button()
        self.declared_devices[self.d_button.name] = self.d_button

        self.d_timer = create_device_timer()
        self.declared_devices[self.d_timer.name] = self.d_timer

        self.d_desk_lamp = create_device_desk_lamp(self.d_led, self.d_button, self.d_timer)

    def test_pretty_print(self):

        visitor = PrettyPrintVisitor()
        for device in [self.d_desk_lamp]:
            device.accept(visitor)
            print(visitor)

    #
    #         expected_str = """begin <- (b.begin  ; (ledA.begin  ; (ledB.begin  ; t.begin )))
    # level1 <- (b.pressed  ; (b.released  ; (ledA.on  ; t.started )))
    # level2 <- (b.pressed  ; (b.released  ; (t.canceled  ; t.started )))
    # standby1 <- (t.timeout  ; ledB.off )
    # standby2 <- (((b.pressed  ; (b.released  ; t.canceled )) xor t.timeout ) ; ((ledB.off  ; ledA.off ) xor (ledA.off  ; ledB.off )))
    # """
    #
    #         self.assertEqual(expected_str, visitor.result)

    def test_check_wf_syntax(self):
        visitor = CheckWFSyntaxVisitor(self.d_desk_lamp.uses, self.declared_devices)
        for device in [self.d_desk_lamp]:
            device.accept(visitor)

        # self.assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)


if __name__ == '__main__':
    unittest.main()
