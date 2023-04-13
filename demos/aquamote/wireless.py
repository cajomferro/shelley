import settings as setts
import machine
import ujson

from .wifi import WiFiClient
from .http import HTTP

from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final

# obvious from the spec itself?
#@claim("system check start & F (stop & END);")
#
# claim1: always join a Wi-Fi network before connecting to server
@claim("integration check (!http.connect) W wifi.connect_ok;")
#
# claim2: if we join Wi-Fi then we must try sending a request
@claim("integration check G (wifi.connect_ok -> F this.request);")
#
# claim3: The request method always makes a http connection attempt
@claim("integration check G (this.request -> ((!this.request_error & !this.request_ok) W http.connect));")
#
# claim4: if there is a successful connection to the server, we must do a post
@claim("integration check G (http.connect_ok -> (X http.post));")
#
# do we want this claim?! it is true but..is it useful?
# @claim("integration check G (http.connect -> (!wifi.get_rssi) W wifi.disable);")
#
# true but..kind of obvious?! I mean, if Wi-Fi is enabled the Wi-Fi spec already forces the disable eventually
# @claim("integration check G (http.connect -> F wifi.disable);")
#
# do we want this claim?! it is true but..is it useful?
# @claim("integration check G (((!wifi.get_rssi & !http.disconnect) -> ((X !http.connect) | END)));")
#
# although this claim is true, let's use claim2+claim3 instead
# @claim("integration check G (wifi.enable -> F ((wifi.connect_ok & (F (http.connect))) | wifi.connect_error));")
#
# although this claim is true, let's use claim3 instead
# @claim("integration check G (wifi.connect_ok -> (F http.connect));")
#
# already guaranteed by the HTTP spec itself
# @claim("integration check G (http.connect_failed -> X http.disconnect);")
@system(uses={"wifi": "WiFi", "http": "HTTP"})
class Wireless:

    def __init__(self):
        self.wifi = WiFiClient()
        self.http = HTTP()
        self._response = None

    @op_initial
    def start(self):
        # for _ in range(setts.get("wifi-join-tries")):

        # counterexample for claim1
        # match self.http.connect(request_url):
        #     case "connect_ok":
        #         self.http.connect_ok()
        #     case "connect_failed":
        #         self.http.connect_failed()
        # self.http.disconnect()

        self.wifi.enable()
        match self.wifi.connect():
            case "connect_ok":
                self.wifi.connect_ok()
                return "start_ok"
            case "connect_error":
                self.wifi.connect_error()
                return "start_failed"

    @op
    def start_ok(self):
        # rssi = self.wifi.get_rssi()
        self.wifi.get_rssi()
        # print("Node RSSI: {0}".format(rssi))
        # setts.set("node-rssi", rssi)
        return "request"

    # @operation(next=["request"])
    # def start_ok_alt(self):
    #     return "request"

    @op
    def start_failed(self):
        machine.sleep(2)
        return "stop"

    @op
    def request(self, post_data):
        """
         I don't care if the request failed or not, just go on and stop or do another request
        """
        # For each request a new socket is open and closed
        print("Sending now...")
        request_url = "https://" + setts.get("host-url") + setts.get("host-uri")
        post_data = ujson.dumps(post_data)

        # uncomment for claim3
        # for _ in max_tries:
        #     match self.http.connect(request_url):
        #         case "connect_ok":
        #             self.http.connect_ok()
        #             match self.http.post(request_url, data=post_data,
        #                                  auth_string=setts.get("host-auth-string")):
        #                 case "post_ok":
        #                     self._response = self.http.post_ok()
        #                     return "request_ok"
        #                 case "post_error":
        #                     self.http.post_error()
        #                     self.http.disconnect()
        #         case "connect_failed":
        #             self.http.connect_failed()
        #             self.http.disconnect()
        # return "request_error"

        match self.http.connect(request_url):
            case "connect_ok":
                self.http.connect_ok()
                match self.http.post(request_url, data=post_data,
                                     auth_string=setts.get("host-auth-string")):
                    case "post_ok":
                        self._response = self.http.post_ok()
                        return "request_ok"
                    case "post_error":
                        self.http.post_error()
            case "connect_failed":
                self.http.connect_failed()
        self.http.disconnect()
        return "request_error"

        # for _ in range(setts.get("hello-tries")):
        #     match self.http.connect(request_url):
        #         case "requests.connect_ok":
        #             self.http.connect_ok()
        #             for _ in range(setts.get("hello-tries")):
        #                 match self.http.post(request_url, data=post_data,
        #                                                auth_string=setts.get("host-auth-string")):
        #                     case "requests.post_ok":
        #                         self.http.post_ok()
        #                         print("Hello done!")
        #                         self.http.disconnect()
        #                         #return
        #                     case "requests.post_error":
        #                         self.http.post_error()
        #                         print("Hello failed!")
        #                         machine.sleep(5)
        #             self.http.disconnect()
        #             #return
        #         case "requests.connect_failed":
        #             self.http.connect_failed()
        #             self.http.disconnect()

        # return  # I don't care if the
        # hello failed or not, just go on and stop or do another request

    @op
    def request_error(self):
        print("request error")
        # self.wifi.get_rssi()
        return ["request", "stop"]

    @op
    def request_ok(self):
        print("request done!")
        self.http.disconnect()
        return ["request", "stop"], self._response

    @op_final
    def stop(self):
        self.wifi.disable()
        return "start"