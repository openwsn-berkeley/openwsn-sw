package com.mehtank.flygina;

import java.io.IOException;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.KeyEvent;
import android.widget.CompoundButton;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;
import android.widget.CompoundButton.OnCheckedChangeListener;
import android.graphics.PorterDuff;

public class Flygina extends Activity {
	static final int heliPort = 2192;
	static final int ledsPort = 2193;
	
    TextView tv;
    ToggleButton leds[] = new ToggleButton[4];
    MoteAddress moteaddr;
    FrameLayout top;

    Controls controls;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        Mote.setPrefs(getPreferences(Context.MODE_PRIVATE));
        
        top = (FrameLayout) findViewById(R.id.top);
        tv = (TextView) findViewById(R.id.value);
        leds[0] = (ToggleButton) findViewById(R.id.led0);
        leds[1] = (ToggleButton) findViewById(R.id.led1);
        leds[2] = (ToggleButton) findViewById(R.id.led2);
        leds[3] = (ToggleButton) findViewById(R.id.led3);
        moteaddr = new MoteAddress(this);
        
        controls = new Controls(this);
        
        OnCheckedChangeListener ledListener = new OnCheckedChangeListener() {
			@Override
			public void onCheckedChanged(CompoundButton buttonView,	boolean isChecked) {
				sendLEDs();
			}
        };
        
        leds[0].setOnCheckedChangeListener(ledListener);
        leds[0].getBackground().setColorFilter(0xFFFFcccc, PorterDuff.Mode.MULTIPLY);
        leds[1].setOnCheckedChangeListener(ledListener);
        leds[1].getBackground().setColorFilter(0xFF88FFcc, PorterDuff.Mode.MULTIPLY);
        leds[2].setOnCheckedChangeListener(ledListener);
        leds[2].getBackground().setColorFilter(0xFFccccFF, PorterDuff.Mode.MULTIPLY);
        leds[3].setOnCheckedChangeListener(ledListener);
        leds[3].getBackground().setColorFilter(0xFFFFcccc, PorterDuff.Mode.MULTIPLY);
    }

    void sendLEDs() {
    	byte b[] = new byte[1];
    	for (int i = 0; i < leds.length; i++)
    		if (leds[i].isChecked()) b[0] += (1 << i);
    	
    	try {
			Mote.sendPacket(b, ledsPort);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
    
	void control(int t, float p, int m1, int m2)	{
		byte b[] = new byte[4];
		
		b[0] = (byte) (m1 >> 8);
		b[1] = (byte) (m1 & 0xff);
		b[2] = (byte) (m2 >> 8);
		b[3] = (byte) (m2 & 0xff);

		String str = "";
		// str += "Seekbar says: " + t + " throttle\n";
		// str += "Pitch is " + p + ".\n\n";
		str += "Motor 1 is " + m1 + ", \n";
		str += "Motor 2 is " + m2 + ". \n\n";
		// str += "[" + b[0] + ", " + b[1] + ", " + b[2] + ", " + b[3] + "]\n\n\n\n";
		
		tv.setText(str);
		
		try {
			if ((m1 == 0) && (m2 == 0))
				Mote.sendPacket(b, heliPort, true);
			else
				Mote.sendPacket(b, heliPort);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	long lastBackClick = 0;
	@Override
	public boolean onKeyDown(int keyCode, KeyEvent event) {
	    if (keyCode == KeyEvent.KEYCODE_BACK) {
	    	long now = System.currentTimeMillis();
	    	if (now - lastBackClick < 3000) // 3 seconds
	    		onDestroy();
	    	else {
	    		lastBackClick = now;
        		Toast.makeText(this, "Click again to quit.", Toast.LENGTH_SHORT).show();
	    	}
	        return true;
	    }
	    return super.onKeyDown(keyCode, event);
	}

	@Override
	public void onDestroy() {
		try {
			Mote.sendPacket(new byte[] {0, 0, 0, 0}, heliPort, true);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		Mote.disconnect();
		controls.destroy();
		super.onDestroy();
		System.exit(0);
	}
}