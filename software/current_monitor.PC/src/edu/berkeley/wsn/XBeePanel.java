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


public class XBeePanel extends JPanel {
	CurrentMonitor parent;
	
	Vector<XBeeConfiguration> configs = new Vector<XBeeConfiguration>();

	JButton read_info_button = new JButton("Read Information");
	{
		read_info_button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent arg0) {
				readInformation();
			}
		});
	}
	JButton add_configuration_button = new JButton("Add Configuration");
	{
		add_configuration_button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent arg0) {
				addConfiguration();
			}
		});
	}
	JButton delete_configuration_button = new JButton("Delete Configuration");
	{
		delete_configuration_button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent arg0) {
				deleteConfiguration();
			}
		});
	}
	JButton start_recording_button = new JButton("Spy XB configuration");
	{
		start_recording_button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent arg0) {
				startRecording();
			}
		});
	}
	JButton add_AT_button = new JButton("Add AT setting");
	{
		add_AT_button.setEnabled(false);
		add_AT_button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent arg0) {
				addAT();
			}
		});
	}
	JButton delete_AT_button = new JButton("Delete AT setting");
	{
		delete_AT_button.setEnabled(false);
		delete_configuration_button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent arg0) {
				deleteAT();
			}
		});
	}
	{		
		Box h1 = Box.createHorizontalBox();
		Box v1 = Box.createVerticalBox();
		Box v2 = Box.createVerticalBox();
		h1.setBorder(new TitledBorder("Operations"));
		h1.add(read_info_button);
		v2.add(add_configuration_button); v2.add(delete_configuration_button);
		h1.add(v2);
		v1.add(start_recording_button);
		h1.add(v1);
		Box v3 = Box.createVerticalBox();
		v3.add(add_AT_button); v3.add(delete_AT_button);
		h1.add(v3);
		add(h1, BorderLayout.NORTH);
	}
	
	DefaultTableModel config_list_model = new DefaultTableModel(0,1);
	JTable configuration_list = new JTable(config_list_model);
	
	JScrollPane config_list_scroller = new JScrollPane(configuration_list);
	{
		configuration_list.setTableHeader(null);
		configuration_list.putClientProperty("JTable.autoStartsEdit", Boolean.FALSE);
		config_list_scroller.setBorder(new TitledBorder("Configurations (F2 to rename)"));
		configuration_list.getSelectionModel().addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent e) {
				viewConfiguration(configuration_list.getSelectedRow());
			}
		});
		configuration_list.setColumnSelectionAllowed(false);
		configuration_list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		config_list_model.addTableModelListener(new TableModelListener() {
			public void tableChanged(TableModelEvent arg0) {
				if ( arg0.getType() == arg0.UPDATE )
					configs.get(arg0.getFirstRow()).name = (String) config_list_model.getValueAt(arg0.getFirstRow(), arg0.getColumn());
			}
		});
	}
	
	DefaultTableModel register_list_model = new DefaultTableModel(0,2);
	JTable register_list = new JTable(register_list_model);
	JScrollPane register_list_scroller = new JScrollPane(register_list);
	{
		register_list_model.setDataVector(new Object[][] {}, new Object[] {"AT Command","Value"});
		register_list.putClientProperty("JTable.autoStartsEdit", Boolean.TRUE);
		register_list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		register_list_scroller.setBorder(new TitledBorder("AT settings"));
		register_list_model.addTableModelListener(new TableModelListener() {
			public void tableChanged(TableModelEvent arg0) {
				if ( arg0.getType() == arg0.UPDATE && configuration_list.getSelectedRow() >= 0 && configuration_list.getSelectedRow() < configs.size() && arg0.getFirstRow() >= 0) {
					XBeeConfiguration xb = configs.get(configuration_list.getSelectedRow());
					ATSetting at = xb.at_settings.get(arg0.getFirstRow());
					if ( at.update(register_list_model.getValueAt(arg0.getFirstRow(), 0).toString(), register_list_model.getValueAt(arg0.getFirstRow(), 1).toString()) ) {
					} else {
						if ( arg0.getColumn() == 0 )
							register_list_model.setValueAt(at.name, arg0.getFirstRow(), 0);
						else
							register_list_model.setValueAt(at.settingToString(), arg0.getFirstRow(), 1);
						parent.error("Invalid AT register or setting");
					}
				}
			}
		});
	}
	
	{
		JSplitPane splitter = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
		splitter.add(config_list_scroller);
		splitter.add(register_list_scroller);
		splitter.setDividerLocation(400);
		add(splitter, BorderLayout.CENTER);
	}
	
	
	public XBeePanel(CurrentMonitor p) {
		super(new BorderLayout());
		parent = p;
		
		
	}
	
	void readInformation() {
		parent.msg("Reading XB information from monitor");
		
	}
	
	void startRecording() {
		parent.msg("Starting to record XB transactions");
		
	}
	void addConfiguration() {
		XBeeConfiguration cfg = new XBeeConfiguration();
		configs.add(cfg);
		config_list_model.addRow(new Object[] {cfg.toString()});
		configuration_list.editCellAt(config_list_model.getRowCount()-1, 0);
		configuration_list.changeSelection(config_list_model.getRowCount()-1, 0, false, false);
	}
	
	void deleteConfiguration() {
		int idx = configuration_list.getSelectedRow();
		if ( idx >= 0 && idx < config_list_model.getRowCount() ) {
			XBeeConfiguration xb = configs.get(idx);
			if ( JOptionPane.OK_OPTION == JOptionPane.showConfirmDialog(null, "Delete configuration "+xb.name+" ?","XBee Configuration Delete",JOptionPane.OK_CANCEL_OPTION) ) {
				config_list_model.removeRow(idx);
				configs.remove(idx);
				viewConfiguration(-1);
			}
		}
	}
	
	void viewConfiguration(int config_no) {
		System.out.println("View "+config_no);
		if ( config_no >= 0 && config_no < config_list_model.getRowCount()) {
			XBeeConfiguration xb = configs.get(config_no);		
			Object[][] new_model = new Object[xb.at_settings.size()][2];
			for ( int c = 0; c<new_model.length; c++ ) {
				new_model[c][0] = xb.at_settings.get(c).name;
				new_model[c][1] = xb.at_settings.get(c).settingToString();
			}
			register_list_model.setDataVector(new_model, new Object[]{"AT Command","Value"});
			
			add_AT_button.setEnabled(true);
			delete_AT_button.setEnabled(true);
		} else {
			register_list_model.setRowCount(0);
			
			add_AT_button.setEnabled(false);
			delete_AT_button.setEnabled(false);
		}
	}
	
	void addAT() {
		int config_no = configuration_list.getSelectedRow();
		if ( config_no >= 0 && config_no < config_list_model.getRowCount()) {
			XBeeConfiguration xb = configs.get(config_no);
			xb.at_settings.add(xb.new ATSetting());
			register_list_model.addRow(new Object[] {"XX","00"});
			register_list.editCellAt(register_list_model.getRowCount()-1, 0);
			register_list.changeSelection(register_list_model.getRowCount()-1, 0, false, false);
		}
		
	}
	
	void deleteAT() {
		int idx = register_list.getSelectedRow();
		if ( idx >= 0 && idx < register_list_model.getRowCount() ) {
			register_list_model.removeRow(idx);
		}
	}
}


class XBeeConfiguration {
	String name = "New Configuration";
	
	Vector<ATSetting> at_settings = new Vector<ATSetting>();
	
	public class ATSetting {
		String name = "XX";
		byte[] setting = new byte[] {0x00};
		public String settingToString() {
			String ret = "";
			for (int c= 0; c < setting.length; c++ )
				ret += String.format("%02X", setting[c]);
			
			return ret;
		}
		
		public boolean setSetting(String str) {
			if ( str.length() % 2 != 0 ) return false;
			byte[] temp = new byte[str.length()/2];
			for (int i = 0; i < str.length(); i += 2) {
				try {
					temp[i/2] = (byte)(0xFF & Short.parseShort(str.substring(i,i+2),16));
				}catch(Exception e) {
					return false;
				}
			}
			setting = temp;
			return true;
		}
		public boolean update(String at, String val) {
			System.out.println("Got called "+at+" "+val);
			if ( at.length() == 2 ) {
				if ( setSetting(val) ) {
					name = at;
					return true;
				} else return false;				
			}else return false;
		}
	}
	
	public String toString() {
		return name;
	}
	
}
