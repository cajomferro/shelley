import pytest
from pathlib import Path
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
    CheckedDevice,
    check_traces,
)
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley import yaml2shelley
from shelley.shelleyc import DeviceMapping
from shelley.shelleyc import CompilationError

httpclient_yml = """
device:
  name: HTTPClient
  behavior:
    - [connected, get]  # client.connect(host, port)) succeeded
    - [connected, post]  # client.connect(host, port)) succeeded
    - [connected, connect_failed]  # !client.connect(host, port))
    - [connect_failed, connected]
    - [get, response200]
    - [get, response404]
    - [get, response401]
    - [get, response500]
    - [post, response200]
    - [post, response404]
    - [post, response401]
    - [post, response500]
    - [response200, get]
    - [response200, post]
    - [response200, disconnected]
    - [response404, get]
    - [response404, disconnected]
    - [response404, post]
    - [response401, get]
    - [response401, disconnected]
    - [response401, post]
    - [response500, get]
    - [response500, disconnected]
    - [response500, post]
    - [disconnected, connected]
"""

wificlient_yml = """
device:
  name: WiFiClient
  events:
    - ssid_joined:
        start: True
    - ssid_failed:
        start: True
  behavior:
    - [connection_timeout, connected]
    - [ssid_joined, connected]
    - [ssid_joined, ssid_left]
    - [ssid_left, ssid_joined]
    - [ssid_left, ssid_failed]
    - [ssid_failed, ssid_failed]
    - [ssid_failed, ssid_joined]
    - [connected, disconnected]
    - [connected, print_timeout]
    - [connected, print_data_ready]
    - [print_data_ready, print_data_ready]
    - [print_timeout, print_timeout]
    - [print_data_ready, disconnected]
    - [print_timeout, disconnected]
    - [disconnected, connected]
    - [disconnected, connection_timeout]
    - [disconnected, ssid_left]
"""

wifihttp_yml = """
device:
  name: WiFiHTTP
  components:
      hc: HTTPClient
      wc: WiFiClient
  events:
    - started:
        start: True
        micro: [wc.ssid_joined, wc.connected, hc.connected]
    - notconnected:
        start: True
        micro:
          xor:
            - [wc.ssid_joined, wc.connected, hc.connect_failed]
            - xor:
              - [wc.ssid_joined, wc.connection_timeout]
              - [wc.ssid_failed]
    - send:
        micro:
          xor:
            - hc.get
            - hc.post
    - ok:
        micro: [wc.print_data_ready, hc.response200]
    - error:
        micro:
          xor:
            - [wc.print_data_ready, hc.response401]
            - xor:
              - [wc.print_data_ready, hc.response401]
              - xor:
                - [wc.print_data_ready, hc.response404]
                - xor:
                  - [wc.print_data_ready, hc.response500]
                  - wc.print_timeout
    - stopped:
        micro: [wc.disconnected, hc.disconnected, wc.ssid_left]
  behavior:
    - [started, send]
    - [notconnected, started]
    - [send, stopped]
    - [send, ok]
    - [send, error]
    - [error, send]
    - [ok, send]
    - [ok, stopped]
    - [error, stopped]
    - [stopped, started]
    - [stopped, notconnected]
"""


def _get_wifi_client_assembled() -> AssembledDevice:
    wificlient_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        wificlient_yml
    )
    wificlient_aut: AutomataDevice = shelley2automata.shelley2automata(wificlient_shy)

    return AssembledDevice.make(
        wificlient_aut, DeviceMapping(dict(), False).__getitem__
    )


def _get_http_client_assembled() -> AssembledDevice:
    httpclient_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        httpclient_yml
    )
    httpclient_aut: AutomataDevice = shelley2automata.shelley2automata(httpclient_shy)

    return AssembledDevice.make(
        httpclient_aut, DeviceMapping(dict(), False).__getitem__
    )


httpclient_assembled = _get_http_client_assembled()
wificlient_assembled = _get_wifi_client_assembled()


def test_compile_httpclient() -> None:
    assert httpclient_assembled.is_valid
    assert type(httpclient_assembled.external) == CheckedDevice


def test_compile_wificlient() -> None:
    assert wificlient_assembled.is_valid
    assert type(wificlient_assembled.external) == CheckedDevice


def test_compile_wifihttp() -> None:

    known_devices = {
        "HTTPClient": httpclient_assembled.external,
        "WiFiClient": wificlient_assembled.external,
    }

    wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(wifihttp_yml)
    wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

    wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices.__getitem__)

    # TODO: assert wifihttp_assembled.is_valid
    assert type(wifihttp_assembled.external) == CheckedDevice


def test_compile_wifihttp_no_known_devices() -> None:
    wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(wifihttp_yml)
    wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

    with pytest.raises(CompilationError) as exc_info:
        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, DeviceMapping(dict(), False).__getitem__
        )

    assert "Error loading system 'HTTPClient': system not defined" == str(
        exc_info.value
    )


