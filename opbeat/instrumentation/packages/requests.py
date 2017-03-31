from opbeat.instrumentation.packages.base import AbstractInstrumentedModule
from opbeat.traces import trace
from opbeat.utils import default_ports
from opbeat.utils.compat import urlparse


def get_host_from_url(url):
    parsed_url = urlparse.urlparse(url)
    host = parsed_url.hostname or " "

    if (
        parsed_url.port and
        default_ports.get(parsed_url.scheme) != parsed_url.port
    ):
        host += ":" + str(parsed_url.port)

    return host


class RequestsInstrumentation(AbstractInstrumentedModule):
    name = 'requests'

    instrument_list = [
        ("requests.sessions", "Session.send"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if 'request' in kwargs:
            request = kwargs['request']
        else:
            request = args[0]

        signature = request.method.upper()
        signature += " " + get_host_from_url(request.url)

        with trace(signature, "ext.http.requests",
                   {'url': request.url}, leaf=True):
            return wrapped(*args, **kwargs)
