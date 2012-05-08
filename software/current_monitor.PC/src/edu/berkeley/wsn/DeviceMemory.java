package edu.berkeley.wsn;

import javax.naming.BinaryRefAddr;
import javax.swing.JFileChooser;
import javax.swing.filechooser.FileFilter;

import java.io.*;
import java.util.Vector;

public class DeviceMemory {
	public static JFileChooser chooser = new JFileChooser();
	static {
		chooser.setFileFilter(new FileFilter() {
			public String getDescription() {
				return "Current Monitor configurations (.cm)";
			}
			public boolean accept(File f) {
				return f.getPath().endsWith(".cm");
			}
		});
	}
	
	public static void loadFromFile() {
		if ( chooser.showOpenDialog(null) == chooser.APPROVE_OPTION ) {
			File f = chooser.getSelectedFile();
			try {
				loadFromStream(new FileInputStream(f));
			} catch (FileNotFoundException exp){
				CurrentMonitor.msg("Error: "+exp);
			}
		}
	}
	
	public static void saveToFile(){
		if ( chooser.showSaveDialog(null) == chooser.APPROVE_OPTION ) {
			File f = chooser.getSelectedFile();
			try {
				saveToStream(new FileOutputStream(f));
			} catch (FileNotFoundException exp){
				CurrentMonitor.msg("Error: "+exp);
			}
		}		
		
	}
	
	public static void loadFromDevice() {
		if ( CurrentMonitor.dev == null ) {
			CurrentMonitor.me.connectToDevice();
		}
		// read from start of flash
		byte[] data;
		data = CurrentMonitor.commands.sendRcv(DeviceCommands.CmdDefs.FLASH_START_READ,(byte)0,(byte)0,(byte)0,(byte)0);
		int length = (0xFF & data[0]) | (0xFF00 & (data[1]<<8)) | (0xFF0000 & (data[2]<<16)) | (0xFF000000 & (data[3]<<24));
		System.out.println("Length of Config memory:"+length);
		byte[] d2 = new byte[length];
		System.arraycopy(data, 4, d2, 0, (data.length - 4 < length)?data.length-4:length);
		int pos = data.length-4;
		int amt = 0;
		while (pos < length) {
			data = CurrentMonitor.commands.sendRcv(DeviceCommands.CmdDefs.FLASH_CONTINUE_READ);
			System.arraycopy(data, 0, d2, pos,amt = ((data.length+pos<length)?data.length:length-pos));
			pos += amt;
		}
		CurrentMonitor.commands.sendRcv(DeviceCommands.CmdDefs.FLASH_STOP_READ);
		
		ByteArrayInputStream stream = new ByteArrayInputStream(d2);
		loadFromStream(stream);
	}
	
	public static void saveToDevice() {
		if ( CurrentMonitor.dev == null ) {
			CurrentMonitor.me.connectToDevice();
		}
		
		ByteArrayOutputStream stream = new ByteArrayOutputStream();
		saveToStream(stream);
		byte[] data = stream.toByteArray();
		byte[] cmd = new byte[50];
		cmd[0] = DeviceCommands.CmdDefs.FLASH_START_WRITE;
		cmd[1] = cmd[2] = cmd[3] = cmd[4] = 0;
		cmd[8] = (byte)((data.length>>24)&0xFF);
		cmd[7] = (byte)((data.length>>16)&0xFF);
		cmd[6] = (byte)((data.length>>8)&0xFF);
		cmd[5] = (byte)((data.length)&0xFF);
		
		int pos, len;
		System.arraycopy(data, 0, cmd, 9, len = pos = ((data.length < cmd.length - 9)?data.length:cmd.length-9));
		CurrentMonitor.commands.sendRcv(cmd);
		cmd[0] = DeviceCommands.CmdDefs.FLASH_CONTINUE_WRITE;
		while ( pos < data.length ) {
			System.arraycopy(data, pos, cmd, 1, len = ((data.length - pos < cmd.length - 1)?data.length - pos:cmd.length - 1));
			CurrentMonitor.commands.sendRcv(cmd);
			pos += len;
		}
		
		CurrentMonitor.commands.sendRcv(DeviceCommands.CmdDefs.FLASH_STOP_WRITE);
	}
	
