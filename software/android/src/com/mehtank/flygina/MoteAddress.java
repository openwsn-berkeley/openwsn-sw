package com.mehtank.flygina;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.text.InputFilter;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Toast;

public class MoteAddress {
	static final int ROWMAX = 2;
	static final int COLMAX = 4;
	
	EditText addrText[][] = new EditText[ROWMAX][COLMAX];
	Activity top;
	SharedPreferences prefs;
	
	static final String[][] DEFAULT_ADDR = 
			{{"2001", "470", "846d", "1"}, 
			 {"1415", "9209", "022b", "1"}};
	
	public MoteAddress(Activity top) {
		this.top = top;

		prefs = top.getPreferences(Context.MODE_PRIVATE);

		LinearLayout addrBytes = (LinearLayout) top.findViewById(R.id.addrbytes);

		LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(100, LinearLayout.LayoutParams.WRAP_CONTENT);
		for (int row = 0; row < ROWMAX; row++) {
			LinearLayout ll = new LinearLayout(top);
			ll.setOrientation(LinearLayout.HORIZONTAL);
			for (int col = 0; col < COLMAX; col++) {
				EditText a = new EditText(top);
				a.setText(prefs.getString("addrStr"+row+col, DEFAULT_ADDR[row][col] ));
				a.setSingleLine();
				a.setFilters(new InputFilter[] {new InputFilter.LengthFilter(4)});
				a.setWidth(100);
				a.setLayoutParams(lp);
				ll.addView(a);
				addrText[row][col] = a;
			}
			addrBytes.addView(ll);
		}
		
		Button button = (Button) top.findViewById(R.id.addrbutton);
		button.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				saveAddress();
				InetAddress moteAddr;
				byte[] b = getAddrBytes();
				try {
					moteAddr = InetAddress.getByAddress(b);
					// displayConn("Pinging " + moteAddr.toString());
					displayConn(moteAddr.isReachable(1000));
				} catch (UnknownHostException e1) {
					displayConn("Unknown Host Exception!");
					e1.printStackTrace();
				} catch (IOException e) {
					displayConn("IO Exception!");
					e.printStackTrace();
				}
			}
		});
	}
	
	private void displayConn(boolean b) {
		if (b)
			displayConn("Mote responds to ping!");
		else
			displayConn("No response from mote.");
	}
	private void displayConn(String s) {
		Toast.makeText(top, s, Toast.LENGTH_SHORT).show();
	}
	
	private byte[] getAddrBytes() {
		byte[] b = new byte[16];
		String[][] addr = new String[ROWMAX][COLMAX];

		for (int row = 0; row < ROWMAX; row++) 
			for (int col = 0; col < COLMAX; col++) 
				addr[row][col] = addrText[row][col].getText().toString();
		b = Mote.getAddressBytes(addr, DEFAULT_ADDR);

		return b;
	}

	public void saveAddress() {
		byte[] b = getAddrBytes();

		SharedPreferences.Editor edit = prefs.edit();
		for (int row = 0; row < ROWMAX; row++) 
			for (int col = 0; col < COLMAX; col++) 
				edit.putString("addrStr"+row+col, addrText[row][col].getText().toString());
		for (int i = 0; i < 16; i++) 
			edit.putInt("addr" + i, b[i]);
		edit.commit();
	}
	
}
