import arrow
import re
import os
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
        $ dig @127.0.0.1 -p 10053 TXT +short rex.latest
        "# Hello"
        "This is a test."
        "Try: rex.index"

        $ dig @127.0.0.1 -p 10053 TXT +short rex.index
        "Latest: rex.latest"
        "Recent:"
        "   rex.hello"
        "   rex.trying.something.silly"

        $ dig @127.0.0.1 -p 10053 TXT +short rex.trying.something.silly
        "# Woohoo!"
        "This actually works?!"

        $ dig @127.0.0.1 -p 10053 TXT +short rex.search.silly
        "# Search results for: silly"
        "rex.trying.something.silly # Woohoo!"

        $ dig @127.0.0.1 -p 10053 TXT +short rex.trying.something.silly.comment.this.is.going.too.far
        "Posted:"
        "this is going too far"
    """
    _pattern = 'rex'
    _routes = {}

    def _dynamic_response_required(self, query):
        """
        Check the query to determine if a dynamic response is required.
        """
        if query.type == dns.TXT:
            labels = str(query.name.name, 'utf-8').split('.')
            if labels[0].startswith(self._pattern):
                return True
        return False

    def _compose_answer(self, name, response):
        response = response.replace('\n', '')
        response = response.replace('\r', '')
        payload = dns.Record_TXT(bytes(response, 'utf-8'))
        answer = dns.RRHeader(
            name=name,
            payload=payload,
            type=dns.TXT,
        )
        return answer

    def _do_dynamic_response(self, query):
        """
        Calculate the response to a query.
        """
        name = str(query.name.name, 'utf-8')
        path = '.'.join(name.split('.')[1:])
        response = self.route_to(path)
        if isinstance(response, str):
            response = [response]
        answers = [self._compose_answer(name, line) for line in response if line.strip()]
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

    def route(self, path):
        def wrapper(func):
            self._routes.update({path: func})

            def wrapped(path_):
                return func(path_)

            return wrapped

        return wrapper

    def route_to(self, path):
        if path in self._routes:
            return self._routes[path](path)
        for _path in self._routes:
            if path.startswith(_path):
                return self._routes[_path](path)
        if '*' in self._routes:
            return self._routes['*'](path)
        return 'Not found.'


def sanitize(file_name):
    file_name = file_name.replace('.txt', '')
    post_name = file_name.split('-').pop()
    return post_name


def is_recent(file_name):
    pdate = re.match('(\d\d\d\d)(\d\d)(\d\d)', file_name.split('-')[0])
    g = pdate.groups()
    post_date = '{}-{}-{}'.format(g[0], g[1], g[2])
    post_date = arrow.get(post_date)
    if post_date.shift(days=30) > arrow.utcnow():
        return True
    return False


def read_post(file_path):
    with open(file_path, 'r') as infile:
        return infile.readlines()


def find_and_read_post(post_path):
    try:
        for root, dirs, files in os.walk('posts'):
            for file_name in files:
                if post_path in file_name:
                    return read_post(os.path.join(root, file_name))
    except:
        pass
    return 'Not found.'


txtrex = TxtRex()


@txtrex.route('index')
def index(path):
    response = ['Latest: rex.latest', 'Recent:']
    posts = []

    for root, dirs, files in os.walk('posts'):
        posts = ['    rex.' + sanitize(p) for p in reversed(sorted(files)) if is_recent(p)]
        if 'comments' in dirs:
            dirs.remove('comments')
    return response + posts


@txtrex.route('latest')
def latest(path):
    for root, dirs, files in os.walk('posts'):
        latest_post = sorted(files).pop()
        return read_post(os.path.join(root, latest_post))


@txtrex.route('*')
def latest(path):
    return find_and_read_post(path)


def main():
    """
    Run the server.
    """
    factory = server.DNSServerFactory(
        clients=[txtrex, client.Resolver(resolv='/etc/resolv.conf')]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)

    reactor.run()


if __name__ == '__main__':
    raise SystemExit(main())
