from shelley.ast.events import EEvent
from shelley.parser.events import parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviours import parse as parse_behaviours
from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleEvent, TriggerRuleSequence, TriggerRuleChoice
from shelley.ast.components import Component
from .ledok import DLed
from .buttonok import DButton
from .timerok import DTimer


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
        behaviours = parse_behaviours(behaviours_str, i_events.union(e_events), actions)

        uses = set()
        uses.add(DLed.name)
        uses.add(DButton.name)
        uses.add(DTimer.name)

        components = {
            Component("ledA"): DLed.name,
            Component("ledB"): DLed.name,
            Component("b"): DButton.name,
            Component("t"): DTimer.name
        }

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

        triggers = dict()
        triggers[EEvent("begin")] = t_begin_rules
        triggers[EEvent("level1")]: t_level1_rules
        triggers[EEvent("level2")]: t_level2_rules
        triggers[EEvent("standby1")]: t_standby1_rules
        triggers[EEvent("standby2")]: t_standby2_rules

        super().__init__(self.name, actions, i_events, e_events, behaviours, uses, components, triggers)


def create_device_desk_lamp(d_led_a: Device, d_button: Device, d_timer: Device):
    return DDeskLamp(d_led_a, d_button, d_timer)