def empty_devices(name: str) -> CheckedDevice:
    raise ValueError()


yaml_button = """
device:
  name: Button
  events: [pressed,released]
  behavior:
    - [pressed, released]
    - [released, pressed]

test_macro:
  ok:
    valid1: [pressed, released, pressed, released, pressed, released, pressed, released]
    valid2: [pressed]
    valid3: [pressed, released]
    valid4: [pressed, released, pressed]
    empty: []
  fail:
    invalid1: [released, pressed]
    invalid2: [released]"""

yaml_smartbutton = """
device:
  name: SmartButton
  components:
    b: Button
  events:
    - on:
        start: True
        final: True
        micro: [ b.pressed, b.released]
  behavior:
    - [on, on]


test_macro:
  ok:
    valid1: [on]
    valid2: [on, on, on, on]
  fail:
    invalid1: False
    empty: []

test_micro:
  ok:
    valid1: [b.pressed, b.released]
    valid2: [b.pressed, b.released, b.pressed, b.released]
    valid3: [b.pressed, b.released, b.pressed, b.released]
  fail:
    invalid1: [b.released, b.pressed] # wrong order
    invalid2: [b.pressed, b.pressed] # violates sequence
    invalid3: [b.released, b.released] # violates sequence
    incomplete1: [b.released] # incomplete (not a final state)
    incomplete2: [b.pressed] # incomplete (not a final state)
    incomplete3: [b.pressed, b.released, b.pressed] # incomplete (not a final state)
    empty: []
"""

yaml_led = """
device:
  name: Led
  events: [on, off] # on is start event
  behavior:
    - [on, off]
    - [off, on]"""

yaml_timer = """
device:
  name: Timer
  events: [started, canceled, timeout] # started is start event
  behavior:
    - [started, canceled]
    - [started, timeout]
    - [canceled, started]
    - [timeout, started]
"""

yaml_desklamp = """device:
  name: DeskLamp
  components:
    ledA: Led
    ledB: Led
    b: Button
    t: Timer
  events:
    - level1:
        start: True
        micro: [b.pressed, b.released, ledA.on, t.started]
    - level2:
        micro:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    - standby1:
        micro: [t.timeout, ledA.off]
    - standby2:
        micro:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
  behavior:
    - [level1, standby1]
    - [level1, level2]
    - [level2, standby2]
    - [standby1, level1]
    - [standby2, level1]"""


def test_assemble_smart_button() -> None:
    # Button
    shelley_device: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(yaml_button)
    automata: AutomataDevice = shelley2automata.shelley2automata(shelley_device)

    assembled_button: AssembledDevice = AssembledDevice.make(automata, empty_devices)
    assert assembled_button.is_valid
    assert type(assembled_button.external) == CheckedDevice

    known_devices = {
        "Button": assembled_button.external,
    }

    # Smartbutton
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_smartbutton)
    automata = shelley2automata.shelley2automata(shelley_device)

    assembled_smartbutton: AssembledDevice = AssembledDevice.make(
        automata, known_devices.__getitem__
    )
    assert assembled_smartbutton.is_valid
    assert type(assembled_smartbutton.external) == CheckedDevice

    with pytest.raises(ValueError) as exc_info:
        # test micro traces
        check_traces(
            assembled_smartbutton.internal_model_check,
            {"ok": {"good": ["b.released", "b.pressed"]}, "fail": {}},
        )  # micro

    assert (
        str(exc_info.value)
        == "Unaccepted valid trace 'good': ['b.released', 'b.pressed']"
    )


def test_assemble_desklamp() -> None:
    # LED
    shelley_device: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(yaml_led)
    automata: AutomataDevice = shelley2automata.shelley2automata(shelley_device)

    assembled_led: AssembledDevice = AssembledDevice.make(automata, empty_devices)
    assert assembled_led.is_valid
    assert type(assembled_led.external) == CheckedDevice

    # Button
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_button)
    automata = shelley2automata.shelley2automata(shelley_device)

    assembled_button: AssembledDevice = AssembledDevice.make(automata, empty_devices)
    assert assembled_button.is_valid
    assert type(assembled_button.external) == CheckedDevice

    # Timer
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_timer)
    automata = shelley2automata.shelley2automata(shelley_device)

    assembled_timer: AssembledDevice = AssembledDevice.make(automata, empty_devices)
    assert assembled_timer.is_valid
    assert type(assembled_timer.external) == CheckedDevice

    known_devices = {
        "Button": assembled_button.external,
        "Led": assembled_led.external,
        "Timer": assembled_timer.external,
    }

    # Desklamp
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_smartbutton)
    automata = shelley2automata.shelley2automata(shelley_device)

    assembled_desklamp: AssembledDevice = AssembledDevice.make(
        automata, known_devices.__getitem__
    )
    assert assembled_desklamp.is_valid
    assert type(assembled_desklamp.external) == CheckedDevice
