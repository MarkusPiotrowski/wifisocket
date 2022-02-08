# Module to control the Silvercrest SWS-A1 Wi-Fi sockets
This module provides functions to control the Silvercrest SWS-A1 Wi-Fi sockets
(sold 2016 by Lidl) and similar devices sold by other vendors, e.g., the Aldi
Easy Home DIS-120.

The sockets are controlled by sending commands with UDP using the local wireless
network. For correct addressing, the IP address of the socket must be known (you
can use this module to get the required information). Each command consist of an
unencrypted 'header', containing the MAC address of the socket and an AES/CBC
encrypted part, containing a packet number, device specific data and the command.

For more details about the data structure and the existing commands, please
visit http://www.fhemwiki.de/wiki/Silvercrest_SWS_A1_Wifi.

IMPORTANT: You need to install the third-party module `pycryptodome`  
IMPORTANT: This module allows only access to sockets in the *local* wireless
network

Register a new socket in your local wireless network
----------------------------------------------------
Usually, the sockets are registered in the local Wi-Fi using an app. If they are
already connected to your Wi-Fi, there is no need to re-connect them. However,
if you need to connect a new socket or if your local Wi-Fi (or its password) has
changed, you can use the `send_password()` function:

    >>> import wifisocket as ws

Press the on/off button of the socket for 5 seconds until the LED starts flashing
red quickly. Then use this command:

    >>> ws.send_password(your_wifi_password)

The password will be transmitted to the socket for 30 sec. The LED of the socket
should stop flashing and become blue. Repeat if necessary.

Getting MAC and IP data from the sockets
----------------------------------------
For addressing the correct socket, you need to know its (fixed) MAC and
(possibly changing) IP addresses. You can collect these data from all connected
plugs at once:

    >>> import wifisocket as ws
    >>> my_sockets = ws.find_sockets()
    >>> print(my_sockets)
    [Socket(mac='xxxxxxxxxxxx', ip='yyy.yyy.yyy.yy'), Socket(mac='.........)]

If you only need the information of one socket, and you either know its MAC or IP
address, you can ask for this socket directly:

    >>> my_socket_1 = ws.find_sockets(mac='xxxxxxxxxxxx')  # or:
    >>> my_socket_2 = ws.find_socket(ip='yyy.yyy.yyy.yy)

In this case, you will only receive *one* tuple (`Socket(mac=xxxx, ip=....)`)
instead of a list. Note that the IP address may change dynamically (depending on
the settings of your local network router).

Sending commands
----------------
Most commands require the MAC and IP address of the addressed socket as the first
positional argument in the form of a tuple `(mac, ip)`.

- **socket_**: The tuple `(mac, ip)`.
- **mac**: Is the MAC address of the socket to which the command is sent. The
MAC will be encoded within the command. It is given without colons, but may be
separated by spaces. `'00010203abcd'` and `'00 01 02 03 ab cd'` are both valid
formats.
- **ip**: Is the IP address which is assigned to the addressed socket in the
local network. The IP address is required to send the command to the correct
socket. `ip` is given in dot separated format, e.g., `'192.168.0.15'`.

Since MAC and IP addresses of a device can be retrieved as a tuple by
`find_socket()`, a simple script to switch a socket on could look like this:

    >>> import wifisocket as ws
    >>> my_sockets = ws.find_sockets()
    >>> ws.switch(my_sockets[0], 'on')

This will switch on the first socket which was found by `find_socket()`. The
order of the sockets is somewhat random, (i.e. subsequent calls of `find_socket()`
may result in differently ordered lists) and it is recommended to keep track of
the different devices by storing or hard-coding the sockets' MACs.

    >>> coffee_machine = 'ac bc de 01 02 03'  # MAC of the socket
    >>> my_sockets = {}
    >>> my_socket['coffee_machine'] = ws.find_sockets(mac=coffee_machine)
    >>> ws.switch(my_sockets['coffee_machine'], 'on')

Defaults
--------
Some command parameters are often the same, independent of the socket which is
being addressed. Nevertheless, it may be necessary or desirable to have control
over them, therefore, they have been coded as default variables, which could be
set by the user:

    >>> import wifisocket as ws
    >>> ws.device = ws.DIS_120  # Aldi Easy Home Wi-Fi adapter

These are the default global variables:

- **packet**: Each command contains a packet number (counting up) and sockets
will only accept commands that have a higher packet number than the command that
was received before. However, the packet number can simply be set to `'FF FF'`,
which is the highest value, because the socket will then start to count from the
beginning. Therefore, `packet` defaults to `'FF FF'`.  
So much for the story being told. In fact, this is nonsense, and the packet
number can be any value between `'00 00'` and `'FF FF'` without any socket being
bothered by it.
- **device**: Is a hex code containing the company code, device code and
authentication code. E.g., for Silvercrest's SWS-A1 sockets (sold by Lidl) this
would be 'C1 11 71 50'. `device` defaults to `SWS_A1` (='C1 11 71 50').
- **udp_port**: The UDP port for sending commands and receiving responses.
**Default port**: 8530.
- **timeout**: The time after which a command stops waiting for a response. A
time-out is usually a sign that a command was not received or not understood.
The function then returns `'Timeout'`. **Default**: 2 seconds.
- **repeat**: How often is a command repeated in case that no valid response is
received. **Default**: 3.


Available commands
------------------
Use these commands to control your sockets:

- **switch(*socket, on_off*)**  
To switch a socket 'on' or 'off'.
- **switch_state(*socket*)**  
Returns 'on' or 'off'.
- **switch_slave(*socket, slave, on_off*)**  
To switch a radio-controlled slave socket. Not tested!
- **timer_query(*socket, which='all', delta_time=None*)**  
Returns data about the programmed timers of a socket.
- **set_timer(*socket, timer, active, repeat, time, switch, delta_time=None*)**  
To program a timer.
- **set_countdown(*socket, time, switch, delta_time=None*)**  
To program a countdown.
- **activate_timer(*socket, timer, activate=True*)**  
To activate or deactivate a programmed timer.
- **delete_timer(*socket, timer*)**  
To delete a programmed timer.
- **absence_mode_query(*socket*)**  
Returns data about absence mode.
- **set_absence_mode(*socket, active, from, to*)**  
To program absence mode.
- **delete_absence_mode(*socket*)**  
To delete absence mode.


Final notes
-----------
UDP communication is error-prone, therefore you should always check if things
are as you expect them to be. E.g., a `find_sockets()` call may not necessarily
return a list of all connected sockets. The above shown series of commands:

    >>> import wifisocket as ws
    >>> my_sockets = ws.find_sockets()
    >>> ws.switch(my_sockets[0], 'on')

is not really recommended, since `my_sockets` could be empty (although you have
several sockets operating) and the use of the `switch` function would then result
in an exception. In this example, you could check if `my_sockets` is not empty.

Commands that do not retrieve data (like `switch()`) still receive a receipt and
will return `True` if the receipt was OK, otherwise they return `'Timeout'`,
`'Bad return data'` or an error message. It is recommended to check the return
values.