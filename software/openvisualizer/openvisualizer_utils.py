
def formatStringBuf(buf):
    return '-'.join(["%02x" % ord(b) for b in buf])

def formatBuf(buf):
    return '({0:>2}B) {1}'.format(
        len(buf),
        '-'.join(["%02x" % b for b in buf]),
    )

def formatIPv6Addr(addr):
    return ':'.join(["%02x" % b for b in addr])


def calculateCRC(self, payload, length):  
    temp_checksum = [0] * 2
        
    self.oneComplementSum(temp_checksum, payload, len(payload));
    temp_checksum[0] ^= 0xFF;
    temp_checksum[1] ^= 0xFF;
        
    # log
    #log.debug("checksum calculated {0:x},{1:x}".format(temp_checksum[0], temp_checksum[1]))
       
    return temp_checksum
    

def oneComplementSum(self, checksum, payload, length):
    sum = 0xFFFF & (checksum[0] << 8 | checksum[1])
    i = length
        
    while (i > 1):
        sum += 0xFFFF & (payload[length - i] << 8 | (payload[length - i + 1]))
        i -= 2
            
    if (i):
        sum += (0xFF & payload[length - 1]) << 8
   
    while (sum >> 16):
        sum = (sum & 0xFFFF) + (sum >> 16)
   
    checksum[0] = (sum >> 8) & 0xFF
    checksum[1] = sum & 0xFF
