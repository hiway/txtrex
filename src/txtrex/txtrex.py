from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server


class TxtRex(object):
    """
    A resolver which presents a blog to the client through TXT records,
    interaction and hyperlinking happens through dynamic, made-up TLDs.

    The blog posts are text files in a directory with metadata embedded
    within the file names as such:

        /posts
            - 20171201-01-trying.something.silly.txt
            - 20171201-02-hello.txt
            - 19831101-blast.from.the.past.txt

    Comments are appended to `comments` directory, with same name as the
    post it refers to, with extension changed to `.comments.log`. Comments
    are not published, and can only be read from within the server.

        /posts
            /comments
                - 20171201-01-trying.something.silly.comments.log

    Every `*.comments.log` line contains:
        - timestamp
        - client-ip
        - comment

    Examples:
        $ dig @127.0.0.1 -p 10053 TXT +short blog.latest
        "# Hello"
        "This is a test."
        "Try: blog.index"

        $ dig @127.0.0.1 -p 10053 TXT +short blog.index
        "Latest: blog.latest"
        "Recent:"
        "   blog.hello"
        "   blog.trying.something.silly"

        $ dig @127.0.0.1 -p 10053 TXT +short blog.trying.something.silly
        "# Woohoo!"
        "This actually works?!"

        $ dig @127.0.0.1 -p 10053 TXT +short blog.search.silly
        "# Search results for: silly"
        "blog.trying.something.silly # Woohoo!"

        $ dig @127.0.0.1 -p 10053 TXT +short blog.trying.something.silly.comment.this.is.going.too.far
        "Posted:"
        "this is going too far"
    """
    _pattern = 'rex'

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
        text = 'You asked for: {}'.format(name)
        payload = dns.Record_TXT(bytes(text, 'utf-8'))
        answer = dns.RRHeader(
            name=name,
            payload=payload,
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
