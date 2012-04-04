import ch.ntb.usb.*;

public class test_java {
    
    
    
        public static void main(String[] args) throws Exception{
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
                
            }
        }
    
}