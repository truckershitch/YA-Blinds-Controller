## YA-Blinds-Controller

This is another way to automate window blinds with an ESP8266 microcontroller.  I have been using this code for over a year and it is fairly mature.

I have three single windows on the rear of my house and they catch the evening sun.  I got sick of getting up to close them when I wanted to watch television.  I saw this project on the web:

https://blog.christophermullins.com/2020/02/16/automating-blinds-with-a-retrofitted-external-motor/

I liked it because I am not good with drywall repair.  Also, the walls are covered with a textured wallpaper that was painted, and I have no idea how I could patch it if things went south or I had to remove it for some reason.

At the time I did not own a 3d printer so I had the parts sourced.  It was probably the most expensive part of the project, and I ended up with adapters that did not fit my blind.  A few months later I got a printer and made my own adapter.  It took a while but it was my first design and I am damn proud of it.  It involved octagon geometry / math and let me just say it has been a while since I did that.

Currently, the code uses Micropython 1.16.  There should not be significant new features and it should run on previous versions as well.

"Heartbeat" information is sent to a configured MQTT server and can be read by Home Assistant.  Some example automations are included here in `scripts_playroom_blinds.yaml`.

There is some provision in here for error handling.  If you download the `error.log` file, you should get a decent error message if one occurs.  MQTT and basic network errors are handled by waiting 60 seconds and then rebooting, until a maximum count is reached, and then the code gives up.  At that point WebREPL may still work and it can be restarted, or simply power cycling the device may fix the issue.  Hopefully.

There are some files/folders here for micropy-cli, namely:
* `.micropy/`
* `.pylintrc`
* `dev-requirements.txt`
* `micropy.json`
* `pymakr.conf`
* `requirements.txt`

I used micropy-cli to help with the development in Visual Studio Code.  You don't need these unless you want to take a look.

https://github.com/BradenM/micropy-cli

Fill out `wifi_cred.py` and `mqtt_cred.py` and name the files as such based on each .sample file.

YMMV.<br>(Your milage may vary.  Don't those abbreviations make you angry?)

### Hardware

* ESP8266 Uno R3 Hybrid Board
* CNC Shield v3
* (3) A4988 Stepper Motor Controllers
* (3) 28BYJ-48 Stepper Motors
* Project Case
  * I got these: https://www.amazon.com/gp/product/B083PSP3WW/ and they are solid.  I had another project in the garage so it worked out.  At the time, I did not own a 3D printer or I would have designed my own case.
* Long-ish length of Ethernet cable.  I would suggest solid core, not stranded, unless you have it already or you like to suffer.
* A crimper for JST connectors or Dupont connectors really helps here

### Assembly

Chistopher takes care of most of that on his page.  The CNC Shield really helps here.  You can do it the hard way but I don't really see the point.

I cut one 10K resistor as the Esp8266 Uno R3 board is a 3.3V board.  I left one lead connected and put a tiny piece of heat shrink on the bare end in case I wanted to reconnect it (although 10K resistors are pretty darn cheap, so I'm not sure why I bothered).  The details as to why are in the link below.

https://onstep.groups.io/g/main/wiki/19670

### Helpful YouTube Videos

* https://www.youtube.com/watch?v=AVlee67TQxs -- Set output current limit for A4988 Stepper Motor Driver
* https://www.youtube.com/watch?v=kCDGEezyzfw -- CNC Shield Setup and testing
* https://www.youtube.com/watch?v=TMK_fLgpESQ -- More CNC Shield Setup
* The CNC Shield v3 is highly documented.  You can learn all you need to learn by doing some reading.

<b>Good luck!</b>