import pytest
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
    CheckedDevice,
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

    wifihttp_assembled = AssembledDevice.make(wifihttp_aut, known_devices)

    assert wifihttp_assembled.is_valid
    assert type(wifihttp_assembled.external) == CheckedDevice


def test_compile_wifihttp_no_known_devices() -> None:
    wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(wifihttp_yml)
    wifihttp_aut: AutomataDevice = shelley2automata.shelley2automata(wifihttp_shy)

    with pytest.raises(KeyError) as exc_info:
        wifihttp_assembled = AssembledDevice.make(wifihttp_aut, {})

    assert "'HTTPClient'" == str(exc_info.value)
