# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('openLbr')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

from openvisualizer.eventBus import eventBusClient
import threading
import openvisualizer.openvisualizer_utils as u

#============================ parameters ======================================

class OpenLbr(eventBusClient.eventBusClient):
    '''
    Class which is responsible for translating between 6LoWPAN and IPv6
    headers.
    
    This class implements the following RFCs:
    
    * *http://tools.ietf.org/html/rfc6282*
      Compression Format for IPv6 Datagrams over IEEE 802.15.4-Based Networks.
    * *http://tools.ietf.org/html/rfc2460* 
      Internet Protocol, Version 6 (IPv6) Specification
    * *http://tools.ietf.org/html/draft-thubert-6man-flow-label-for-rpl-03
       The IPv6 Flow Label within a RPL domain  
    '''
    #implementing http://tools.ietf.org/html/draft-thubert-6man-flow-label-for-rpl-03
    
    # http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml 
    IANA_PROTOCOL_IPv6ROUTE  = 43
    IANA_UDP                 = 17
    IANA_ICMPv6              = 58
    IANA_IPv6HOPHEADER       = 0
    # there is no IANA for IPV6 HEADER right now, we use NHC identifier for it
    IPV6_HEADER              = 0xEE #https://tools.ietf.org/html/rfc6282#section-4.2
    
    #hop header flags
    O_FLAG                   = 0x10
    R_FLAG                   = 0x08
    F_FLAG                   = 0x04
    I_FLAG                   = 0x02
    K_FLAG                   = 0x01
    FLAG_MASK                = 0x1F
    
    # Number of bytes in an IPv6 header.
    IPv6_HEADER_LEN          = 40
    
    IPHC_DISPATCH            = 3
    
    IPHC_TF_4B               = 0
    IPHC_TF_3B               = 1
    IPHC_TF_1B               = 2
    IPHC_TF_ELIDED           = 3

    IPHC_NH_INLINE           = 0
    IPHC_NH_COMPRESSED       = 1

    IPHC_HLIM_INLINE         = 0
    IPHC_HLIM_1              = 1
    IPHC_HLIM_64             = 2
    IPHC_HLIM_255            = 3 

    IPHC_CID_NO              = 0
    IPHC_CID_YES             = 1

    IPHC_SAC_STATELESS       = 0
    IPHC_SAC_STATEFUL        = 1

    IPHC_SAM_128B            = 0
    IPHC_SAM_64B             = 1
    IPHC_SAM_16B             = 2
    IPHC_SAM_ELIDED          = 3

    IPHC_M_NO                = 0
    IPHC_M_YES               = 1

    IPHC_DAC_STATELESS       = 0
    IPHC_DAC_STATEFUL        = 1

    IPHC_DAM_128B            = 0
    IPHC_DAM_64B             = 1
    IPHC_DAM_16B             = 2
    IPHC_DAM_ELIDED          = 3

    NHC_DISPATCH             = 0x0E
    
    NHC_EID_MASK             = 0x0E
    NHC_EID_HOPBYHOP         = 0
    NHC_EID_ROUTING          = 1
    NHC_EID_IPV6             = 7

    NHC_NH_INLINE            = 0
    NHC_NH_COMPRESSED        = 1

    PAGE_ONE_DISPATCH        = 0xF1
    MASK_6LoRH               = 0xE0
    ELECTIVE_6LoRH           = 0xA0
    CRITICAL_6LoRH           = 0x80

    TYPE_6LoRH_IP_IN_IP      = 0x06
    TYPE_6LoRH_RPI           = 0x05
    TYPE_6LoRH_RH3_0         = 0x00
    TYPE_6LoRH_RH3_1         = 0x01
    TYPE_6LoRH_RH3_2         = 0x02
    TYPE_6LoRH_RH3_3         = 0x03
    TYPE_6LoRH_RH3_4         = 0x04

    MASK_LENGTH_6LoRH_IPINIP = 0x1F
    
    #=== RPL source routing header (RFC6554)
    SR_FIR_TYPE              = 0x03
    
    #=== UDP Header compression (RFC6282) 
    
    NHC_UDP_MASK             = 0xF8
    NHC_UDP_ID               = 0xF0
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # store params
        self.stateLock            = threading.Lock()
        self.networkPrefix        = None
        self.dagRootEui64         = None
         
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name             = 'OpenLBR',
            registrations =  [
                {
                    'sender'   : self.WILDCARD, #signal from internet to the mesh network
                    'signal'   : 'v6ToMesh',
                    'callback' : self._v6ToMesh_notif
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'networkPrefix', #signal once a prefix is set.
                    'callback' : self._setPrefix_notif
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'infoDagRoot', #signal once a dagroot id is received
                    'callback' : self._infoDagRoot_notif, 
                },
                {
                    'sender'   : self.WILDCARD, #signal when a pkt from the mesh arrives and has to be forwarded to Internet (or local)
                    'signal'   : 'fromMote.data', #only to data (any), not status nor error
                    'callback' : self._meshToV6_notif, 
                },
            ]
        )
        
        # local variables
            
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== IPv6 -> 6LoWPAN
    
    def _v6ToMesh_notif(self,sender,signal,data):
        '''
        Converts a IPv6 packet into a 6LoWPAN packet.
        
        This function assumes there is a component listening on the EventBus
        which answers to the 'getSourceRoute' signal.
        
        This function dispatches the 6LoWPAN packet with signal 'bytesToMesh'.
        '''
        
        try:
            
            ipv6_bytes       = data
            
            # turn raw byte into dictionary of fields
            ipv6             = self.disassemble_ipv6(ipv6_bytes)

             # filter out multicast packets
            if ipv6['dst_addr'][0]==0xff:
                return
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug(self._format_IPv6(ipv6,ipv6_bytes))
            
            # convert IPv6 dictionary into 6LoWPAN dictionary
            lowpan           = self.ipv6_to_lowpan(ipv6)
            
            # add the source route to this destination
            if len(lowpan['dst_addr'])==16:
                dst_addr=lowpan['dst_addr'][8:]
            elif len(lowpan['dst_addr'])==8:
                dst_addr=lowpan['dst_addr']
            else:
                log.warning('unsupported address format {0}'.format(lowpan['dst_addr']))
                    
            lowpan['route'] = self._getSourceRoute(dst_addr)
            
            if len(lowpan['route'])<2:
                # no source route could be found
                log.warning('no source route to {0}'.format(lowpan['dst_addr']))
                # TODO: return ICMPv6 message
                return
            
            lowpan['route'].pop() #remove last as this is me.
            
            lowpan['nextHop'] = lowpan['route'][len(lowpan['route'])-1] #get next hop as this has to be the destination address, this is the last element on the list
            # turn dictionary of fields into raw bytes
            lowpan_bytes     = self.reassemble_lowpan(lowpan)
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug(self._format_lowpan(lowpan,lowpan_bytes))
            
            #print "output:"
            #print lowpan_bytes
            # dispatch
            self.dispatch(
                signal       = 'bytesToMesh',
                data         = (lowpan['nextHop'],lowpan_bytes),
            )
            
        except (ValueError,NotImplementedError) as err:
            log.error(err)
            pass
    
    
    def _meshToV6_notif(self,sender,signal,data):
        '''
        Converts a 6LowPAN packet into a IPv6 packet.
        
        This function dispatches the IPv6 packet with signal 'according to the destination address, protocol_type and port'.
        '''
        try:
            ipv6dic={}
            #build lowpan dictionary from the data
            ipv6dic = self.lowpan_to_ipv6(data)
            success = True
            dispatchSignal = None
            
            #read next header
            if ipv6dic['next_header']==self.IANA_IPv6HOPHEADER:
                #hop by hop header present, check flags and parse    
                if (ipv6dic['hop_flags'] & self.O_FLAG) == self.O_FLAG:
                    #error -- this packet has gone downstream somewhere.
                    log.error("detected possible downstream link on upstream route from {0}".format(",".join(str(c) for c in ipv6dic['src_addr'])))
                if (ipv6dic['hop_flags'] & self.R_FLAG) == self.R_FLAG:
                    #error -- loop in the route
                    log.error("detected possible loop on upstream route from {0}".format(",".join(str(c) for c in ipv6dic['src_addr'])))
                #skip the header and process the rest of the message.
                ipv6dic['next_header'] = ipv6dic['hop_next_header']
                
            #===================================================================

            if ipv6dic['next_header']==self.IPV6_HEADER:
                #ipv6 header (inner)
                ipv6dic_inner = {}
                # prasing the iphc inner header and get the next_header
                ipv6dic_inner = self.lowpan_to_ipv6([ipv6dic['pre_hop'],ipv6dic['payload']])
                ipv6dic['next_header'] = ipv6dic_inner['next_header']
                ipv6dic['payload'] = ipv6dic_inner['payload']
                ipv6dic['payload_length'] = ipv6dic_inner['payload_length']
                ipv6dic['src_addr'] = ipv6dic_inner['src_addr']
                if not ipv6dic.has_key('hop_limit'):
                    ipv6dic['hop_limit'] = ipv6dic_inner['hop_limit']
                ipv6dic['dst_addr'] = ipv6dic_inner['dst_addr']
                ipv6dic['flow_label'] = ipv6dic_inner['flow_label']
                
            if ipv6dic['next_header']==self.IANA_ICMPv6:
                #icmp header
                if len(ipv6dic['payload'])<5:
                    log.critical("wrong payload lenght on ICMPv6 packet {0}".format(",".join(str(c) for c in data)))
                    print "wrong payload lenght on ICMPv6 packet {0}".format(",".join(str(c) for c in data))
                    return
                
                
                ipv6dic['icmpv6_type']=ipv6dic['payload'][0]
                ipv6dic['icmpv6_code']=ipv6dic['payload'][1]
                ipv6dic['icmpv6_checksum']=ipv6dic['payload'][2:4]
                ipv6dic['app_payload']=ipv6dic['payload'][4:]
                
                #this function does the job
                dispatchSignal=(tuple(ipv6dic['dst_addr']),self.PROTO_ICMPv6,ipv6dic['icmpv6_type'])
                 
            elif ipv6dic['next_header']==self.IANA_UDP:
                #udp header -- can be compressed.. assume first it is not compressed.
                if len(ipv6dic['payload'])<5:
                    log.critical("wrong payload lenght on UDP packet {0}".format(",".join(str(c) for c in data)))
                    print "wrong payload lenght on UDP packet {0}".format(",".join(str(c) for c in data))
                    return
                
                if ipv6dic['payload'][0] & self.NHC_UDP_MASK==self.NHC_UDP_ID:
                    
                    oldUdp=ipv6dic['payload'][:5]
                    #re-arrange fields and inflate
                    newUdp = []
                    newUdp += oldUdp[1:3] # Source Port
                    newUdp += oldUdp[3:5] # Destination Port
                    length = 8+len(pkt[5:])
                    newUdp += [(length & 0xFF00) >> 8] # Length
                    newUdp += [(length & 0x00FF) >> 0]
                    idxCS = len(newUdp) # remember index of checksum
                    newUdp += [0x00,0x00] # Checksum (placeholder)
                    #append payload to compute crc again
                    newUdp += ipv6dic['payload'][5:] # data octets
                    
                    checksum = u.calculateCRC(newUdp)
                    #fill crc with the right value.
                    newUdp[idxCS] = checksum[0]
                    newUdp[idxCS+1] = checksum[1]
                    #keep fields for later processing if needed
                    ipv6dic['udp_src_port']=newUdp[:2]
                    ipv6dic['udp_dest_port']=newUdp[2:4]
                    ipv6dic['udp_length']=newUdp[4:6]
                    ipv6dic['udp_checksum']=newUdp[6:8]
                    ipv6dic['app_payload']=newUdp[8:]
                    
                    #substitute udp header by the uncompressed header.               
                    ipv6dic['payload'] =newUdp[:8] + ipv6dic['payload'][5:]
                else:
                    #No UDP header compressed    
                    ipv6dic['udp_src_port']=ipv6dic['payload'][:2]
                    ipv6dic['udp_dest_port']=ipv6dic['payload'][2:4]
                    ipv6dic['udp_length']=ipv6dic['payload'][4:6]
                    ipv6dic['udp_checksum']=ipv6dic['payload'][6:8]
                    ipv6dic['app_payload']=ipv6dic['payload'][8:]
                dispatchSignal=(tuple(ipv6dic['dst_addr']),self.PROTO_UDP,u.buf2int(ipv6dic['udp_dest_port']))
            
            #keep payload and app_payload in case we want to assemble the message later. 
            #ass source address is being retrieved from the IPHC header, the signal includes it in case
            #receiver such as RPL DAO processing needs to know the source.               
            
            success = self._dispatchProtocol(dispatchSignal,(ipv6dic['src_addr'],ipv6dic['app_payload']))    
            
            if success:
                return
            
            # assemble the packet and dispatch it again as nobody answer 
            ipv6pkt=self.reassemble_ipv6_packet(ipv6dic)       
            
            self.dispatch('v6ToInternet',ipv6pkt)
            
        except (ValueError,NotImplementedError) as err:
            log.error(err)
            pass
    
    def disassemble_ipv6(self,ipv6):
        '''
        Turn byte array representing IPv6 packets into into dictionary
        of fields.
        
        See http://tools.ietf.org/html/rfc2460#page-4.
        
        :param ipv6: [in] Byte array representing an IPv6 packet.
        
        :raises: ValueError when some part of the process is not defined in
            the standard.
        :raises: NotImplementedError when some part of the process is defined in
            the standard, but not implemented in this module.
        
        :returns: A dictionary of fields.
        '''
        
        if len(ipv6)<self.IPv6_HEADER_LEN:
            raise ValueError('Packet too small ({0} bytes) no space for IPv6 header'.format(len(ipv6)))
        
        returnVal                      = {}
        returnVal['version']           = ipv6[0] >> 4
        if returnVal['version']!=6:
            raise ValueError('Not an IPv6 packet, version=={0}'.format(returnVal['version']))
        
        returnVal['traffic_class']     = ((ipv6[0] & 0x0F) << 4) + (ipv6[1] >> 4)
        returnVal['flow_label']        = ((ipv6[1] & 0x0F) << 16) + (ipv6[2] << 8) + ipv6[3]
        returnVal['payload_length']    = u.buf2int(ipv6[4:6])
        returnVal['next_header']       = ipv6[6]
        returnVal['hop_limit']         = ipv6[7]
        returnVal['src_addr']          = ipv6[8:8+16]
        returnVal['dst_addr']          = ipv6[24:24+16]
        returnVal['payload']           = ipv6[40:]
        
        return returnVal
    
    def ipv6_to_lowpan(self,ipv6):
        '''
        Compact IPv6 header into 6LowPAN header.
        
        :param ipv6: [in] A disassembled IPv6 packet.
        
        :raises: ValueError when some part of the process is not defined in
            the standard.
        :raises: NotImplementedError when some part of the process is defined in
            the standard, but not implemented in this module.
        
        :returns: A disassembled 6LoWPAN packet.
        '''
        
        # header
        lowpan = {}
        
        # tf
        if ipv6['traffic_class']!=0:
            raise NotImplementedError('traffic_class={0} unsupported'.format(ipv6['traffic_class']))
        # comment the flow_label check as it's zero in 6lowpan network. See follow RFC:
        # https://tools.ietf.org/html/rfc4944#section-10.1  
        # if ipv6['flow_label']!=0:
            # raise NotImplementedError('flow_label={0} unsupported'.format(ipv6['flow_label']))
        lowpan['tf']         = []
        
        # nh
        lowpan['nh']         = [ipv6['next_header']]
        
        # hlim
        lowpan['hlim']       = [ipv6['hop_limit']]
        
        # cid
        lowpan['cid']        = []
        
        # src_addr
        lowpan['src_addr']   = ipv6['src_addr']
        
        # dst_addr
        lowpan['dst_addr']   = ipv6['dst_addr']
        
        # payload
        lowpan['payload']    = ipv6['payload']
        
        # join
        return lowpan
    
    def reassemble_lowpan(self,lowpan):
        '''
        Turn dictionary of 6LoWPAN header fields into byte array.
        
        :param lowpan: [in] dictionary of fields representing a 6LoWPAN header.
        
        :returns: A list of bytes representing the 6LoWPAN packet.
        '''
        returnVal            = []

        # the 6lowpan packet contains 4 parts
        # 1. Page Dispatch (page 1)
        # 2. RH3 6LoRH(s)
        # 3. RPI 6LoRH (maybe elided)
        # 4. IPinIP 6LoRH (maybe elided)
        # 5. IPHC inner header
        
        # ===================== 1. Page Dispatch (page 1) =====================

        returnVal += [self.PAGE_ONE_DISPATCH]

        if lowpan['src_addr'][:8] != [187, 187, 0, 0, 0, 0, 0, 0]:
            compressReference = [187, 187, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        else:
            compressReference = lowpan['src_addr']


        # destination address
        if len(lowpan['route'])>1:
            # source route needed, get prefix from compression Reference
            if len(compressReference)==16:
                prefix=compressReference[:8]

            # =======================3. RH3 6LoRH(s) ============================== 
            sizeUnitType = 0xff
            size     = 0
            hopList  = []

            for hop in list(reversed(lowpan['route'][1:])):
                size += 1
                if compressReference[-8:-1] == hop[-8:-1]:
                    if sizeUnitType != 0xff:
                        if  sizeUnitType != self.TYPE_6LoRH_RH3_0:
                            returnVal += [self.CRITICAL_6LoRH|(size-2),sizeUnitType]
                            returnVal += hopList
                            size = 1
                            sizeUnitType = self.TYPE_6LoRH_RH3_0
                            hopList = [hop[-1]]
                            compressReference = hop
                        else:
                            hopList += [hop[-1]]
                            compressReference = hop
                    else:
                        sizeUnitType = self.TYPE_6LoRH_RH3_0
                        hopList += [hop[-1]]
                        compressReference = hop
                elif compressReference[-8:-2] == hop[-8:-2]:
                    if sizeUnitType != 0xff:
                        if  sizeUnitType != self.TYPE_6LoRH_RH3_1:
                            returnVal += [self.CRITICAL_6LoRH|(size-2),sizeUnitType]
                            returnVal += hopList
                            size = 1
                            sizeUnitType = self.TYPE_6LoRH_RH3_1
                            hopList = hop[-2:]
                            compressReference = hop
                        else:
                            hopList += hop[-2:]
                            compressReference = hop
                    else:
                        sizeUnitType = self.TYPE_6LoRH_RH3_1
                        hopList += hop[-2:]
                        compressReference = hop
                elif compressReference[-8:-4] == hop[-8:-4]:
                    if sizeUnitType != 0xff:
                        if  sizeUnitType != self.TYPE_6LoRH_RH3_2:
                            returnVal += [self.CRITICAL_6LoRH|(size-2),sizeUnitType]
                            returnVal += hopList
                            size = 1
                            sizeUnitType = self.TYPE_6LoRH_RH3_2
                            hopList = hop[-4:]
                            compressReference = hop
                        else:
                            hopList += hop[-4:]
                            compressReference = hop
                    else:
                        sizeUnitType = self.TYPE_6LoRH_RH3_2
                        hopList += hop[-4:]
                        compressReference = hop
                else:
                    if sizeUnitType != 0xff:
                        if  sizeUnitType != self.TYPE_6LoRH_RH3_3:
                            returnVal += [self.CRITICAL_6LoRH|(size-2),sizeUnitType]
                            returnVal += hopList
                            size = 1
                            sizeUnitType = self.TYPE_6LoRH_RH3_3
                            hopList = hop
                            compressReference = hop
                        else:
                            hopList += hop
                            compressReference = hop
                    else:
                        sizeUnitType = self.TYPE_6LoRH_RH3_3
                        hopList += hop
                        compressReference = hop

            returnVal += [self.CRITICAL_6LoRH|(size-1),sizeUnitType]
            returnVal += hopList

        # ===================== 2. IPinIP 6LoRH ===============================

        if lowpan['src_addr'][:8] != [187, 187, 0, 0, 0, 0, 0, 0]:
            # add RPI 
            # TBD
            flag = self.O_FLAG | self.I_FLAG | self.K_FLAG
            senderRank = 0 # rank of dagroot
            returnVal += [self.CRITICAL_6LoRH | flag,self.TYPE_6LoRH_RPI,senderRank]
            # ip in ip 6lorh
            l = 1
            returnVal += [self.ELECTIVE_6LoRH | l,self.TYPE_6LoRH_IP_IN_IP]
            returnVal += lowpan['hlim']

            compressReference = [187, 187, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        else:
            compressReference = lowpan['src_addr']
 
        # ========================= 4. IPHC inner header ======================
        # Byte1: 011(3b) TF(2b) NH(1b) HLIM(2b)
        if len(lowpan['tf'])==0:
            tf               = self.IPHC_TF_ELIDED
        else:
            raise NotImplementedError()
        # next header is in NHC format
        nh               = self.IPHC_NH_INLINE
        if   lowpan['hlim']==1:
            hlim             = self.IPHC_HLIM_1
            lowpan['hlim'] = []
        elif lowpan['hlim']==64:
            hlim             = self.IPHC_HLIM_64
            lowpan['hlim'] = []
        elif lowpan['hlim']==255:
            hlim             = self.IPHC_HLIM_255
            lowpan['hlim'] = []
        else:
            hlim             = self.IPHC_HLIM_INLINE
        returnVal           += [(self.IPHC_DISPATCH<<5) + (tf<<3) + (nh<<2) + (hlim<<0)]
        
        # Byte2: CID(1b) SAC(1b) SAM(2b) M(1b) DAC(2b) DAM(2b)
        if len(lowpan['cid'])==0:
            cid              = self.IPHC_CID_NO
        else:
            cid              = self.IPHC_CID_YES
        sac                  = self.IPHC_SAC_STATELESS
        if   len(lowpan['src_addr'])==128/8:
            sam              = self.IPHC_SAM_128B
        elif len(lowpan['src_addr'])==64/8:
            sam              = IPHC_SAM_64B
        elif len(lowpan['src_addr'])==16/8:
            sam              = self.IPHC_SAM_16B
        elif len(lowpan['src_addr'])==0:
            sam              = self.IPHC_SAM_ELIDED
        else:
            raise SystemError()
        dac                  = self.IPHC_DAC_STATELESS
        m                    = self.IPHC_M_NO
        if   len(lowpan['dst_addr'])==128/8:
            dam              = self.IPHC_DAM_128B
        elif len(lowpan['dst_addr'])==64/8:
            dam              = self.IPHC_DAM_64B
        elif len(lowpan['dst_addr'])==16/8:
            dam              = self.IPHC_DAM_16B
        elif len(lowpan['dst_addr'])==0:
            dam              = self.IPHC_DAM_ELIDED
        else:
            raise SystemError()
        returnVal           += [(cid << 7) + (sac << 6) + (sam << 4) + (m << 3) + (dac << 2) + (dam << 0)]

        # tf
        returnVal           += lowpan['tf']

        # nh
        returnVal           += lowpan['nh']
        
        # hlim
        returnVal           += lowpan['hlim']
        
        # cid
        returnVal           += lowpan['cid']

        # src_addr
        returnVal           += lowpan['src_addr']
        
        # dst_addr
        returnVal           += lowpan['dst_addr']

        # payload
        returnVal           += lowpan['payload']

        return returnVal
    
    #===== 6LoWPAN -> IPv6
    
    def lowpan_to_ipv6(self,data):
                
        pkt_ipv6 = {}
        mac_prev_hop=data[0]
        pkt_lowpan=data[1]

        if pkt_lowpan[0]==self.PAGE_ONE_DISPATCH:
            ptr = 1
            if pkt_lowpan[ptr] & self.MASK_6LoRH == self.CRITICAL_6LoRH and pkt_lowpan[ptr+1] == self.TYPE_6LoRH_RPI:
                # next header is RPI (hop by hop)
                pkt_ipv6['next_header'] = self.IANA_IPv6HOPHEADER
                pkt_ipv6['hop_flags'] = pkt_lowpan[ptr] & self.FLAG_MASK
                ptr = ptr+2

                if pkt_ipv6['hop_flags'] & self.I_FLAG==0:
                    pkt_ipv6['hop_rplInstanceID'] = pkt_lowpan[ptr]
                    ptr += 1
                else:
                    pkt_ipv6['hop_rplInstanceID'] = 0
               
                if pkt_ipv6['hop_flags'] & self.K_FLAG==0:
                    pkt_ipv6['hop_senderRank'] = ((pkt_lowpan[ptr]) << 8) + ((pkt_lowpan[ptr+1]) << 0)
                    ptr += 2
                else:
                    pkt_ipv6['hop_senderRank'] = (pkt_lowpan[ptr]) << 8
                    ptr += 1
                # iphc is following after hopbyhop header
                pkt_ipv6['hop_next_header'] = self.IPV6_HEADER

                if pkt_lowpan[ptr] & self.MASK_6LoRH == self.ELECTIVE_6LoRH and pkt_lowpan[ptr+1] == self.TYPE_6LoRH_IP_IN_IP:
                    # ip in ip encapsulation
                    length = pkt_lowpan[ptr] & self.MASK_LENGTH_6LoRH_IPINIP
                    pkt_ipv6['hop_limit'] = pkt_lowpan[ptr+2]
                    ptr += 3
                    if length == 1:
                        pkt_ipv6['src_addr'] = [0xbb,0xbb,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01]
                    elif length == 9:
                        pkt_ipv6['src_addr'] = self.networkPrefix + pkt_lowpan[ptr:ptr+8]
                        ptr += 8
                    elif length == 17:
                        pkt_ipv6['src_addr'] = pkt_lowpan[ptr:ptr+16]
                        ptr += 16
                    else:
                        log.error("ERROR wrong length of encapsulate")
            else:
                log.error("ERROR no support this type of 6LoRH yet")
        else:
            ptr = 2
            if (pkt_lowpan[0] >> 5) != 0x03:
                log.error("ERROR not a 6LowPAN packet")
                return   
        
            # tf
            tf = ((pkt_lowpan[0]) >> 3) & 0x03
            if tf == self.IPHC_TF_3B:
                pkt_ipv6['flow_label'] = ((pkt_lowpan[ptr]) << 16) + ((pkt_lowpan[ptr+1]) << 8) + ((pkt_lowpan[ptr+2]) << 0)
                ptr = ptr + 3
            elif tf == self.IPHC_TF_ELIDED:
                pkt_ipv6['flow_label'] = 0
            else:
                log.error("Unsupported or wrong tf")
            # nh
            nh = ((pkt_lowpan[0]) >> 2) & 0x01
            if nh == self.IPHC_NH_INLINE:
                pkt_ipv6['next_header'] = (pkt_lowpan[ptr])
                ptr = ptr+1
            elif nh == self.IPHC_NH_COMPRESSED:
                # log.error("unsupported nh==IPHC_NH_COMPRESSED")
                # the next header will be retrieved later
                pass
            else:
                log.error("wrong nh field nh="+str(nh))
                
            # hlim
            hlim = (pkt_lowpan[0]) & 0x03
            if hlim == self.IPHC_HLIM_INLINE:
                pkt_ipv6['hop_limit'] = (pkt_lowpan[ptr])
                ptr = ptr+1
            elif hlim == self.IPHC_HLIM_1:
                pkt_ipv6['hop_limit'] = 1
            elif hlim == self.IPHC_HLIM_64:
                pkt_ipv6['hop_limit'] = 64
            elif hlim == self.IPHC_HLIM_255:
                pkt_ipv6['hop_limit'] = 255
            else:
                log.error("wrong hlim=="+str(hlim))
            # sam
            sam = ((pkt_lowpan[1]) >> 4) & 0x03
            if sam == self.IPHC_SAM_ELIDED:
                #pkt from the previous hop
                pkt_ipv6['src_addr'] = self.networkPrefix + mac_prev_hop
                
            elif sam == self.IPHC_SAM_16B:
                a1 = pkt_lowpan[ptr]
                a2 = pkt_lowpan[ptr+1]
                ptr = ptr+2
                s = ''.join(['\x00','\x00','\x00','\x00','\x00','\x00',a1,a2])
                pkt_ipv6['src_addr'] = self.networkPrefix+s
        
            elif sam == self.IPHC_SAM_64B:
                pkt_ipv6['src_addr'] = self.networkPrefix+pkt_lowpan[ptr:ptr+8]
                ptr = ptr + 8
            elif sam == self.IPHC_SAM_128B:
                pkt_ipv6['src_addr'] = pkt_lowpan[ptr:ptr+16]
                ptr = ptr + 16
            else:
                log.error("wrong sam=="+str(sam))
                
            # dam
            dam = ((pkt_lowpan[1]) & 0x03)
            if dam == self.IPHC_DAM_ELIDED:
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("IPHC_DAM_ELIDED this packet is for the dagroot!")
                pkt_ipv6['dst_addr'] = self.networkPrefix+self.dagRootEui64
            elif dam == self.IPHC_DAM_16B:
                a1 = pkt_lowpan[ptr]
                a2 = pkt_lowpan[ptr+1]
                ptr = ptr+2
                s = ''.join(['\x00','\x00','\x00','\x00','\x00','\x00',a1,a2])
                pkt_ipv6['dst_addr'] = self.networPrefix+s
            elif dam == self.IPHC_DAM_64B:
                pkt_ipv6['dst_addr'] = self.networkPrefix+pkt_lowpan[ptr:ptr+8]
                ptr = ptr + 8
            elif dam == self.IPHC_DAM_128B:
                pkt_ipv6['dst_addr'] = pkt_lowpan[ptr:ptr+16]
                ptr = ptr + 16
            else:
                log.error("wrong dam=="+str(dam))

            if nh == self.IPHC_NH_COMPRESSED:
                if ((pkt_lowpan[ptr] >> 4) & 0x0f) == self.NHC_DISPATCH:
                    eid = (pkt_lowpan[ptr] & self.NHC_EID_MASK) >> 1
                    if eid == self.NHC_EID_HOPBYHOP:
                        pkt_ipv6['next_header'] = self.IANA_IPv6HOPHEADER
                    elif eid == self.NHC_EID_IPV6:
                        pkt_ipv6['next_header'] = self.IPV6_HEADER
                    else:
                        log.error("wrong NH_EID=="+str(eid))
            
            #hop by hop header 
            #composed of NHC, NextHeader,Len + Rpl Option
            if pkt_ipv6['next_header'] == self.IANA_IPv6HOPHEADER:
                 pkt_ipv6['hop_nhc'] = pkt_lowpan[ptr]
                 ptr = ptr+1
                 if (pkt_ipv6['hop_nhc'] & 0x01) == 0:
                    pkt_ipv6['hop_next_header'] = pkt_lowpan[ptr]
                    ptr = ptr+1
                 else :
                    # the next header filed will be elided
                    pass
                 pkt_ipv6['hop_hdr_len'] = pkt_lowpan[ptr]
                 ptr = ptr+1
                 #start of RPL Option
                 pkt_ipv6['hop_optionType'] = pkt_lowpan[ptr]
                 ptr = ptr+1
                 pkt_ipv6['hop_optionLen'] = pkt_lowpan[ptr]
                 ptr = ptr+1
                 pkt_ipv6['hop_flags'] = pkt_lowpan[ptr]
                 ptr = ptr+1
                 pkt_ipv6['hop_rplInstanceID'] = pkt_lowpan[ptr]
                 ptr = ptr+1
                 pkt_ipv6['hop_senderRank'] = ((pkt_lowpan[ptr]) << 8) + ((pkt_lowpan[ptr+1]) << 0)
                 ptr = ptr+2
                 #end RPL option
                 if (pkt_ipv6['hop_nhc'] & 0x01) == 1:
                     if ((pkt_lowpan[ptr]>>1) & 0x07) == self.NHC_EID_IPV6:
                         pkt_ipv6['hop_next_header'] = self.IPV6_HEADER

        # payload
        pkt_ipv6['version']        = 6
        pkt_ipv6['traffic_class']  = 0
        pkt_ipv6['payload']        = pkt_lowpan[ptr:len(pkt_lowpan)]

        pkt_ipv6['payload_length'] = len(pkt_ipv6['payload'])
        pkt_ipv6['pre_hop']        = mac_prev_hop
        return pkt_ipv6
    
    def reassemble_ipv6_packet(self, pkt):
        pktw = [((6 << 4) + (pkt['traffic_class'] >> 4)),
                (((pkt['traffic_class'] & 0x0F) << 4) + (pkt['flow_label'] >> 16)),
                ((pkt['flow_label'] >> 8) & 0x00FF),
                (pkt['flow_label'] & 0x0000FF),
                (pkt['payload_length'] >> 8),
                (pkt['payload_length'] & 0x00FF),
                (pkt['next_header']),
                (pkt['hop_limit'])]
        for i in range(0,16):
            pktw.append( (pkt['src_addr'][i]) )
        for i in range(0,16):
            pktw.append( (pkt['dst_addr'][i]) ) 
        
        return pktw + pkt['payload']
        
    
    
    #======================== helpers =========================================
    
    #===== source route
    
    def _getSourceRoute(self,destination):
        returnVal = self._dispatchAndGetResult(
            signal       = 'getSourceRoute',
            data         = destination,
        )
        return returnVal
    
    def _setPrefix_notif(self,sender,signal, data):
        '''
        Record the network prefix.
        '''
        with self.stateLock:
            self.networkPrefix    = data  
            log.info('Set network prefix  {0}'.format(u.formatIPv6Addr(data)))
            
            
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        Record the DAGroot's EUI64 address.
        '''
        
        if data['isDAGroot']==1:
            with self.stateLock:
                self.dagRootEui64     = data['eui64'][:]

#===== formatting
    
    def _format_IPv6(self,ipv6,ipv6_bytes):
        output  = []
        output += ['']
        output += ['']
        output += ['============================= IPv6 packet =====================================']
        output += ['']
        output += ['Version:           {0}'.format(ipv6['version'])]
        output += ['Traffic class:     {0}'.format(ipv6['traffic_class'])]
        output += ['Flow label:        {0}'.format(ipv6['flow_label'])]
        output += ['Payload length:    {0}'.format(ipv6['payload_length'])]
        output += ['Hop Limit:         {0}'.format(ipv6['hop_limit'])]
        output += ['Next header:       {0}'.format(ipv6['next_header'])]
        output += ['Source Addr.:      {0}'.format(u.formatIPv6Addr(ipv6['src_addr']))]
        output += ['Destination Addr.: {0}'.format(u.formatIPv6Addr(ipv6['dst_addr']))]
        output += ['Payload:           {0}'.format(u.formatBuf(ipv6['payload']))]
        output += ['']
        output += [self._formatWireshark(ipv6_bytes)]
        output += ['']
        return '\n'.join(output)
    
    def _format_lowpan(self,lowpan,lowpan_bytes):
        output          = []
        output         += ['']
        output         += ['']
        output         += ['============================= lowpan packet ===================================']
        output         += ['']
        output         += ['tf:                {0}'.format(u.formatBuf(lowpan['tf']))]
        output         += ['nh:                {0}'.format(u.formatBuf(lowpan['nh']))]
        output         += ['hlim:              {0}'.format(u.formatBuf(lowpan['hlim']))]
        output         += ['cid:               {0}'.format(u.formatBuf(lowpan['cid']))]
        output         += ['src_addr:          {0}'.format(u.formatBuf(lowpan['src_addr']))]
        output         += ['dst_addr:          {0}'.format(u.formatBuf(lowpan['dst_addr']))]
        if 'route' in lowpan:
            output     += ['source route:']
            for hop in lowpan['route']:
                output += [' - {0}'.format(u.formatAddr(hop))]
        output         += ['payload:           {0}'.format(u.formatBuf(lowpan['payload']))]
        output += ['']
        output += [self._formatWireshark(lowpan_bytes)]
        output += ['']
        return '\n'.join(output)
    
    def _formatWireshark(self,pkt):
        NUM_BYTES_PER_LINE        = 16
        
        output                    = []
        index                     = 0
        while index<len(pkt):
            this_line             = []
            
            # get the bytes for this line
            bytes                 = pkt[index:index+NUM_BYTES_PER_LINE]
            
            # print the header
            this_line            += ['%06x '%index]
            
            # print the bytes (gather the end_chars)
            end_chars             = []
            end_chars            += ['  ']
            for b in bytes:
                # print the bytes
                this_line        += [' %02x'%b]
                # gather the end_chars
                if 32 < b < 127:
                    end_chars    += [chr(b)]
                else:
                    end_chars    += ['.']
            
            # pad
            for _ in range(len(bytes),NUM_BYTES_PER_LINE):
                this_line        += ['   ']
            
            # print the end_chars
            this_line            += end_chars
            
            # store the line
            this_line             = ''.join(this_line)
            output               += [this_line]
            
            # increment index
            index                += NUM_BYTES_PER_LINE
        
        return '\n'.join(output)
