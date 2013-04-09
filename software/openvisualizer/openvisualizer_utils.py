
def formatBuf(buf):
    return '({0:>2}B) {1}'.format(
        len(buf),
        '-'.join(["%02x"%b for b in buf]),
    )

def formatIPv6Addr(addr):
    return ':'.join(["%02x"%b for b in addr])