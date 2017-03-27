from opbeat.instrumentation.packages.base import AbstractInstrumentedModule
from opbeat.traces import trace
from opbeat.utils import default_ports
from opbeat.utils.compat import urlparse


class HostFromUrlMixin(object):

    def get_host_from_url(self, url):
        parsed_url = urlparse.urlparse(url)
        host = parsed_url.hostname or " "

        if (
            parsed_url.port and
            default_ports.get(parsed_url.scheme) != parsed_url.port
        ):
            host += ":" + str(parsed_url.port)

        return host


class RequestsInstrumentation(AbstractInstrumentedModule, HostFromUrlMixin):
    name = 'requests'

    instrument_list = [
        ("requests.sessions", "Session.request"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if 'method' in kwargs:
            method = kwargs['method']
        else:
            method = args[0]

        if 'url' in kwargs:
            url = kwargs['url']
        else:
            url = args[1]

        signature = method.upper()

        if url:
            signature += " " + self.get_host_from_url(url)

        with trace(signature, "ext.http.requests",
                   {'url': url}, leaf=True):
            return wrapped(*args, **kwargs)


class PreparedRequestInstrumentation(AbstractInstrumentedModule, HostFromUrlMixin):
    name = 'requests_prepared_request'

    instrument_list = [
        ("requests.sessions", "Session.send"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if 'request' in kwargs:
            request = kwargs['request']
        else:
            request = args[0]

        signature = request.method.upper()
        signature += " " + self.get_host_from_url(request.url)

        with trace(signature, "ext.http.requests",
                   {'url': request.url}, leaf=True):
            return wrapped(*args, **kwargs)