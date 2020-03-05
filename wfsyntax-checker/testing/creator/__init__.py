from ast.events import EEvent
from parser.events import parse as parse_events
from parser.actions import parse as parse_actions
from parser.behaviours import parse as parse_behaviours
from ast.devices import Device
from ast.triggers import Trigger
from ast.rules import TriggerRuleEvent, TriggerRuleSequence, TriggerRuleChoice
from ast.components import Component


class DLed(Device):
    name = 'LED'

    def __init__(self):
        i_events, e_events = parse_events('internal on,internal off,external begin')

        actions = parse_actions("turnOn,turnOff")

        behaviours_str = "begin -> turnOn() on,on -> turnOff() off,off -> turnOn() on"

        behaviours = parse_behaviours(behaviours_str, i_events + e_events, actions)

        super().__init__(self.name, actions, i_events, e_events, behaviours)


class DButton(Device):
    name = 'Button'

    def __init__(self):
        i_events, e_events = parse_events('external begin, external pressed,external released')
        actions = parse_actions("")

        behaviours_str = "begin -> pressed,pressed -> released,released -> pressed"

        behaviours = parse_behaviours(behaviours_str, i_events + e_events, actions)

        super().__init__(self.name, actions, i_events, e_events, behaviours)


class DTimer(Device):
    name = 'Timer'

    def __init__(self):
        i_events, e_events = parse_events("external begin, internal started, internal canceled, external timeout")
        actions = parse_actions("start,cancel")

        behaviours_str = """begin -> start() started
            started -> cancel() canceled
            started -> timeout
            canceled -> start() started
            timeout -> start() started"""

        behaviours = parse_behaviours(behaviours_str, i_events + e_events, actions)

        super().__init__(self.name, actions, i_events, e_events, behaviours)


class DDeskLamp(Device):
    name = 'DeskLamp'

    def __init__(self, led: DLed, button: DButton, timer: DTimer):
        i_events, e_events = parse_events(
            "external begin, external level1, external level2, external standby1, external standby2")
        actions = parse_actions("")

        behaviours_str = \
            """
            begin -> level1
            level1 -> standby1
            level1 -> level2
            level2 -> standby2
            standby1 -> level1
            standby2 -> level1
            """

        behaviours = parse_behaviours(behaviours_str, i_events + e_events, actions)

        uses = [DLed.name, DButton.name, DTimer.name]

        components = [
            Component(led, "ledA"),
            Component(led, "ledB"),
            Component(button, "b"),
            Component(timer, "t")
        ]

        # Trigger rules for Desk Lamp
        # level1 <- b.pressed; b.released; ledA.on; t.started
        # level2 <- b.pressed; b.released; (t.canceled and ledB.on); t.started
        # standby1 <- t.timeout; ledB.off
        # standby2 <-
        #   ((b.pressed; b.released; t.canceled) xor t.timeout); (ledB.off and ledA.off)

        t_begin_rules = TriggerRuleSequence(
            TriggerRuleEvent("b", "begin"),
            TriggerRuleSequence(
                TriggerRuleEvent("ledA", "begin"),
                TriggerRuleSequence(
                    TriggerRuleEvent("ledB", "begin"),
                    TriggerRuleEvent("t", "begin"))))

        t_level1_rules = TriggerRuleSequence(
            TriggerRuleEvent("b", "pressed"),
            TriggerRuleSequence(
                TriggerRuleEvent("b", "released"),
                TriggerRuleSequence(
                    TriggerRuleEvent("ledA", "on"),
                    TriggerRuleEvent("t", "started"))))

        t_level2_rules = TriggerRuleSequence(
            TriggerRuleEvent("b", "pressed"),
            TriggerRuleSequence(
                TriggerRuleEvent("b", "released"),
                TriggerRuleSequence(
                    TriggerRuleEvent("t", "canceled"),  # TODO: AND? or GROUP? is not working for valid reduction!!!
                    #                    TriggerRuleGroup(
                    #                        TriggerRuleAnd(
                    #                            TriggerRuleEvent("t", "canceled"),
                    #                            TriggerRuleEvent("ledB", "on"))),
                    TriggerRuleEvent("t", "started"))))

        t_standby1_rules = TriggerRuleSequence(
            TriggerRuleEvent("t", "timeout"),
            TriggerRuleEvent("ledB", "off"))

        t_standby2_rules = TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleSequence(
                    TriggerRuleEvent("b", "pressed"),
                    TriggerRuleSequence(
                        TriggerRuleEvent("b", "released"),
                        TriggerRuleEvent("t", "canceled"))),
                TriggerRuleEvent("t", "timeout")),

            TriggerRuleChoice(
                TriggerRuleSequence(
                    TriggerRuleEvent("ledB", "off"),
                    TriggerRuleEvent("ledA", "off")
                ),
                TriggerRuleSequence(
                    TriggerRuleEvent("ledA", "off"),
                    TriggerRuleEvent("ledB", "off")
                )))

        triggers = [Trigger(EEvent("begin"), t_begin_rules),
                    Trigger(EEvent("level1"), t_level1_rules),
                    Trigger(EEvent("level2"), t_level2_rules),
                    Trigger(EEvent("standby1"), t_standby1_rules),
                    Trigger(EEvent("standby2"), t_standby2_rules)]

        super().__init__(self.name, actions, i_events, e_events, behaviours, uses, components, triggers)


