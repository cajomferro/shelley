import machine
import socket as usocket
from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final

class RequestError(Exception):
    pass


class SocketError(Exception):
    pass


@claim("system check connect & F (disconnect & END);")
@system(uses={})
class HTTP:
    def _connect(self, host, port):
        try:
            ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
            ai = ai[0]
        except OSError as err:
            print(err)
            raise SocketError("Socket get address info failed")

        socket = usocket.socket(ai[0], ai[1], ai[2])
        try:
            machine.sleep(0)
            socket.connect(ai[-1])
            machine.sleep(3)
            return socket
        except OSError as err:
            print(err)
            socket.close()
            del socket
            raise SocketError("Socket connection failed")

    def _ssl(self, socket, host):
        try:
            import ussl

            socket = ussl.wrap_socket(socket, server_hostname=host)
            return socket
        except OSError as err:
            print(err)
            socket.close()
            del socket
            if err.args[0] != 16:
                raise SocketError("Socket ssl binding failed!")
            else:
                raise SocketError("Fatal error")

    def _request(self, method, url, data=None, auth_string=None):
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""

        query = "%s /%s HTTP/1.0\r\n" % (method, path)
        query += "Host: %s\r\n" % (host)
        query += "Connection: close\r\n"
        query += "User-Agent: compat\r\n"
        query += "Content-Type: application/json\r\n"
        query += "Authorization: Basic %s\r\n" % (auth_string)
        query += "Content-Length: %d\r\n" % len(data)
        query += "\r\n"
        query += data

        try:
            sreader = machine.StreamReader(self.socket)
            swriter = machine.StreamWriter(self.socket, {})

            swriter.write(query.encode("utf-8"))
            swriter.drain()
            res = sreader.readline()
            return res
        except OSError as err:
            raise RequestError(str(err))

    def _connect(self, url):
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)

        if proto == "http:":
            port = 80
        elif proto == "https:":
            port = 443
        else:
            self.last_error = "Unsupported protocol: " + proto
            return "connect_failed"

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        for i in range(3):
            try:
                self.socket = self._connect(host, port)
                if proto == "https:":
                    self.socket = self._ssl(self.socket, host)
                    return True
            except SocketError as err:
                print(err)
            machine.sleep(3)

        self.last_error = "Could not open socket after max tries!"
        return False

    @op_initial
    def connect(self, url):
        match self._connect(url):
            case True:
                return "connect_ok"
            case False:
                return "connect_failed"

    @op
    def connect_ok(self):
        # print('Connected to {} on port {}'.format(host, port))
        print("Connected to socket!")
        return ["get", "post", "disconnect"]

    @op
    def connect_failed(self):
        print(f"Connecting to socket failed: {self.last_error}")
        return "disconnect"

    @op
    def get(self, url, **kw):
        try:
            self.res = self._request("GET", url, **kw)
            return "get_ok"
        except RequestError as err:
            self.last_error = err
            return "get_error"

    @op
    def get_ok(self):
        print("GET ok")
        return ["get", "post", "disconnect"]

    @op
    def get_error(self):
        print(f"GET error: {self.last_error}")
        return ["get", "post", "disconnect"]

    @op
    def post(self, url, **kw):
        try:
            self.res = self._request("POST", url, **kw)
            return "post_ok"
        except RequestError as err:
            self.last_error = err
            return "post_error"

    @op
    def post_ok(self):
        print("POST ok")
        return ["get", "post", "disconnect"]

    @op
    def post_error(self):
        print(f"POST error: {self.last_error}")
        return ["get", "post", "disconnect"]

    @op_final
    def disconnect(self):
        self.socket.close()
        return "connect"
