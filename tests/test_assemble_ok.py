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
  name: HTTPClient
  operations:
    connected:
        start: true
        next: [get, post, connect_failed]
    disconnected:
        start: false
        next: [connected]
    get:
        start: false
        next: [response200, response404, response401, response500]
    post:
        start: false
        next: [response200, response404, response401, response500]
    connect_failed:
        start: false
        next: [connected]
    response200:
        start: false
        next: [get, post, disconnected]
    response404:
        start: false
        next: [get, post, disconnected]
    response401:
        next: [get, post, disconnected]
        start: false
    response500:
        next: [get, post, disconnected]
        start: false
"""

wificlient_yml = """
  name: WiFiClient
  operations:
    ssid_joined:
        start: True
        next: [connected, ssid_left]
    ssid_failed:
        start: True
        next: [ssid_failed, ssid_joined]
    connection_timeout:
        start: true
        next: [connected]
    connected:
        start: false
        next: [disconnected, print_timeout, print_data_ready]
    print_data_ready:
        start: false
        next: [print_data_ready, disconnected]
    print_timeout:
        start: false
        next: [print_timeout, disconnected]
    ssid_left:
        start: false
        next: [ssid_joined, ssid_failed]
    disconnected:
        start: false
        next: [connected, connection_timeout, ssid_left]
"""

wifihttp_yml = """
  name: WiFiHTTP
  components:
      hc: HTTPClient
      wc: WiFiClient
  operations:
    started:
        start: True
        micro: [wc.ssid_joined, wc.connected, hc.connected]
        next: [send]
    notconnected:
        start: True
        next: [started]
        micro:
          xor:
            - [wc.ssid_joined, wc.connected, hc.connect_failed]
            - xor:
              - [wc.ssid_joined, wc.connection_timeout]
              - [wc.ssid_failed]
    send:
        start: false
        next: [stopped, ok, error]
        micro:
          xor:
            - hc.get
            - hc.post
    ok:
        start: false
        micro: [wc.print_data_ready, hc.response200]
        next: [stopped, send]
    error:
        start: false
        next: [stopped, send]
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
    stopped:
        start: false
        micro: [wc.disconnected, hc.disconnected, wc.ssid_left]
        next: [started, notconnected]
"""


def _get_wifi_client_assembled() -> AssembledDevice:
    wificlient_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        wificlient_yml
    )
    wificlient_aut: AutomataDevice = shelley2automata.shelley2automata(wificlient_shy)

    return AssembledDevice.make(wificlient_aut, DeviceMapping().__getitem__)


def _get_http_client_assembled() -> AssembledDevice:
    httpclient_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        httpclient_yml
    )
    httpclient_aut: AutomataDevice = shelley2automata.shelley2automata(httpclient_shy)

    return AssembledDevice.make(httpclient_aut, DeviceMapping().__getitem__)


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
            wifihttp_aut, DeviceMapping().__getitem__
        )

    assert "Error loading system 'HTTPClient': system not defined" == str(
        exc_info.value
    )


def empty_devices(name: str) -> CheckedDevice:
    raise ValueError()


yaml_button = """
name: Button
operations:
    pressed:
      start: true
      next: [released]
    released:
      start: false
      next: [pressed]

test_system:
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
name: SmartButton
components:
    b: Button
operations:
    on:
        start: True
        final: True
        micro: [ b.pressed, b.released]
        next: [on]


test_system:
  ok:
    valid1: [on]
    valid2: [on, on, on, on]
  fail:
    invalid1: False
    empty: []

test_integration:
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
  name: Led
  operations:
    on:
        start: true
        next: [off]
    off:
        start: false
        next: [on]"""

yaml_timer = """
  name: Timer
  operations:
    started:
        start: true
        next: [canceled, timeout]
    canceled:
        start: false
        next: [started]
    timeout:
        start: false
        next: [started]
"""

yaml_desklamp = """
  name: DeskLamp
  operations:
    ledA: Led
    ledB: Led
    b: Button
    t: Timer
  events:
    level1:
        start: True
        micro: [b.pressed, b.released, ledA.on, t.started]
        next: [standby1, level2]
    level2:
        next: [standby2]
        start: false
        micro:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    standby1:
        start: false
        micro: [t.timeout, ledA.off]
        next: [level1]
    standby2:
        start: false
        next: [level1]
        micro:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
"""


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
