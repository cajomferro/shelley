import unittest

from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp, \
    create_device_desk_lamp_violates_led_a
from testing.creator import create_device_desk_lamp_duplicated_trigger
from _local.devices import check as check_device, DeviceInvalidTriggerRuleReduction
from triggers.checker import TriggersListDuplicatedError


class TestDevices(unittest.TestCase):
    def test_desk_lamp_valid(self):
        declared_devices = {}

        d_led = create_device_led()
        check_device(d_led, {}, is_composite=False)
        declared_devices[d_led.name] = d_led

        d_button = create_device_button()
        check_device(d_button, declared_devices, is_composite=False)
        declared_devices[d_button.name] = d_button

        d_timer = create_device_timer()
        check_device(d_timer, declared_devices, is_composite=False)
        declared_devices[d_timer.name] = d_timer

        d_desk_lamp = create_device_desk_lamp(d_led, d_button, d_timer)
        check_device(d_desk_lamp, declared_devices, is_composite=True)

    def test_desk_lamp_dup_trigger(self):
        declared_devices = {}

        d_led = create_device_led()
        check_device(d_led, {}, is_composite=False)
        declared_devices[d_led.name] = d_led

        d_button = create_device_button()
        check_device(d_button, declared_devices, is_composite=False)
        declared_devices[d_button.name] = d_button

        d_timer = create_device_timer()
        check_device(d_timer, declared_devices, is_composite=False)
        declared_devices[d_timer.name] = d_timer

        d_desk_lamp = create_device_desk_lamp_duplicated_trigger(d_led, d_button, d_timer)
        with self.assertRaises(TriggersListDuplicatedError) as context:
            check_device(d_desk_lamp, declared_devices, is_composite=True)

    def test_desk_lamp_violates_ledA(self):
        declared_devices = {}

        d_led = create_device_led()
        check_device(d_led, {}, is_composite=False)
        declared_devices[d_led.name] = d_led

        d_button = create_device_button()
        check_device(d_button, declared_devices, is_composite=False)
        declared_devices[d_button.name] = d_button

        d_timer = create_device_timer()
        check_device(d_timer, declared_devices, is_composite=False)
        declared_devices[d_timer.name] = d_timer

        d_desk_lamp = create_device_desk_lamp_violates_led_a(d_led, d_button, d_timer)
        with self.assertRaises(DeviceInvalidTriggerRuleReduction) as context:
            check_device(d_desk_lamp, declared_devices, is_composite=True)

        self.assertEqual(str(context.exception), "Invalid behaviour: ledA.begin -> ledA.off")


if __name__ == '__main__':
    unittest.main()
