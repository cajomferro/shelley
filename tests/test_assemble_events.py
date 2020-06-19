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
        start: false
        next: [get, post, disconnected]
      response500:
        start: false
        next: [get, post, disconnected]
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
        micro: [wc.joined, wc.connected, hc.connected]
        next: [send]
    notconnected:
        start: True
        micro:
          xor:
            - [wc.joined, wc.connected, hc.connect_failed]
            - xor:
              - [wc.joined, wc.connection_timeout]
              - [wc.ssid_failed]
        next: [started]
    send:
        start: True
        micro:
          xor:
            - hc.get
            - hc.post
        next: [stopped, ok, error]
    ok:
        start: True
        next: [send, stopped]
        micro: [wc.print_data_ready, hc.response200]
    error:
        start: True
        next: [send, stopped]
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
        next: [started, notconnected]
        start: True
        micro: [wc.disconnected, hc.disconnected, wc.ssid_left]
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


def test_start_missing_true() -> None:

    regex = r"  events:\n" r"    started:\n" r"        start: True"
    replace = r"  events:\n" r"    started:\n" r"        start: "  # Missing True here

    wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )

    assert (
        "operation declaration error in ['started']: Expecting a boolean, but found NoneType: None"
        == str(exc_info.value)
    )


def test_start_not_bool() -> None:
    regex = r"  events:\n" r"    started:\n" r"        start: True"
    replace = (
        r"  events:\n" r"    started:\n" r"        start: Txrxuxe"
    )  # Invalid type !

    wifihttp_yml_bad = re.sub(regex, replace, wifihttp_yml)

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )

    assert (
        "operation declaration error in ['started']: Expecting a boolean, but found str: 'Txrxuxe'"
        == str(exc_info.value)
    )
