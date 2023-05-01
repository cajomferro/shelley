import settings as setts
import machine
import ujson

from .wifi import WiFiClient
from .http import HTTP

from shelley.shelleypy import system, operation, claim, op_initial_final, op_initial, op_final, op

@claim("system check start & F (stop & END);")
@claim("integration check G (http.connect_failed -> X http.disconnect);")
@claim("integration check G (wifi.enable -> F ((wifi.get_rssi & (X (http.connect))) | wifi.connect_error));")
@claim("integration check G (http.post -> F wifi.disable);")
@claim("integration check G (((! (wifi.get_rssi | http.disconnect)) -> ((X ! http.connect) | END  )));")
@system(uses={"wifi": "WiFi", "http": "HTTP"})
class Wireless:

    def __init__(self):
        self.wifi = WiFiClient()
        self.http = HTTP()

    @op_initial
    def start(self):
        self.wifi.enable()
        match self.wifi.connect():
            case "connect_ok":
                self.wifi.connect_ok()
                return ["start_ok"]
            case "connect_error":
                self.wifi.connect_error()
                return ["start_failed"]

    @op_final
    def stop(self):
        self.wifi.disable()
        return ["start"]

    @op
    def start_ok(self):
        self.wifi.get_rssi()
        return ["request"]

    @op
    def start_failed(self):
        machine.sleep(2)
        return ["stop"]

    @op
    def request(self, post_data):
        print("Sending now...")
        request_url = "https://" + setts.get("host-url") + setts.get("host-uri")
        post_data = ujson.dumps(post_data)

        match self.http.connect(request_url):
            case "connect_ok":
                self.http.connect_ok()
                match self.http.post(request_url, data=post_data,
                                     auth_string=setts.get("host-auth-string")):
                    case "post_ok":
                        self.http.post_ok()
                        print("Hello done!")
                        self.http.disconnect()
                        return ["request_ok"]
                    case "post_error":
                        self.http.post_error()
                        machine.sleep(5)
                        self.http.disconnect()
                        self.error = "POST request failed!"
                        return ["request_error"]
            case "connect_failed":
                self.http.connect_failed()
                self.http.disconnect()
                self.error = "HTTP connection failed!"
                return ["request_error"]


    @op
    def request_error(self):
        print(f"{self.error}")
        return ["request", "stop"]

    @op
    def request_ok(self):
        print("request done!")
        return ["request", "stop"]