	private static void loadFromStream(InputStream in) {
		Vector<Runnable> update_tasks = new Vector<Runnable>();
		try {
			int cbuf;
			while((cbuf = in.read()) != -1) {
				switch (cbuf) {
				case 0x20: // XBee configuration
					System.out.println("Found XBee configurations");
					update_tasks.add(loadXbeeFromStream(in));
					break;				
				}
			}
			
			for (Runnable task : update_tasks) {
				task.run();
			}
		} catch (IOException exp) {
			CurrentMonitor.msg("Error loading:"+exp);
		}		
	}
	

	
	
	private static void saveToStream(OutputStream out) {
		try {
			saveXbeeToStream(out);
		} catch (IOException exp) {
			CurrentMonitor.msg("Error saving:"+exp);
		}			
	}
	
	private static Runnable loadXbeeFromStream(InputStream in) throws IOException {
		int num_configs = read8(in);
		int cur_config = 0;
		final Vector<XBeeConfiguration> temp_configs = new Vector<XBeeConfiguration>();
		while ( cur_config < num_configs ) {
			XBeeConfiguration conf = new XBeeConfiguration();
			
			int config_name_len = read8(in);
			byte[] name_bytes = new byte[config_name_len];
			in.read(name_bytes);
			conf.name = new String(name_bytes);
			System.out.println("Found configuration "+conf.name);
			int num_at_commands = read16(in);
			for ( int cur_at_command = 0; cur_at_command < num_at_commands; cur_at_command++) {
				XBeeConfiguration.ATSetting at = conf.new ATSetting();
				at.name = "" + (char)(in.read()) + (char)(in.read());
				int settingb = read8(in);
				byte[] inb = new byte[settingb];
				in.read(inb);
				at.setting = inb;
				conf.at_settings.add(at);
			}
			cur_config++;
			temp_configs.add(conf);
		}
		return new Runnable() {
			public void run() {
				CurrentMonitor.xbee_tab.configs.clear();
				CurrentMonitor.xbee_tab.config_list_model.setRowCount(0);
				for (XBeeConfiguration cfg : temp_configs) {
					CurrentMonitor.xbee_tab.configs.add(cfg);
					CurrentMonitor.xbee_tab.config_list_model.addRow(new Object[] {cfg.toString()});
				}
			}
		};
	}
	
	private static void saveXbeeToStream(OutputStream out) throws IOException {
		out.write(0x20);
		write8(out, CurrentMonitor.xbee_tab.configs.size());
		for ( XBeeConfiguration conf : CurrentMonitor.xbee_tab.configs ) {
			write8(out, conf.name.length());
			out.write(conf.name.getBytes());
			write16(out,conf.at_settings.size());
			for ( XBeeConfiguration.ATSetting at : conf.at_settings ) {
				out.write(at.name.charAt(0));
				out.write(at.name.charAt(1));
				write8(out,at.setting.length);
				out.write(at.setting);
			}
		}
	}
	
	private static int read32(InputStream in) throws IOException {
		return (0xFF & in.read()) |
				((0xFF & in.read())<<8) |
				((0xFF & in.read())<<16) |
				((0xFF & in.read())<<24);
	}
	
	private static void write32(OutputStream out, int u32) throws IOException {
		out.write(u32&0xFF);
		out.write((u32>>8)&0xFF);
		out.write((u32>>16)&0xFF);
		out.write((u32>>24)&0xFF);
	}
	
	private static int read16(InputStream in) throws IOException {
		return (0xFF & in.read()) |
				((0xFF & in.read())<<8);
	}
	
	private static void write16(OutputStream out, int u16) throws IOException {
		out.write(u16&0xFF);
		out.write((u16>>8)&0xFF);
	}
	
	private static int read8(InputStream in) throws IOException {
		return (0xFF & in.read());
	}
	
	private static void write8(OutputStream out, int u8) throws IOException {
		out.write(u8&0xFF);
	}
}
