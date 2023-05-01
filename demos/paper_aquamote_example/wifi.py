import settings as setts
import umachine as machine
import network
import machine

from shelley.shelleypy import operation, system, claim, op_initial_final, op_initial, op_final, op


class UnstableWifiError(Exception):
    def __init__(self):
        super().__init__("Unstable WiFi connection!")


@claim("system check enable & F (disable & END);")
@system(uses={})
class WiFi:
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)

    @op_initial
    def enable(self):
        self._wlan.active(True)
        return ["connect"]

    @op_final
    def disable(self):
        if self._wlan.isconnected():
            self._wlan.disconnect()
        self._wlan.active(False)
        return ["enable"]

    @op
    def connect(self):
        error = False
        def _wait_for_connection():
            print("Waiting for router...")
            while self._wlan.status() == network.STAT_CONNECTING:
                machine.sleep_ms(500)

        self._wlan.connect(setts.get("wifi-ssid"), setts.get("wifi-password"))

        try:
            machine.wait_for(
                _wait_for_connection(), setts.get("wifi-join-timeout-sec")
            )
        except machine.TimeoutError:
            error = True

        if error:
            return ["connect_error"]

        for _ in range(3):  # wait a bit to check if wifi is stable
            if not self._wlan.isconnected():
                return ["connect_error"]
            machine.sleep_ms(500)

        return ["connect_ok"]

    @op
    def connect_ok(self):
        print("WiFi is connected!")
        return ["get_rssi", "disable"]

    @op
    def connect_error(self):
        print(f"WiFi connection error: {self._wlan.last_error()}")
        return "disable"

    @op
    def get_rssi(self):
        return ["get_rssi", "disable"]
