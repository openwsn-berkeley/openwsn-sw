
def formatBuf(buf):
    return '-'.join(["%02x"%ord(b) for b in buf])