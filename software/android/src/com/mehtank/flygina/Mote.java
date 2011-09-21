package com.mehtank.flygina;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

import android.content.SharedPreferences;

public class Mote {
	static InetAddress addr;
	static DatagramSocket sock;
	static SharedPreferences prefs;
	
	public static void setPrefs(SharedPreferences prefs) {
		Mote.prefs = prefs;
	}
	
	static void connect(int port) throws SocketException, UnknownHostException {
		byte[] addrBytes = new byte[16];
		for (int i = 0; i < 16; i++) 
			addrBytes[i] = (byte) prefs.getInt("addr" + i, 0);

		sock = new DatagramSocket();
		addr = InetAddress.getByAddress(addrBytes);
        sock.connect(addr, port);
	} 
	
	static long lastSent = 0;
	static final long minTime = 100;
	
	static void sendPacket(byte[] b, int port, boolean force) throws SocketException, UnknownHostException, IOException {		
		long now = System.currentTimeMillis();
		if (force || ((now - lastSent) > minTime)) {
			try {
				connect(port);
				sock.send(new DatagramPacket(b, b.length, addr, port));
				disconnect();
				lastSent = now;
			} catch (NullPointerException e) {};
		}		
	}
	
	static void sendPacket(byte[] b, int port) throws SocketException, UnknownHostException, IOException {
		sendPacket(b, port, false);
	}
	
	static void disconnect() {
		if (sock != null) {
			sock.disconnect();
			sock.close();
			sock = null;
		}
	}

	private static byte[] toBytes(String num, String defaultNum) {
		int i = 0;
		try {
			i = Integer.parseInt(defaultNum, 16);
		} catch (NumberFormatException e) {}
		try {
			i = Integer.parseInt(num, 16);
		} catch (NumberFormatException e) {}
		
		return new byte[] {(byte) ((i & 0xff00) >> 8), (byte) (i & 0xff)};
	}
	public static byte[] getAddressBytes(String[][] addr, String[][] defaultAddr) {
		byte[] b = new byte[16];
		int curByte = 0;
		for (int row = 0; row < addr.length; row++) {
			for (int col = 0; col < addr[row].length; col++) {
				byte[] b1 = toBytes(addr[row][col], defaultAddr[row][col]);
				b[curByte++] = b1[0];
				b[curByte++] = b1[1];
			}
		}
		return b;
	}
}
