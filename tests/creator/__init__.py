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


# def create_device_desk_lamp_duplicated_trigger(d_led_a: Device, d_button: Device, d_timer: Device):
#     return DDeskLampDuplicatedTrigger(d_led_a, d_button, d_timer)
#
#
# def create_device_desk_lamp_violates_led_a(d_led_a: Device, d_button: Device, d_timer: Device):
#     return DDeskLampViolatesLedA(d_led_a, d_button, d_timer)
