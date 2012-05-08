package edu.berkeley.wsn;

import ch.ntb.usb.*;

import javax.swing.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

import javax.swing.event.*;
import javax.swing.border.*;
import com.rapplogic.*; 
import com.rapplogic.xbee.*;
import com.rapplogic.xbee.api.*;

public class DeviceCommands {
	public static interface CmdDefs { 
	    public static final byte PIC_RESET = 0x00;
	    public static final byte DEVICE_RESET = 0x01;
	
	    public static final byte FLASH_START_READ = 0x10;
	    public static final byte FLASH_CONTINUE_READ = 0x11;
	    public static final byte FLASH_STOP_READ = 0x12;
	    public static final byte FLASH_START_WRITE = 0x15;
	    public static final byte FLASH_CONTINUE_WRITE = 0x16;
	    public static final byte FLASH_STOP_WRITE = 0x17;
	
	    public static final byte XBEE_INFO = 0x20; // get information about # of configurations and current one
	    public static final byte XBEE_GET_CONFIG = 0x21; // dump a configuration
	    public static final byte XBEE_SAVE_CONFIG = 0x22; // provide a configuration
	    public static final byte XBEE_SET_CURRENT_CONFIG = 0x23; // start using a configuration
	    public static final byte XBEE_START_MONITOR = 0x24; // start monitoring events going through the UART
	    public static final byte XBEE_STOP_MONITOR = 0x25; //stop monitoring events going through the UART
	    public static final byte XBEE_CHECK_EVENT = 0x26;
	    
	    public static final byte ADC_READ_IMMEDIATE = 0x30;
	}
	
	CurrentMonitor parent;
	static int sequence_number = 1;
	
	XBee xbee = new XBee();
	
	
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
	
	public byte[] sendRcv(byte ... command) {
		return sendRcvPayload(command);
	}
	
	public synchronized byte[] sendRcvPayload(byte[] payload) {

		/*
		System.out.print("-> [");
		for ( byte b : payload ) {
			System.out.print(Integer.toHexString(0xFF&b)+", ");
		}
		System.out.println("]");
		*/
		sequence_number++;
		
		int num_segments = (payload.length-1) / (EP_SIZE-HEADER_SIZE) + 1;
		if (payload.length <= EP_SIZE-HEADER_SIZE) num_segments = 1;
		
		byte[] packet = new byte[EP_SIZE];
		// flush out backlog
		int backed_up = 0;
		try {
			while(true != false) {
				parent.dev.readBulk(parent.EP_IN, packet, EP_SIZE, 5, false);
				backed_up++;
			}
		} catch (ch.ntb.usb.USBTimeoutException exp) {
			//System.out.println(backed_up+" backed up packets");
		} catch (ch.ntb.usb.USBException exp) {
			exp.printStackTrace();
			return null;			
		}
		
		
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
		if ( fails ) return null;
		
		int seq_no = ((0xFF & packet[0]) | (0xFF & packet[1])<<8);
		if ( seq_no != sequence_number ) {
			System.err.println("Error: Sequence number mismatch. Expected "+sequence_number+" Got "+seq_no);
			fails = true;
		}
		if ( fails ) return null;
		
		int length = (0xFF & packet[2]);
		num_segments = (0xFF & packet[3]);
		if ( num_segments > 1 && length == 0) length = 256;
		byte[] retval = new byte[length];
		int cur_seg = (0xFF & packet[4]);
		int segments_recieved = 1<<cur_seg;
		if ( cur_seg == num_segments - 1)
			System.arraycopy(packet, HEADER_SIZE, retval, cur_seg * (EP_SIZE-HEADER_SIZE), (length-1) % (EP_SIZE-HEADER_SIZE) + 1);
		else
			System.arraycopy(packet, HEADER_SIZE, retval, cur_seg * (EP_SIZE-HEADER_SIZE), EP_SIZE-HEADER_SIZE);
		
		long time = System.currentTimeMillis();
		
		while ( System.currentTimeMillis() < time + 2000 && (segments_recieved+1) != (1<<num_segments) ) {
			try {
				xmit = parent.dev.readBulk(parent.EP_IN, packet, EP_SIZE, 1000, false);
				if (xmit!=EP_SIZE) fails = true;
			} catch (USBException exp) {
				exp.printStackTrace();
				fails = true;
			}
			if (fails) break;
			cur_seg = (0xFF & packet[4]);
			segments_recieved |= 1<<cur_seg;
			if ( cur_seg == num_segments - 1)
				System.arraycopy(packet, HEADER_SIZE, retval, cur_seg * (EP_SIZE-HEADER_SIZE), (length-1) % (EP_SIZE-HEADER_SIZE) + 1);
			else
				System.arraycopy(packet, HEADER_SIZE, retval, cur_seg * (EP_SIZE-HEADER_SIZE), EP_SIZE-HEADER_SIZE);
		}
		
		if ( fails ) {
			System.err.println("Communication error: Invalid packet detected");
			return null;
		}
		/*
		System.out.print("<- [");
		for ( byte b : retval ) {
			System.out.print(Integer.toHexString(0xFF&b)+", ");
		}
		System.out.println("]");
		*/
		
		return retval;
	}
	
	
}
