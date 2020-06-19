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
    connected: {start: true}
    disconnected: {start: false}
    get: {start: false}
    post: {start: false}
    connect_failed: {start: false}
    response200: {start: false}
    response404: {start: false}
    response401: {start: false}
    response500: {start: false}
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
    ssid_joined:
        start: True
    ssid_failed:
        start: True
    connection_timeout: {start: true}
    connected: {start: false}
    print_data_ready: {start: false}
    print_timeout: {start: false}
    ssid_left: {start: false}
    disconnected: {start: false}
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
    started:
        start: True
        micro: [wc.joined, wc.connected, hc.connected]
    notconnected:
        start: True
        micro:
          xor:
            - [wc.joined, wc.connected, hc.connect_failed]
            - xor:
              - [wc.joined, wc.connection_timeout]
              - [wc.ssid_failed]
    send:
        start: false
        micro:
          xor:
            - hc.get
            - hc.post
    ok:
        start: false
        micro: [wc.print_data_ready, hc.response200]
    error:
        start: false
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

    return AssembledDevice.make(wificlient_aut, DeviceMapping().__getitem__)


def _get_http_client_assembled() -> AssembledDevice:
    httpclient_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        httpclient_yml
    )
    httpclient_aut: AutomataDevice = shelley2automata.shelley2automata(httpclient_shy)

    return AssembledDevice.make(httpclient_aut, DeviceMapping().__getitem__)


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
            r"    send:\n"
            r"        start: false\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = r"    send: {start: false}\n"  # send will be auto discovered without specifying micro
        wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)
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
        "operation declaration error in ['send']: Only declare an integration rule when there are components (system has 2 components).\nHint: write integration rule or remove all components."
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
            r"    send:\n"
            r"        start: false\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = r"    send:\n" r"        micro: {}"
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
        regex = (
            r"    send:\n"
            r"        start: false\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = r"    send:\n" r"        micro: []"
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
        # introduce bad syntax on good yml
        regex = (
            r"    send:\n"
            r"        start: false\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = (
            r"    send:\n" r"        start: True\n"
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

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        str(exc_info.value)
        == "operation declaration error in ['send']: Only declare an integration rule when there are components (system has 2 components).\nHint: write integration rule or remove all components."
    )


def XXX_test_compile_wifihttp_invalid_xor_1_option() -> None:
    # TODO: Error in operation declaration 'started': unknown operations {'wc.joined'}
    """
    If the device has components and event is declared, it must specify micro
    :return:
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        # introduce bad syntax on good yml
        regex = (
            r"    send:\n"
            r"        start: false\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = (
            r"    send:\n"
            r"        start: false\n"
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
        regex = (
            r"    send:\n"
            r"        start: false\n"
            r"        micro:\n"
            r"          xor:\n"
            r"            - hc.get\n"
            r"            - hc.post"
        )
        replace = (
            r"    send:\n"
            r"        start: false\n"
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

        wifihttp_assembled = AssembledDevice.make(
            wifihttp_aut, known_devices.__getitem__
        )

    assert (
        str(exc_info.value)
        == "Invalid micro rule '{'xor': ['hc.get', 'hc.get', 'hc.post']}'. Branching (xor) requires 2 options!"
    )
