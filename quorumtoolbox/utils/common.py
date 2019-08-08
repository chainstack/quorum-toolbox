from furl import furl


def make_url(address):
    address = furl(address)

    if not address.host:
        address.set(host=str(address))
        address.set(path='')
    if not address.scheme and not address.port:
        address.set(port=8545)
    if not address.scheme:
        address.set(scheme='http')

    return str(address)
