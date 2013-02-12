
def formatAddress(addr):
    return '-'.join(['%02x'%b for b in addr])

def formatBuf(buf):
    return ''.join(['%02x'%b for b in buf])