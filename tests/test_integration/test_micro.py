import pytest
import re
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
)
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley import yaml2shelley


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
        micro: [wc.joined, wc.connected, hc.connected]
    - notconnected:
        start: True
        micro:
          xor:
            - [wc.joined, wc.connected, hc.connect_failed]
            - xor:
              - [wc.joined, wc.connection_timeout]
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

    return AssembledDevice.make(wificlient_aut, {})


def _get_http_client_assembled() -> AssembledDevice:
    httpclient_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        httpclient_yml
    )
    httpclient_aut: AutomataDevice = shelley2automata.shelley2automata(httpclient_shy)

    return AssembledDevice.make(httpclient_aut, {})


httpclient_assembled = _get_http_client_assembled()
wificlient_assembled = _get_wifi_client_assembled()


def test_compile_wifihttp_event_undeclared() -> None:
    """
    If the device has components and event is undeclared, it means it doesn't have micro hence is invalid
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = r""  # send will be auto discovered without specifying micro
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert (
        "Event 'send' doesn't specify micro behavior but device has components!"
        == str(exc_info.value)
    )


def test_compile_wifihttp_event_declared_micro_empty1() -> None:
    """
    If the device has components and event is declared, micro must have at least one trigger rule
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = r"    - send:\n" r"        micro: {}"
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert str(exc_info.value) == "Micro must not be empty!"


def test_compile_wifihttp_event_declared_micro_empty2() -> None:
    """
    If the device has components and event is declared, micro must have at least one trigger rule
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = r"    - send:\n" r"        micro: []"
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert "Micro must not be empty!" == str(exc_info.value)


def test_compile_wifihttp_event_declared_micro_undeclared() -> None:
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = (
            r"    - send:\n" r"        start: True\n"
        )  # micro is now undefined but send event is still declared
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert (
        str(exc_info.value)
        == "Event 'send' doesn't specify micro behavior but device has components!"
    )


def test_compile_wifihttp_invalid_xor_1_option() -> None:
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.post"
        )
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert (
        str(exc_info.value)
        == "Invalid micro rule '{'xor': ['hc.post']}'. Branching (xor) requires 2 options!"
    )


def test_compile_wifihttp_invalid_xor_3_options() -> None:
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = (
            r"    - send:\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

        # parse yaml and assemble device
        known_devices = {
            "HTTPClient": httpclient_assembled.external,
            "WiFiClient": wificlient_assembled.external,
        }
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )
        wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert (
        str(exc_info.value)
        == "Invalid micro rule '{'xor': ['hc.get', 'hc.get', 'hc.post']}'. Branching (xor) requires 2 options!"
    )
