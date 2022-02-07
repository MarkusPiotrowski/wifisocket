# DOCUMENTATION

## Constants and Global Default Variables
### Constants
#### En- and Decryption
PASSKEY = b'0123456789abcdef'  
INITIALIZATION_VECTOR = PASSKEY

#### Device Codes
SWS_A1 = 'C1 11 71 50'  
DIS_120 = 'C2 11 92 DD'  
U_DEVICE = 'CA A1 88 98'  # Unknown device

#### Commands
CMD_INIT = '01 40 \{mac} '  
CMD_HEADER = '00 \{packet} \{device} '  
CMD_SEARCH = '23 \{mac} 02 02'  
CMD_SWITCH = '01 \{switch} 04 04 04 04'  
CMD_GET_STATE = '02 00 00 00 00 04 04 04 04'  
CMD_TIMER_QUERY = '04 00 00 06 06 06 06 06 06'  
CMD_SET_TIMER = '03 00 \{timer} \{repeat} \{hour} \{minute} \{switch} 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F'   
CMD_DELETE_TIMER = '05 00 \{timer:02x} 06 06 06 06 06 06'  
CMD_SWITCH_SLAVE = '08 \{slave} \{switch} 04 04 04 04'  
CMD_AM_QUERY = '0A 08 08 08 08 08 08 08 08'  
CMD_SET_AM = '09 \{active} \{from_:08x} \{to_:08x} 1E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E'  
CMD_DELETE_AM = '09 00 00 00 00 00 00 00 00 00 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E'  
CMD_HEARTBEAT = '61 55 93 26 54 04 04 04 04'  
CMD_VERSION = '62 08 08 08 08 08 08 08 08'  

### Default Variables
device = SWS_A1  
packet = 'FF FF'  
udp_port = 8530  
timeout = 2  
repeat = 3  
my_ip = socket.gethostname()  

## User Functions

***
### **find_sockets(*mac='FF FF FF FF FF FF', ip='255.255.255.255'*)**
*Broadcast status query and collect MAC and IP data of all sockets.*

Using this function with standard arguments (`find_sockets()`) will return a list of all available/connected sockets. You can search for a certain socket either by giving its MAC or IP address.
Note that the MAC address is a fixed number of a device, while the IP depends on the network to which the socket is connected and may also change dynamically over time.
The return value is a list of named tuples `[(Socket(mac=..., ip=...)', ...]` or just a named tuple if the socket was defined by it's MAC or IP address.
***

### **switch(*socket_, on_off*)**
*Switch the socket on or off.*

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **on_off**: `'on'` or `'off'` to switch on or off.
***

### **switch_state(*socket_*)**
*Return the switch state of a socket (`'on'` or `'off'`)*
- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
***
 
### **switch_slave(*socket_, slave, on_off*)**
*Switch the slave socket on or off.*  
To switch the radio-controlled 433 Mhz slave sockets (e.g., ALDI Easy Home kit)
 >EXPERIMENTAL! I haven't tested this.

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **slave**: 3-byte long hex, like '78fb12'. Like a MAC address, this is a specific number of the radio slave sockets.
- **on_off**: `'on'` or `'off'` to switch on or off.
***

### **timer_query(*socket_, which='all', delta_time=None*)**
*Return the timer data for a given socket.*  

Each socket has 10 timer slots (no. 1-10) and one countdown slot.

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **which**: Allows to select which timers are reported. Options:  
`'all'`: all timers (**default**)  
`1`-`10` or `'Countdown'`: the respective timer  
`'set'`: all programmed timers (if active or not)  
`'active'`: only the active timers  
`'free'`: non-programmed timer slots, will only return a list of the free timer numbers.
- **delta_time**: Difference between the socket's time and the local time.  
The modul assumes that the sockets are internally running UCT (GMT) time. The default setting corrects between your local time and UCT. If this is not correct, you can apply a different time difference (in seconds).

The function either returns a named tuple (`Timer`) (if the `which` argument is set to one timer) or a list of named tuples:

- **number**: The number of the timer. Ten timer slots are available (`1`-`10`). Another timer slot (no. 11) is the countdown timer and referred to as `'Countdown'`.
- **active**: `True` or `False` when the timer is programmed (active or not) and `None` if the timer slot is empty.
- **repeat**: A binary representation for daily repeat cycles, where each digit stands for a day in the week, starting at Monday. E.g.,  
`'1111100'`: repeat from Monday to Friday  
`'1111111'`: repeat every day  
`'0000000'`: never repeat, just switch today
- **time**: When to switch, in 24-hour format (*hh:mm*).  
Note: This modul assumes that the sockest are using UCT internally and corrects this to local time. If this is not correct, use the 'delta_time' argument (see above).
- **switch**: What to do. Switch `'on'` or `'off'`.
***

