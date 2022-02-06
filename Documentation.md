# DOCUMENTATION

## Constants and Global Default Variables
### Constants
#### En- and Decryption
PASSKEY = b'0123456789abcdef'

INITIALIZATION_VECTOR = PASSKEY
#### Device Codes
SWS_A1 = 'C1 11 71 50'

DIS_120 = 'C2 11 92 DD'
#### Commands
CMD_INIT = '01 40 {mac} '

CMD_HEADER = '00 {packet} {device} '

CMD_SEARCH = '23 {mac} 02 02'

CMD_SWITCH = '01 {switch} 04 04 04 04'

CMD_GET_STATE = '02 00 00 00 00 04 04 04 04'

CMD_TIMER_QUERY = '04 00 00 06 06 06 06 06 06'

CMD_SET_TIMER = '03 00 {timer} {repeat} {hour} {minute} {switch} 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F'
				 
CMD_DELETE_TIMER = '05 00 {timer:02x} 06 06 06 06 06 06'

CMD_SWITCH_SLAVE = '08 {slave} {switch} 04 04 04 04'

CMD_AM_QUERY = '0A 08 08 08 08 08 08 08 08'

CMD_SET_AM = '09 {active} {from_:08x} {to_:08x} 1E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E'

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

##### **find_sockets(*mac='FF FF FF FF FF FF', ip='255.255.255.255'*)**
***
*Broadcast status query and collect MAC and IP data of all sockets.*

Using this function with standard arguments (`find_sockets()`) will return a list of all available/connected sockets. You can search for a certain socket either by giving its MAC or IP address.
Note that the MAC address is a fixed number of a device, while the IP depends on the network to which the socket is connected and may also change dynamically over time.
The return value is a list of named tuples `[(Socket(mac=..., ip=...)', ...]` or just a named tuple if the socket was defined by it's MAC or IP address.

##### **switch(*socket_, on_off*)**
***
*Switch the socket on or off.*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>on_off</dt>
<dd>`'on'` or `'off'` to switch on or off.</dd>
</dl>

 
##### **switch_state(*socket_*)**
***
*Return the swicht state of a socket (`'on'` or `'off'`)*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
</dl>

 
##### **switch_slave(*socket_, slave, on_off*)**
***
*Switch the slave socket on or off.*
To switch the radio-controlled 433 Mhz slave sockets (e.g., ALDI Easy Home kit)
 >EXPERIMENTAL! I haven't tested this.
 
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>slave</dt>
<dd>3-byte long hex, like '78fb12'. Like a MAC address, this is a specific number of the radio slave sockets.</dd>
<dt>on_off</dt>
<dd>`'on'` or `'off'` to switch on or off.</dd>
</dl>


##### **timer_query(*socket_, which='all', delta_time=None*)**
***
*Return the timer data for a given socket.*
Each socket has 10 timer slots (no. 1-10) and one countdown slot.
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>which</dt>
<dd>Allows to select which timers are reported. Options:
<ul>
<li>'all': all timers (default)</li>
<li>1-10 or 'Countdown': the respective timer</li>
<li>'set': all programmed timers (if active or not)</li>
<li>'active': only the active timers</li>
<li>'free': non-programmed timer slots, will only return a list of the free timer numbers.
</ul>
</dd>
<dt>delta_time<dt>
<dd>Difference between the socket's time and the local time. 
The modul assumes that the sockets are internally running UCT (GMT) time. The default setting corrects between your local time and UCT. If this is not correct, you can apply a different time difference (in seconds).<dd>
</dl>

The function either returns a named tuple (`Timer`) (if the `which` argument is set to one timer) or a list of named tuples:
<dl>
<dt>number</dt>
<dd>The number of the timer. Ten timer slots are available (`1`-`10`). Another timer slot (no. 11) is the countdown timer and referred to as `'Countdown'`.</dd>
<dt>active</dt>
<dd>`True` or `False` when the timer is programmed (active or not) and `None` if the timer slot is empty.</dd>
<dt>repeat</dt>
<dd>A binary representation for daily repeat cycles, where each digit stands for a day in the week, starting at Monday. E.g.,
<ul>
<li>`'1111100'`: repeat from Monday to Friday</li>
<li>`'1111111'`: repeat every day</li>
<li>`'0000000'`: never repeat, just switch today</li>
</ul></dd>
<dt>time</dt>
<dd>When to switch, in 24-hour format (*hh:mm*).

Note: This modul assumes that the sockest are using UCT internally and corrects this to local time. If this is not correct, use the 'time_delta' argument (see above).</dd>
<dt>switch</dt>
<dd>What to do. Switch `'on'` or `'off'`.</dd>
</dl>

