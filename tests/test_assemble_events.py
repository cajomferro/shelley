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
  start_with: [connected]
  end_with: $ANY
  name: HTTPClient
  operations:
      connected:
        next: [get, post, connect_failed]
      disconnected:
        next: [connected]
      get:
        next: [response200, response404, response401, response500]
      post:
        next: [response200, response404, response401, response500]
      connect_failed:
        next: [connected]
      response200:
        next: [get, post, disconnected]
      response404:
        next: [get, post, disconnected]
      response401:
        next: [get, post, disconnected]
      response500:
        next: [get, post, disconnected]
"""

wificlient_yml = """
  name: WiFiClient
  start_with: [ssid_joined, ssid_failed, connection_timeout]
  end_with: $ANY
  operations:
    ssid_joined:
        next: [connected, ssid_left]
    ssid_failed:
        next: [ssid_failed, ssid_joined]
    connection_timeout:
        next: [connected]
    connected:
        next: [disconnected, print_timeout, print_data_ready]
    print_data_ready:
        next: [print_data_ready, disconnected]
    print_timeout:
        next: [print_timeout, disconnected]
    ssid_left:
        next: [ssid_joined, ssid_failed]
    disconnected:
        next: [connected, connection_timeout, ssid_left]
"""

wifihttp_yml = """
  name: WiFiHTTP
  start_with: $ANY
  end_with: $ANY
  components:
      hc: HTTPClient
      wc: WiFiClient
  operations:
    started:
        micro: [wc.joined, wc.connected, hc.connected]
        next: [send]
    notconnected:
        micro:
          xor:
            - [wc.joined, wc.connected, hc.connect_failed]
            - xor:
              - [wc.joined, wc.connection_timeout]
              - [wc.ssid_failed]
        next: [started]
    send:
        micro:
          xor:
            - hc.get
            - hc.post
        next: [stopped, ok, error]
    ok:
        next: [send, stopped]
        micro: [wc.print_data_ready, hc.response200]
    error:
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


def replace_start_with(s: str, expr: str, prefix: str = "start_with: ") -> str:
    return s.replace("start_with: $ANY\n", prefix + f"{expr}\n")


def test_start_missing_true() -> None:
    # Missing True here
    wifihttp_yml_bad = replace_start_with(wifihttp_yml, expr="")

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )

    assert (
        "section 'start_with': expecting string '$ANY', or a list of operation names (strings), but got: None\nHint: To list all operations write 'start_with: $ANY'"
        == str(exc_info.value)
    )


def test_start_not_bool() -> None:
    wifihttp_yml_bad = replace_start_with(wifihttp_yml, expr="Txrxuxe")

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        wifihttp_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            wifihttp_yml_bad
        )

    assert (
        "section 'start_with': expecting string '$ANY', or a list of operation names (strings), but got: 'Txrxuxe'\nHint: To list all operations write 'start_with: $ANY'"
        == str(exc_info.value)
    )