### **set_timer(*socket_, timer, active, repeat, time_, switch, delta_time=None*)**
*Program a timer (or countdown) of a socket.*

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **timer**: Each socket has 10 timer slots (`1`-`10`) and one countdown slot (`11` or `'Countdown'`).
- **active**: A timer can be programmed but does not need to be active. `True`  or `False`.
- **repeat**: A binary representation for daily repeat cycles, where each digit stands for a day in the week, starting at Monday. E.g.,  
`'1111100'`: repeat from Monday to Friday  
`'1111111'`: repeat every day  
`'0000000'`: never repeat, just switch today
- **time_**: Time in **hh:mm** format, e.g., `'13:25'`.
- **switch**: `'on'` or `'off'`
-delta_time**:Difference between the socket's time and the local time.  
The modul assumes that the sockets are internally running UCT (GMT) time. The default setting corrects between your local time and UCT. If this is not correct, you can apply a different time difference (in seconds).
***
   
### **set_countdown(*socket_, time_, switch, delta_time=None*)**
*Call set_timer with countdown-specific defaults.*  

Helper function for easy setting of the countdown timer.

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **time_**: Countdown time in **hh:mm** format, e.g., `'01:30'`.
- **switch**:`'on'` or `'off'`
- **delta_time**: Difference between the socket's time and the local time.  
The modul assumes that the sockets are internally running UCT (GMT) time. The default setting corrects between your local time and UCT. If this is not correct, you can apply a different time difference (in seconds).
***

### **activate_timer(*socket_, timer, activate=True*)**
*Activate or deactivate an existing timer.*  

Helper function to activate or deactivate an already programmed timer.

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **timer**: The number of the programmed timer (`1`-`10`).
- **activate**: `activate=True` (**default**) will activate the timer, `activate=False` will deactivate it. Deactivating a timer does not delete it, its settings will be kept.
***

### **delete_timer(*socket_, timer*)**
*Delete the given timer of the given socket.*

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **timer**: The number of the programmed timer (`1`-`10` or `'Countdown'`).
***

### **absence_mode_query(*socket_*)**
*Return the absence mode (antithief mode) data.*

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
***

### **set_absence_mode(*socket_, active, from_, to_*)**
*Set absence (antithief) mode.*

In absence (or antithief) mode the socket switches on and off every 30 minutes.

- **socket_**:A tuple of (MAC address, IP address) of the Wi-Fi socket.
- **active**: `True` or `False` to activate absence mode. Actually, this parameter doesn't make too much sense, because the whole command must be send anyway. (Couldn't just send 'activate'...).
- **from_**: Start of absence mode in **dd.mm.yyyy hh:mm** format, e.g., `'20.01.2023 22:00'`.
- **to_**:Like `from_`.
***


### **delete_absence_mode(*socket_*)**
*Delete absence mode.*

- **socket_**: A tuple of (MAC address, IP address) of the Wi-Fi socket.
***

### **heartbeat(*socket_*)**
*Ask for heartbeat response of socket. Return `True` when alive.*

- **socket_** A tuple of (MAC address, IP address) of the Wi-Fi socket.
***

### **send_password(*password, time_=30*)**
*Send the Wi-Fi password to a listening socket.*

Press the on/off button of the socket for 5 seconds until the LED starts flashing red quickly. Then use this command.

- **password**: The password of the wireless network.
- **time_**: Duration (in seconds) how long the process should proceed. Default: 30 sec.
***
    
## Helper Functions
Please consider them 'PRIVAT'.

***
### **assemble_command(*mac, command*)**
*Assemble a valid command from different parts and return it.*
***

### **encrypt(*command*)**
*Encrypt the command with AES/CBC.*
***

### **decrypt(*message*)**
*Decrypt message with AES/CBS.*
***

### **create_socket(*my_ip=my_ip, broadcast=False*)**
*Create an internet socket for UDP communication to (real) sockets.*

- **broadcast**: Set to `True` if the socket is for broadcasting UDP to all listening devices. If broadcast is `True`, the IP address is automatically set to `'255.255.255.255'`. Default: `False`.
***

### **send(*ip, command, broadcast=False*)**
*Send a command to a socket, receive and return the answer.*

- **ip**: The IP address of the device, given as dot-separated string.  
Note that the IP address of a socket may change (when dynamically assigned). Use `find_sockets(mac)` to get the IP address of a certain device.
- **command**: A command string in hex format (space-separated or not).
- **broadcast**: Send to all devices in the local wireless network. Default is `False` which means that commands are usually send to a given device, defined by its IP.
*** 

### **send_and_forget(*ip, command, broadcast=False*)**
*Just send a command to a socket once, do nothing else.*
***
