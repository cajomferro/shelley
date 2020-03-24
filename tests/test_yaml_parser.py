import yaml
from shelley.ast.events import EEvent, EEvents
from shelley.ast.actions import Actions
from shelley.ast.behaviors import Behaviors
from shelley.ast.devices import Device
from shelley.ast.triggers import Triggers


def test_read_and_print():
    with open('input/example.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)

    print(yaml_code)

    device_name = yaml_code['device']['name']
    device_events = yaml_code['device']['events']
    device_behavior = yaml_code['device']['behavior']
    device_components = yaml_code['device']['components']
    device_triggers = yaml_code['device']['triggers']

    assert device_name == 'DeskLamp'
    assert device_events == ['level1', 'level2', 'standby1', 'standby2']
    assert device_behavior == [['begin', 'level1'], ['level1', 'level2']]
    assert device_components == {'ledA': 'Led', 'ledB': 'Led', 'b': 'Button', 't': 'Timer'}
    assert device_triggers == {'standby1': [{'xor': [['b.press', 'b.release', 't.cancelled'], 't.timeout']},
                                            {'xor': [['ledA.off', 'ledB.off'], ['ledB.off', 'ledA.of']]}]}


def create_device_from_yaml(yaml_code) -> Device:
    try:
        device_name = yaml_code['device']['name']
    except KeyError:
        raise Exception("Device must have a name")

    try:
        device_events = yaml_code['device']['events']
    except KeyError:
        raise Exception("Device must have events")

    try:
        device_behavior = yaml_code['device']['behavior']
    except KeyError:
        raise Exception("Device must have a behavior")

    try:
        device_components = yaml_code['device']['components']
    except KeyError:
        device_components = dict()

    try:
        device_triggers = yaml_code['device']['triggers']
    except KeyError:
        device_triggers = dict()

    events: EEvents = EEvents()
    for event_name in device_events:
        events.add(EEvent(event_name))

    behaviors: Behaviors = Behaviors()
    for beh_transition in device_behavior:
        left = beh_transition[0]
        right = beh_transition[1]
        e1 = events.find_by_name(left)
        e2 = events.find_by_name(right)
        behaviors.create(e1, e2)

    return Device(device_name, Actions(), EEvents(), events, behaviors, Triggers())


def test_create_button():
    with open('input/buttonok.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)

    shelley_device = create_device_from_yaml(yaml_code)

    assert shelley_device.name == 'Button'
    assert shelley_device.get_all_events().list_str() == ['pressed', 'released']
    assert shelley_device.behaviors.list_str() == ['pressed -> released', 'released -> pressed']