# class DDeskLampDuplicatedTrigger(Device):
#     name = 'DeskLamp'
#
#     def __init__(self, led: DLed, button: DButton, timer: DTimer):
#         i_events, e_events = parse_events(
#             "external begin, external level1, external level2, external standby1, external standby2")
#         actions = parse_actions("")
#
#         behaviours_str = \
#             """
#             begin -> level1
#             level1 -> standby1
#             level1 -> level2
#             level2 -> standby2
#             standby1 -> level1
#             standby2 -> level1
#             """
#
#         behaviours = parse_behaviours(behaviours_str, i_events + e_events, actions)
#
#         uses = [DLed.name, DButton.name, DTimer.name]
#
#         components = [
#             Component(led, "ledA"),
#             Component(led, "ledB"),
#             Component(button, "b"),
#             Component(timer, "t")
#         ]
#
#         t_begin_rules = TriggerRuleSequence(
#             TriggerRuleEvent("b", "begin"),
#             TriggerRuleSequence(
#                 TriggerRuleEvent("ledA", "begin"),
#                 TriggerRuleSequence(
#                     TriggerRuleEvent("ledB", "begin"),
#                     TriggerRuleEvent("t", "begin"))))
#
#         t_level1_rules = TriggerRuleSequence(
#             TriggerRuleEvent("b", "pressed"),
#             TriggerRuleSequence(
#                 TriggerRuleEvent("b", "released"),
#                 TriggerRuleSequence(
#                     TriggerRuleEvent("ledA", "on"),
#                     TriggerRuleEvent("t", "started"))))
#
#         t_level2_rules = TriggerRuleSequence(
#             TriggerRuleEvent("b", "pressed"),
#             TriggerRuleSequence(
#                 TriggerRuleEvent("b", "released"),
#                 TriggerRuleSequence(
#                     TriggerRuleGroup(
#                         TriggerRuleAnd(
#                             TriggerRuleEvent("t", "canceled"),
#                             TriggerRuleEvent("ledB", "on"))),
#                     TriggerRuleEvent("t", "started"))))
#
#         t_standby1_rules = TriggerRuleSequence(
#             TriggerRuleEvent("t", "timeout"),
#             TriggerRuleEvent("ledB", "off"))
#
#         t_standby2_rules = TriggerRuleSequence(
#             TriggerRuleGroup(
#                 TriggerRuleChoice(
#                     TriggerRuleGroup(
#                         TriggerRuleSequence(
#                             TriggerRuleEvent("b", "pressed"),
#                             TriggerRuleSequence(
#                                 TriggerRuleEvent("b", "released"),
#                                 TriggerRuleEvent("t", "canceled")))),
#                     TriggerRuleEvent("t", "timeout"))),
#             TriggerRuleGroup(
#                 TriggerRuleAnd(
#                     TriggerRuleEvent("ledB", "off"),
#                     TriggerRuleEvent("ledA", "off"))))
#
#         triggers = [Trigger(EEvent("begin"), t_begin_rules),
#                     Trigger(EEvent("level1"), t_level1_rules),
#                     Trigger(EEvent("level1"), t_level2_rules),  # TEST HERE
#                     Trigger(EEvent("standby1"), t_standby1_rules),
#                     Trigger(EEvent("standby2"), t_standby2_rules)]
#
#         super().__init__(self.name, [], [], e_events, behaviours, uses, components, triggers)
#
#
# class DDeskLampViolatesLedA(Device):
#     name = 'DeskLamp'
#
#     def __init__(self, led: DLed, button: DButton, timer: DTimer):
#         i_events, e_events = parse_events(
#             "external begin, external level1, external level2, external standby1, external standby2")
#         actions = parse_actions("")
#
#         behaviours_str = \
#             """
#             begin -> level1
#             level1 -> standby1
#             level1 -> level2
#             level2 -> standby2
#             standby1 -> level1
#             standby2 -> level1
#             """
#
#         behaviours = parse_behaviours(behaviours_str, i_events + e_events, actions)
#
#         uses = [DLed.name, DButton.name, DTimer.name]
#
#         components = [
#             Component(led, "ledA"),
#             Component(led, "ledB"),
#             Component(button, "b"),
#             Component(timer, "t")
#         ]
#
#         t_begin_rules = TriggerRuleSequence(
#             TriggerRuleEvent("b", "begin"),
#             TriggerRuleSequence(
#                 TriggerRuleEvent("ledA", "begin"),
#                 TriggerRuleSequence(
#                     TriggerRuleEvent("ledB", "begin"),
#                     TriggerRuleEvent("t", "begin"))))
#
#         t_level1_rules = TriggerRuleSequence(
#             TriggerRuleEvent("b", "pressed"),
#             TriggerRuleSequence(
#                 TriggerRuleEvent("b", "released"),
#                 TriggerRuleSequence(
#                     TriggerRuleEvent("ledA", "off"),  # TEST HERE -> after ledA.begin should be ledA.on!
#                     TriggerRuleEvent("t", "started"))))
#
#         t_level2_rules = TriggerRuleSequence(
#             TriggerRuleEvent("b", "pressed"),
#             TriggerRuleSequence(
#                 TriggerRuleEvent("b", "released"),
#                 TriggerRuleSequence(
#                     TriggerRuleGroup(
#                         TriggerRuleAnd(
#                             TriggerRuleEvent("t", "canceled"),
#                             TriggerRuleEvent("ledB", "on"))),
#                     TriggerRuleEvent("t", "started"))))
#
#         t_standby1_rules = TriggerRuleSequence(
#             TriggerRuleEvent("t", "timeout"),
#             TriggerRuleEvent("ledB", "off"))
#
#         t_standby2_rules = TriggerRuleSequence(
#             TriggerRuleGroup(
#                 TriggerRuleChoice(
#                     TriggerRuleGroup(
#                         TriggerRuleSequence(
#                             TriggerRuleEvent("b", "pressed"),
#                             TriggerRuleSequence(
#                                 TriggerRuleEvent("b", "released"),
#                                 TriggerRuleEvent("t", "canceled")))),
#                     TriggerRuleEvent("t", "timeout"))),
#             TriggerRuleGroup(
#                 TriggerRuleAnd(
#                     TriggerRuleEvent("ledB", "off"),
#                     TriggerRuleEvent("ledA", "off"))))
#
#         triggers = [Trigger(EEvent("begin"), t_begin_rules),
#                     Trigger(EEvent("level1"), t_level1_rules),
#                     Trigger(EEvent("level2"), t_level2_rules),
#                     Trigger(EEvent("standby1"), t_standby1_rules),
#                     Trigger(EEvent("standby2"), t_standby2_rules)]
#
#         super().__init__(self.name, [], [], e_events, behaviours, uses, components, triggers)


def create_device_led():
    return DLed()


def create_device_button():
    return DButton()


def create_device_timer():
    return DTimer()


def create_device_desk_lamp(d_led_a: Device, d_button: Device, d_timer: Device):
    return DDeskLamp(d_led_a, d_button, d_timer)

# def create_device_desk_lamp_duplicated_trigger(d_led_a: Device, d_button: Device, d_timer: Device):
#     return DDeskLampDuplicatedTrigger(d_led_a, d_button, d_timer)
#
#
# def create_device_desk_lamp_violates_led_a(d_led_a: Device, d_button: Device, d_timer: Device):
#     return DDeskLampViolatesLedA(d_led_a, d_button, d_timer)
