package edu.berkeley.wsn;


import javax.swing.JPanel;
import ch.ntb.usb.*;
import javax.swing.*;
import javax.swing.*;

import java.awt.*;
import java.awt.event.*;

import javax.swing.event.*;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellEditor;
import javax.swing.text.JTextComponent;
import javax.swing.border.*;

import edu.berkeley.wsn.XBeeConfiguration.ATSetting;

import java.util.*;



public class StatusPanel extends JPanel implements Runnable {
	
	JButton start_updates = new JButton("Update Status");
	{
		start_updates.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (stat_update_thread == null ) {
					stat_update_thread = new Thread(StatusPanel.this);
					stat_update_thread.setDaemon(true);
					stat_update_thread.start();
				}
			}
		});
	}
	
	JButton stop_updates = new JButton("Stop Updating");
	{
		stop_updates.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if (stat_update_thread != null ) {
					stat_update_thread = null;
				}
			}
		});
	}
	
	JTextField iLow_text = new JTextField();
	JTextField iLow_raw_text = new JTextField();
	JTextField iHigh_text = new JTextField();
	JTextField iHigh_raw_text = new JTextField();
	
	Thread stat_update_thread;
	
	public StatusPanel() {
		super(new BorderLayout());
		Box h1 = Box.createHorizontalBox();
		h1.add(start_updates);
		h1.add(stop_updates);
		add(h1,BorderLayout.NORTH);
		
		JPanel pan = new JPanel(new GridLayout(4, 2));
		pan.add(new JLabel("iLow:")); pan.add(iLow_text);
		pan.add(new JLabel("iLow_raw:")); pan.add(iLow_raw_text);
		pan.add(new JLabel("iHigh:")); pan.add(iHigh_text);
		pan.add(new JLabel("iHigh_raw:")); pan.add(iHigh_raw_text);
		
		Box v1 = Box.createVerticalBox();
		v1.add(pan);
		v1.add(Box.createVerticalGlue());
		add(v1,BorderLayout.CENTER);
	}
	
	public void run() {
		if (CurrentMonitor.dev == null) {
			CurrentMonitor.error("Not connected to device");
			return;
		}
		
		try {
			while(stat_update_thread != null) {
				if ( CurrentMonitor.me.tabber.getSelectedComponent() == this ) {
					byte[] dat = CurrentMonitor.commands.sendRcv(DeviceCommands.CmdDefs.ADC_READ_IMMEDIATE);
					int iLow_raw = (0xFF & dat[0]) | ((0xFF & dat[1])<<8);
					int iHigh_raw = (0xFF & dat[2]) | ((0xFF & dat[3])<<8);
					
					double iHigh = ((iHigh_raw - 1.0)*3.3/1024/10.34);
					double iLow = -0.000044361198738*iLow_raw + 0.008737874605678;
					iLow_text.setText((iLow*1e6)+"uA");
					iLow_raw_text.setText(iLow_raw+"");
					iHigh_text.setText((iHigh*1e3)+"mA");
					iHigh_raw_text.setText(iHigh_raw+"");
				}
				Thread.sleep(500);
			}
		}catch (Exception exp) {
			exp.printStackTrace();
			CurrentMonitor.error("An error occurred:"+exp+"\nStatus Panel will stop.");
		}
	}
}
