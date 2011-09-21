package com.mehtank.flygina;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.widget.SeekBar;
import android.widget.SeekBar.OnSeekBarChangeListener;

public class Controls implements OnSeekBarChangeListener, SensorEventListener {
    SensorManager sensorManager;
    Sensor sensor;
    SeekBar seek;
    
    Flygina top;
    
    float azimuth = 0;
    float pitch = 0;
    float roll = 0;
    int throttle = 0;
    
    int motor1 = 0, motor2 = 0;
    final static int MOTORMIN = 0;
    final static int MOTORMAX = 100;
    
    public Controls(Flygina top) {
    	this.top = top;
    	
        sensorManager = (SensorManager)top.getSystemService(Context.SENSOR_SERVICE);
        sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ORIENTATION);
        sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL);

        seek = (SeekBar) top.findViewById(R.id.seek);
        seek.setProgress(0);
        seek.setOnSeekBarChangeListener(this);
    }
    
    void destroy() {
		sensorManager.unregisterListener(this);
    }

    private int threshold(int m) {
    	if (m < MOTORMIN) 
    		return MOTORMIN;
    	if (m > MOTORMAX) 
    		return MOTORMAX;
    	return m;
    }
    private void update() {
		int t = throttle;
		if (t < 0) t = 0;
		
		float p = pitch / 200;
		int m1 = (int) (t * (1 + p));
		int m2 = (int) (t * (1 - p));
		
		m1 = threshold(m1);
		m2 = threshold(m2);
		
		if ((m1 == motor1) && (m2 == motor2))
			return;
		
		motor1 = m1;
		motor2 = m2;
		top.control(t, p, m1, m2);
    }
    
	@Override
	public void onSensorChanged(SensorEvent event) {
		azimuth=event.values[0];
		pitch=event.values[1];
		roll=event.values[2];
		update();
	}

	@Override
	public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
		throttle = seekBar.getProgress();
		update();
	}

	@Override
	public void onAccuracyChanged(Sensor arg0, int arg1) {}
	@Override
	public void onStartTrackingTouch(SeekBar seekBar) {}
	@Override
	public void onStopTrackingTouch(SeekBar seekBar) {
		seekBar.setProgress(0);
	}
}
