import unittest
from unittest.mock import MagicMock
from components import Component
from components.checker import check, ComponentsListEmptyError, ComponentsListDuplicatedError, \
    ComponentsDeviceNotUsedError, ComponentsDeviceNotDeclaredError


class TestComponents(unittest.TestCase):
    def test_is_valid(self):
        uses_devices = ['Led', 'Button']

        device_led = MagicMock()
        device_led.name = 'Led'

        device_button = MagicMock()
        device_button.name = 'Button'

        declared_devices = {'Led': device_led, 'Button': device_button}

        ledA = Component(device_led, 'ledA')
        ledB = Component(device_led, 'ledB')
        button = Component(device_button, 'button')
        components = [ledA, ledB, button]
        original_len = len(components)

        result = check(components, uses_devices, declared_devices)

        self.assertEqual(original_len, len(result))

        self.assertTrue(ledA.name in result)
        self.assertTrue(ledB.name in result)
        self.assertTrue(button.name in result)
        self.assertFalse("timer" in result)

    def test_duplicated(self):
        uses_devices = ['Led', 'Button']

        device_led = MagicMock()
        device_led.name = 'Led'

        device_button = MagicMock()
        device_button.name = 'Button'

        declared_devices = {'Led': device_led, 'Button': device_button}

        ledA = Component(device_led, 'ledA')
        button = Component(device_button, 'button')
        components = [ledA, ledA, button]

        with self.assertRaises(ComponentsListDuplicatedError) as context:
            check(components, uses_devices, declared_devices)

    def test_empty(self):
        with self.assertRaises(ComponentsListEmptyError) as context:
            check([], [], {})

    def test_device_not_in_uses(self):
        uses_devices = ['Led']  # , 'Button']

        device_led = MagicMock()
        device_led.name = 'Led'

        device_button = MagicMock()
        device_button.name = 'Button'

        declared_devices = {'Led': device_led, 'Button': device_button}

        ledA = Component(device_led, 'ledA')
        button = Component(device_button, 'button')
        components = [ledA, button]

        with self.assertRaises(ComponentsDeviceNotUsedError) as context:
            check(components, uses_devices, declared_devices)
        self.assertEqual(str(context.exception), "Device type 'Button' must be in uses list!")

    def test_device_not_declared(self):
        uses_devices = ['Led', 'Button']

        device_led = MagicMock()
        device_led.name = 'Led'

        device_button = MagicMock()
        device_button.name = 'Button'

        declared_devices = {'Led': device_led}  # , 'Button': device_button}

        ledA = Component(device_led, 'ledA')
        ledB = Component(device_led, 'ledB')
        button = Component(device_button, 'button')
        components = [ledA, ledB, button]

        with self.assertRaises(ComponentsDeviceNotDeclaredError) as context:
            check(components, uses_devices, declared_devices)
        self.assertEqual(str(context.exception), "Device type 'Button' has not been declared!")


if __name__ == '__main__':
    unittest.main()
