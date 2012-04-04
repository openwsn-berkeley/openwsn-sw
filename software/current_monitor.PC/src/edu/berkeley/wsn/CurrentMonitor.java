package edu.berkeley.wsn;

import ch.ntb.usb.*;
import javax.swing.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

import javax.swing.event.*;
import javax.swing.border.*;



public class CurrentMonitor  extends JFrame{
	private static final long serialVersionUID = 2L;
	public static final short VID = 0x04D8;
	public static final short PID = 0x000A;
	public static final int EP_IN = 0x83;
	public static final int EP_OUT = 0x03;
	
	// UI components
	JButton connect_button = new JButton("Connect to Device");
	{
		connect_button.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				connectToDevice();
			}
		});
	}
	
	JPanel connect_tab = new JPanel(new BorderLayout());
	{
		Box h1 = Box.createHorizontalBox();
		h1.add(connect_button);
		h1.add(Box.createHorizontalGlue());
		connect_tab.add(h1,BorderLayout.NORTH);
	}
	
	
	XBeePanel xbee_tab = new XBeePanel(this);


	JTabbedPane tabber = new JTabbedPane(JTabbedPane.TOP);
	{
		tabber.add(connect_tab,"Connection");
		tabber.add(xbee_tab,"Xbee configurations");
	}
	
	static JTextArea console = new JTextArea(10,5);
	static JScrollPane console_scroller = new JScrollPane(console);
	{
		console_scroller.setBorder(new TitledBorder("Messages"));
		console.setEditable(false);
		((javax.swing.text.DefaultCaret)(console.getCaret())).setUpdatePolicy(javax.swing.text.DefaultCaret.ALWAYS_UPDATE);
	}

	
	
	// Our components
	static Device dev;

	
	static void error(String message) {
		msg("!!! "+message+" !!!");
		JOptionPane.showMessageDialog(null, message, "Error", JOptionPane.ERROR_MESSAGE);
	}
	
	static void msg(String message) {
		console.append(message+"\n");
		console_scroller.getVerticalScrollBar().setValue(100000);
	}

	public CurrentMonitor() {
		getContentPane().add(tabber,BorderLayout.CENTER);
		getContentPane().add(console_scroller,BorderLayout.SOUTH);
		
		setDefaultCloseOperation(EXIT_ON_CLOSE);
		setSize(800,600);
		setTitle("Current Monitor configurator");
		setVisible(true);
	}

	private void connectToDevice() {
		try {
			msg("Connecting to device at 0x"+Integer.toHexString(VID)+",0x"+Integer.toHexString(PID));
			dev = USB.getDevice(VID,PID);
			dev.open(1, 2, 0);
			

		} catch (USBException exp) {
			error(""+exp);
		}
	}
	
	
    public static void main(String[] args) throws Exception{
    	
    	new CurrentMonitor();
    	/*
            byte led_on[] = new byte[64];
            led_on[0] = (byte)0x80;
            byte read_button[] = new byte[64];
            read_button[0] = (byte)0x81;
            byte incoming[] = new byte[64];
            
            Device dev = USB.getDevice((short)0x04D8,(short)0x000A );
            System.out.println(dev);
            dev.open(1,2,0);
   
            while(true != false) {
                dev.writeBulk( 0x03, led_on, 64, 3000, false);
                //Thread.sleep(10);
                dev.writeBulk( 0x03, read_button, 64, 3000, false);
                //Thread.sleep(1);
                try {
                    dev.readBulk( 0x83, incoming, 64, 10, false);
                    System.out.println("Incoming: "+incoming[1]);
                } catch (USBException exp) {
                        System.out.println(exp);
                }
                Thread.sleep(100);
                
            }*/
    }
    
}