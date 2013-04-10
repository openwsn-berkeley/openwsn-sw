
#===== formatting

def formatStringBuf(buf):
    return '-'.join(["%02x" % ord(b) for b in buf])

def formatBuf(buf):
    return '({0:>2}B) {1}'.format(
        len(buf),
        '-'.join(["%02x" % b for b in buf]),
    )

def formatIPv6Addr(addr):
    return ':'.join(["%02x" % b for b in addr])
    
def formatAddr(addr):
    return '-'.join(["%02x" % b for b in addr])

#===== CRC

def calculateCRC(self, payload):  
    
    checksum       = [0x00]*2
    
    sum            = 0xFFFF & (checksum[0] << 8 | checksum[1])
    i              = len(payload)
    while (i > 1):
        sum       += 0xFFFF & (payload[length-i] << 8 | (payload[length-i+1]))
        i         -= 2
    if i:
        sum       += (0xFF & payload[length - 1]) << 8
    while (sum >> 16):
        sum        = (sum & 0xFFFF) + (sum >> 16)
    
    checksum[0]    = (sum >> 8) & 0xFF
    checksum[1]    = sum & 0xFF
    
    checksum[0]   ^= 0xFF;
    checksum[1]   ^= 0xFF;
    
    return checksum
