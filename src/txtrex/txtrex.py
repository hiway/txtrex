from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server


class TxtRex(object):
    """
    A resolver which presents a blog to the client through TXT records,
    interaction and hyperlinking happens through dynamic, made-up TLDs.

    Example:
        dig @localhost -p 10053 workstation1.example.com TXT +short
        "You are looking for: 172.0.2.1"

    """
    _pattern = 'workstation'
    _network = '172.0.2'

    def _dynamic_response_required(self, query):
        """
        Check the query to determine if a dynamic response is required.
        """
        if query.type == dns.TXT:
            labels = str(query.name.name, 'utf-8').split('.')
            if labels[0].startswith(self._pattern):
                return True
        return False

    def _do_dynamic_response(self, query):
        """
        Calculate the response to a query.
        """
        name = str(query.name.name, 'utf-8')
        labels = name.split('.')
        parts = labels[0].split(self._pattern)
        last_octet = int(parts[1])
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_TXT(bytes('You are looking for: %s.%s' % (self._network, last_octet), 'utf-8')),
            type=dns.TXT,
        )
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional

    def query(self, query, timeout=None):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        if self._dynamic_response_required(query):
            return defer.succeed(self._do_dynamic_response(query))
        else:
            return defer.fail(error.DomainError())


def main():
    """
    Run the server.
    """
    factory = server.DNSServerFactory(
        clients=[TxtRex(), client.Resolver(resolv='/etc/resolv.conf')]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)

    reactor.run()


if __name__ == '__main__':
    raise SystemExit(main())
