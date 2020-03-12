from shelley.ast.events import EEvent, IEvent
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

        component_ledA = Component("ledA")
        component_ledB = Component("ledB")
        component_b = Component("b")
        component_t = Component("t")
        components = {
            component_ledA: DLed.name,
            component_ledB: DLed.name,
            component_b: DButton.name,
            component_t: DTimer.name
        }

        # Trigger rules for Desk Lamp
        # level1 <- b.pressed; b.released; ledA.on; t.started
        # level2 <- b.pressed; b.released; (t.canceled and ledB.on); t.started
        # standby1 <- t.timeout; ledB.off
        # standby2 <-
        #   ((b.pressed; b.released; t.canceled) xor t.timeout); (ledB.off and ledA.off)

        t_begin_rules = TriggerRuleSequence(
            TriggerRuleEvent(component_b, EEvent('begin')),
            TriggerRuleSequence(
                TriggerRuleEvent(component_ledA, EEvent('begin')),
                TriggerRuleSequence(
                    TriggerRuleEvent(component_ledB, EEvent('begin')),
                    TriggerRuleEvent(component_t, EEvent('begin')))))

        t_level1_rules = TriggerRuleSequence(
            TriggerRuleEvent(component_b, EEvent('pressed')),
            TriggerRuleSequence(
                TriggerRuleEvent(component_b, EEvent('released')),
                TriggerRuleSequence(
                    TriggerRuleEvent(component_ledA, IEvent('on')),
                    TriggerRuleEvent(component_t, IEvent('started')))))

        t_level2_rules = TriggerRuleSequence(
            TriggerRuleEvent(component_b, EEvent('pressed')),
            TriggerRuleSequence(
                TriggerRuleEvent(component_b, EEvent('released')),
                TriggerRuleSequence(
                    TriggerRuleChoice(
                        TriggerRuleSequence(
                            TriggerRuleEvent(component_t, IEvent('canceled')),
                            TriggerRuleEvent(component_ledB, IEvent('on'))
                        ),
                        TriggerRuleSequence(
                            TriggerRuleEvent(component_ledB, IEvent('on')),
                            TriggerRuleEvent(component_t, IEvent('canceled'))
                        )
                    ),
                    TriggerRuleEvent(component_t, IEvent('started'))
                )
            )
        )

        t_standby1_rules = TriggerRuleSequence(
            TriggerRuleEvent(component_t, EEvent('timeout')),
            TriggerRuleEvent(component_ledB, IEvent('off')))

        t_standby2_rules = TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleSequence(
                    TriggerRuleEvent(component_b, EEvent('pressed')),
                    TriggerRuleSequence(
                        TriggerRuleEvent(component_b, EEvent('released')),
                        TriggerRuleEvent(component_t, IEvent('canceled')))),
                TriggerRuleEvent(component_t, EEvent('timeout'))),

            TriggerRuleChoice(
                TriggerRuleSequence(
                    TriggerRuleEvent(component_ledB, IEvent('off')),
                    TriggerRuleEvent(component_ledA, IEvent('off'))
                ),
                TriggerRuleSequence(
                    TriggerRuleEvent(component_ledA, IEvent('off')),
                    TriggerRuleEvent(component_ledB, IEvent('off'))
                )))

        triggers = dict()
        triggers[EEvent("begin")] = t_begin_rules
        triggers[EEvent("level1")] = t_level1_rules
        triggers[EEvent("level2")] = t_level2_rules
        triggers[EEvent("standby1")] = t_standby1_rules
        triggers[EEvent("standby2")] = t_standby2_rules

        super().__init__(self.name, actions, i_events, e_events, behaviours, triggers, uses, components)


def create_device_desk_lamp(d_led_a: Device, d_button: Device, d_timer: Device):
    return DDeskLamp(d_led_a, d_button, d_timer)
