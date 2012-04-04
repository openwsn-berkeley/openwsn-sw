package edu.berkeley.wsn;

import ch.ntb.usb.*;
import javax.swing.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

import javax.swing.event.*;
import javax.swing.border.*;



public class DeviceCommands {
	public static interface CmdDefs { 
	    public static final byte PIC_RESET = 0x00;
	    public static final byte DEVICE_RESET = 0x01;
	
	    public static final byte FLASH_READ = 0x10;
	    public static final byte FLASH_WRITE = 0x12;
	    public static final byte FLASH_ERASE = 0x13;
	
	    public static final byte XBEE_INFO = 0x20; // get information about # of configurations and current one
	    public static final byte XBEE_GET_CONFIG = 0x21; // dump a configuration
	    public static final byte XBEE_SAVE_CONFIG = 0x22; // provide a configuration
	    public static final byte XBEE_SET_CURRENT_CONFIG = 0x23; // start using a configuration
	    public static final byte XBEE_START_MONITOR = 0x24; // start monitoring events going through the UART
	    public static final byte XBEE_STOP_MONITOR = 0x25; //stop monitoring events going through the UART
	    public static final byte XBEE_EVENT_RECIEVED = 0x26;
	}
	
	CurrentMonitor parent;
	static int sequence_number = 1;
	
	
	public DeviceCommands(CurrentMonitor p) {
		parent = p;
	}
	
	public void pause(){
		try{
			Thread.sleep(100);
		} catch (Exception e) {}
	}
	
	static final int EP_SIZE = 64;
	static final int HEADER_SIZE = 3+2;
	
	public byte[] sendRcvPayload(byte[] payload) {
		sequence_number++;
		
		int num_segments = (payload.length-1) / (EP_SIZE-HEADER_SIZE) + 1;
		if (payload.length <= EP_SIZE-HEADER_SIZE) num_segments = 1;
		
		byte[] packet = new byte[EP_SIZE];
		packet[0] = (byte)(sequence_number & 0xFF); // PIC is little-endian
		packet[1] = (byte)((sequence_number>>8) & 0xFF);
		packet[2] = (byte)(payload.length);
		packet[3] = (byte)(0xFF&num_segments);

		int xmit = 0;
		
		for ( int i = 0; i < num_segments; i++ ) {
			int len = EP_SIZE-HEADER_SIZE;
			if (i == num_segments-1) {
				len = (payload.length-1) % ( EP_SIZE-HEADER_SIZE ) + 1;
			} 
			System.arraycopy(payload, i*(EP_SIZE-HEADER_SIZE), packet, HEADER_SIZE, len);
			packet[4] = (byte)i;
			try {
				xmit = parent.dev.writeBulk(parent.EP_OUT, packet, EP_SIZE, 500, false);
				pause();
				if (xmit!=EP_SIZE) return null;
			} catch (USBException exp) {
				exp.printStackTrace();
				return null;
			}
		}
		boolean fails = false;
		try {
			xmit = parent.dev.readBulk(parent.EP_IN, packet, EP_SIZE, 500, false);
			if (xmit!=EP_SIZE) fails = true;
		} catch (USBException exp) {
			exp.printStackTrace();
			fails = true;
		}
		
		if ( ((0xFF & packet[0]) | (0xFF & packet[1])<<8) != sequence_number ) {
			System.err.println("Error: Sequence number mismatch");
			fails = true;
		}
		int length = (0xFF & packet[2]);
		byte[] retval = new byte[length];
		num_segments = (0xFF & packet[3]);
		int cur_seg = (0xFF & packet[4]);
		int segments_recieved = 1<<cur_seg;
		if ( cur_seg == num_segments - 1)
			System.arraycopy(packet, cur_seg * (EP_SIZE-HEADER_SIZE), retval, 0, (length-1) % (EP_SIZE-HEADER_SIZE) + 1);
		else
			System.arraycopy(packet, cur_seg * (EP_SIZE-HEADER_SIZE), retval, 0, EP_SIZE-HEADER_SIZE);
		
		long time = System.currentTimeMillis();
		
		while ( System.currentTimeMillis() < time + 2000 && (segments_recieved+1) != (1<<num_segments) ) {
			try {
				xmit = parent.dev.readBulk(parent.EP_IN, packet, EP_SIZE, 500, false);
				if (xmit!=EP_SIZE) fails = true;
			} catch (USBException exp) {
				exp.printStackTrace();
				fails = true;
			}
			if (fails) break;
			cur_seg = (0xFF & packet[4]);
			segments_recieved |= 1<<cur_seg;
			if ( cur_seg == num_segments - 1)
				System.arraycopy(packet, cur_seg * (EP_SIZE-HEADER_SIZE), retval, 0, length % (EP_SIZE-HEADER_SIZE));
			else
				System.arraycopy(packet, cur_seg * (EP_SIZE-HEADER_SIZE), retval, 0, EP_SIZE-HEADER_SIZE);
		}
		
		if ( fails ) {
			System.err.println("Communication error: Invalid packet detected");
			return null;
		}
		
		return retval;
	}
	
	
}