##### **set_timer(*socket_, timer, active, repeat, time_, switch, delta_time=None*)**
***
*Program a timer (or countdown) of a socket.*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>timer</dt>
<dd>Each socket has 10 timer slots (`1`-`10`) and one countdown slot (`11` or `'Countdown'`).</dd>
<dt>active</dt>
<dd>A timer can be programmed but does not need to be active. `True`  or `False`.</dd>
<dt>repeat</dt>
<dd>A binary representation for daily repeat cycles, where each digit stands for a day in the week, starting at Monday. E.g.,
<ul>
<li>`'1111100'`: repeat from Monday to Friday</li>
<li>`'1111111'`: repeat every day</li>
<li>`'0000000'`: never repeat, just switch today</li>
</ul></dd>
<dt>time_</dt>
<dd>Time in **hh:mm** format, e.g., `'13:25'`.</dd>
<dt>switch</dt>
<dd>`'on'` or `'off'`</dd>
<dt>delta_time</dt>
<dd>Difference between the socket's time and the local time.
The modul assumes that the sockets are internally running UCT (GMT) time. The default setting corrects between your local time and UCT. If this is not correct, you can apply a different time difference (in seconds).</dd>
</dl>

   
##### **set_countdown(*socket_, time_, switch, delta_time=None*)**
***
*Call set_timer with countdown-specific defaults.*

Helper function for easy setting of the countdown timer.
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>time_</dt>
<dd>Countdown time in **hh:mm** format, e.g., `'01:30'`.</dd>
<dt>switch</dt>
<dd>`'on'` or `'off'`</dd>
<dt>delta_time</dt>
<dd>Difference between the socket's time and the local time.
The modul assumes that the sockets are internally running UCT (GMT) time. The default setting corrects between your local time and UCT. If this is not correct, you can apply a different time difference (in seconds).</dd>
</dl>


##### **activate_timer(*socket_, timer, activate=True*)**
***
*Activate or deactivate an existing timer.*

Helper function to activate or deactivate an already programmed timer.
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>timer</dt>
<dd>The number of the programmed timer (`1`-`10`).</dd>
<dt>activate</dt>
<dd>`activate=True` (default) will activate the timer, `activate=False` will deactivate it. Deactivating a timer does not delete it, its settings will be kept.</dd>
</dl>


##### **delete_timer(*socket_, timer*)**
***
*Delete the given timer of the given socket.*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>timer</dt>
<dd>The number of the programmed timer (`1`-`10` or `'Countdown'`).</dd>
</dl>


##### **absence_mode_query(*socket_*)**
***
*Return the absence mode (antithief mode) data.*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
</dl>


##### **set_absence_mode(*socket_, active, from_, to_*)**
***
*Set absence (antithief) mode.*

In absence (or antithief) mode the socket switches on and off every 30 minutes.
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
<dt>active</dt>
<dd>`True` or `False` to activate absence mode. Actually, this parameter doesn't make too much sense, because the whole command must be send anyway. (Couldn't just send 'activate'...).</dd>
<dt>from_</dt>
<dd>Start of absence mode in **dd.mm.yyyy hh:mm** format, e.g., `'20.01.2023 22:00'`.</dd>
<dt>to_</dt>
<dd>Like `from_`.</dd>
</dl>


##### **delete_absence_mode(*socket_*)**
***
*Delete absence mode.*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
</dl>


##### **heartbeat(*socket_*)**
***
*Ask for heartbeat response of socket. Return `True` when alive.*
<dl>
<dt>socket_</dt>
<dd>A tuple of (MAC address, IP address) of the Wi-Fi socket.</dd>
</dl>


##### **send_password(*password, time_=30*)**
***
*Send the Wi-Fi password to a listening socket.*

Press the on/off button of the socket for 5 seconds until the LED starts flashing red quickly. Then use this command.
<dl>
<dt>password</dt>
<dd>The password of the wireless network.</dd>
<dt>time_</dt>
<dd>Duration (in seconds) how long the process should proceed. Default: 30 sec.</dd>
</dl>

    
## Helper Functions
Please consider them 'PRIVAT'.

##### **assemble_command(*mac, command*)**
***
*Assemble a valid command from different parts and return it.*

##### **encrypt(*command*)**
***
*Encrypt the command with AES/CBC.*

##### **decrypt(*message*)**
***
*Decrypt message with AES/CBS.*

##### **create_socket(*my_ip=my_ip, broadcast=False*)**
***
*Create an internet socket for UDP communication to (real) sockets.*
<dl>
<dt>broadcast</dt>
<dd>Set to `True` if the socket is for broadcasting UDP to all listening devices. If broadcast is `True`, the IP address is automatically set to `'255.255.255.255'`. Default: `False`.</dd>
</dl>


##### **send(*ip, command, broadcast=False*)**
***
*Send a command to a socket, receive and return the answer.*
<dl>
<dt>ip</dt>
<dd>The IP address of the device, given as dot-separated string.
Note that the IP address of a socket may change (when dynamically assigned). Use `find_sockets(mac)` to get the IP address of a certain device.</dd>
<dt>command</dt>
<dd>A command string in hex format (space-separated or not).</dd>
<dt>broadcast</dt>
<dd>Send to all devices in the local wireless network. Default is `False` which means that commands are usually send to a given device, defined by it's IP.</dd>
</dl>


##### **send_and_forget(*ip, command, broadcast=False*)**
***
*Just send a command to a socket once, do nothing else.*
