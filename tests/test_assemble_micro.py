import pytest
import re
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
)
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley import yaml2shelley
from shelley.shelleyc import DeviceMapping

httpclient_yml = """
device:
  name: HTTPClient
  events:
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
device:
  name: WiFiClient
  events:
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
device:
  name: WiFiHTTP
  components:
      hc: HTTPClient
      wc: WiFiClient
  events:
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

SEND_REGEX = r"""    send:
        start: false
        next: [stopped, ok, error]
        micro:
          xor:
            - hc.get
            - hc.post
"""


def replace_send(yml: str, *lines: str) -> str:
    replace = "    send:\n" "        next: [stopped, ok, error]\n"
    for line in lines:
        replace += "        " + line + "\n"
    return yml.replace(SEND_REGEX, replace)


def test_compile_wifihttp_event_undeclared() -> None:
    """
    If the device has components and event is undeclared, it means it doesn't have micro hence is invalid
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        wifihttp_yml_bad = replace_send(wifihttp_yml)
        print(wifihttp_yml_bad)
        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )
    assert (
        "operation declaration error in ['send']: Integration rule missing. Only declare an integration rule when there are components (system has 2 components).\nHint: write integration rule or remove all components."
        == str(exc_info.value)
    )


def test_compile_wifihttp_event_declared_micro_empty1() -> None:
    """
    If the device has components and event is declared, micro must have at least one trigger rule
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        wifihttp_yml_bad = replace_send(wifihttp_yml, "micro: {}")

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        str(exc_info.value)
        == "operation declaration error in ['send']: integration rule error: An empty sequence introduces ambiguity.\nHint: remove empty sequence or add subsystem call to sequence."
    )


def test_compile_wifihttp_event_declared_micro_empty2() -> None:
    """
    If the device has components and event is declared, micro must have at least one trigger rule
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        wifihttp_yml_bad = replace_send(wifihttp_yml, "micro: []")
        print(wifihttp_yml_bad)
        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        "operation declaration error in ['send']: integration rule error: An empty sequence introduces ambiguity.\nHint: remove empty sequence or add subsystem call to sequence."
        == str(exc_info.value)
    )


def test_compile_wifihttp_event_declared_micro_undeclared() -> None:
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # micro is now undefined but send event is still declared
        wifihttp_yml_bad = replace_send(wifihttp_yml, "start: True")

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        str(exc_info.value)
        == "operation declaration error in ['send']: Integration rule missing. Only declare an integration rule when there are components (system has 2 components).\nHint: write integration rule or remove all components."
    )


def XXX_test_compile_wifihttp_invalid_xor_1_option() -> None:
    # TODO: Error in operation declaration 'started': unknown operations {'wc.joined'}
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        wifihttp_yml_bad = replace_send(
            wifihttp_yml, "micro:", "  xor:", "    - hc.post"
        )

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        str(exc_info.value)
        == "Invalid micro rule '{'xor': ['hc.post']}'. Branching (xor) requires 2 options!"
    )


def XXX_test_compile_wifihttp_invalid_xor_3_options() -> None:
    # There is an error in WiFiClient: unknown operation wc.joined
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        wifihttp_yml_bad = replace_send(
            wifihttp_yml,
            "micro:",
            "  xor:",
            "    - hc.get",
            "    - hc.get",
            "    - hc.post",
        )

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        str(exc_info.value)
        == "Invalid micro rule '{'xor': ['hc.get', 'hc.get', 'hc.post']}'. Branching (xor) requires 2 options!"
    )
