# wifisocket.py
# Copyright 2022, Markus Piotrowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details <http://www.gnu.org/licenses/>.
"""
Module to control the Silvercrest SWS-A1 Wi-Fi sockets
======================================================
This module provides functions to control the Silvercrest SWS-A1 Wi-Fi sockets
(sold 2016 by Lidl) and similar devices sold by other vendors, e.g., the Aldi
Easy Home DIS-120.

The sockets are controlled by sending commands with UDP using the local
wireless network. For correct addressing, the IP address of the socket must
be known (you can use this module to get the required information).
Each command consist of an unencrypted 'header', containing the MAC address of
the socket and an AES/CBC encrypted part, containing a packet number, device
specific data and the command.
For more details about the data structure and the existing commands, please
visit http://www.fhemwiki.de/wiki/Silvercrest_SWS_A1_Wifi.

IMPORTANT: You need to install the third-party module `pycryptodome`

IMPORTANT: This module allows only access to sockets in the *local* wireless
network

Register a new socket in your local wireless network
----------------------------------------------------
Usually, the sockets are registered in the local Wi-Fi using an app. If they
are already connected to your Wi-Fi, there is no need to re-connect them.
However, if you need to connect a new socket or if your local Wi-Fi (or its
password) has changed, you can use the `send_password()` function:

    >>> import wifisocket as ws

Press the on/off button of the socket for 5 seconds until the LED starts
flashing red quickly. Then use this command:

    >>> ws.send_password(your_wifi_password)

The password will be transmitted to the socket for 30 sec. The LED of the
socket should stop flashing and become blue. Repeat if necessary.

Getting MAC and IP data from the sockets
----------------------------------------
For addressing the correct socket, you need to know its (fixed) MAC and
(possibly changing) IP addresses. You can collect these data from all
connected plugs at once:

    >>> import wifisocket as ws
    >>> my_sockets = ws.find_sockets()
    >>> print(my_sockets)
    [Socket(mac='xxxxxxxxxxxx', ip='yyy.yyy.yyy.yy'), Socket(mac='.........)]

If you only need the information of one socket, and you either know its MAC
or IP address, you can ask for this socket directly:

    >>> my_socket_1 = ws.find_sockets(mac='xxxxxxxxxxxx')  # or:
    >>> my_socket_2 = ws.find_socket(ip='yyy.yyy.yyy.yy)

In this case, you will only receive *one* tuple (`Socket(mac=xxxx, ip=....)`)
instead of a list. Note that the IP address may change dynamically (depending
on the settings of your local network router).

Sending commands
----------------
Most commands require the MAC and IP address of the addressed socket as
first positional argument in form of a tuple (`(mac, ip)`).

    :socket_: The tuple `(mac, ip)`
    :mac: Is the MAC address of the socket to which the command is sent.
        The MAC will be encoded within the command. It is given without colons
        but may be separated by spaces. '00010203abcd' and '00 01 02 03 ab cd'
        are both valid formats.
    :ip: Is the IP address which is assigned to the addressed socket in the
        local network. The IP address is required to send the command to the
        correct socket. `ip` is given in dot separated format, e.g.,
        '192.168.0.15'.

Since MAC and IP addresses of a device can be retrieved as a tuple by
`find_socket()`, a simple script to switch a socket on could look like this:

    >>> import wifisocket as ws
    >>> my_sockets = ws.find_sockets()
    >>> ws.switch(my_sockets[0], 'on')

This will switch on the first socket which was found by `find_socket()`.
The order of the sockets is somewhat random, (i.e. subsequent
calls of `find_socket()` may result in differently ordered lists) and it is
recommended to keep track of the different devices by storing or hard-coding
the sockets' MACs.

    >>> coffee_machine = 'ac bc de 01 02 03'  # MAC of the socket
    >>> my_sockets = {}
    >>> my_socket['coffee_machine'] = ws.find_sockets(mac=coffee_machine)
    >>> ws.switch(my_sockets['coffee_machine'], 'on')

Defaults
--------
Some command parameters are often the same, independent of the socket
which is being addressed. Nevertheless, it may be necessary or desirable
to have control over them, therefore, they have been coded as default
variables, which could be set by the user:

    >>> import wifisocket as ws
    >>> ws.device = ws.DIS_120  # Aldi Easy Home Wi-Fi adapter

These are the default global variables:

    :packet: Each command contains a packet number (counting up) and sockets
        will only accept commands that have a higher packet number than the
        command that was received before. However, the packet number can simply
        be set to 'FF FF', which is the highest value, because the socket will
        then start to count from the beginning. Therefore, `packet` defaults
        to 'FF FF'.
        So much for the story being told. In fact, this is nonsense and the
        packet number can be any value between '00 00' and 'FF FF' without any
        socket being bothered by it.
    :device: Is a hex code containing the company code, device code and
        authentication code. E.g., for Silvercrest's SWS-A1 sockets (sold by
        Lidl) this would be 'C1 11 71 50'. `device` defaults to `SWS_A1`
        (='C1 11 71 50').
    :udp_port: The UDP port for sending commands and receiving responses.
        Default port: 8530.
    :timeout: The time after which a command stops waiting for a response.
        A time-out is usually a sign that a command was not received or not
        understood. The function then returns `'Timeout'`. Default: 2 seconds.
    :repeat: How often is a command repeated in case that no valid response is
        received. Default: 3.

Available commands
------------------
Use these commands to control your sockets:

    :switch(socket, on_off): To switch a socket 'on' or 'off'. 
    :switch_state(socket): Returns 'on' or 'off'.
    :switch_slave(socket, slave, on_off): To switch a radio-controlled
        slave socket. Not tested!
    :timer_query(socket, which='all', delta_time=None): Returns data
        about the programmed timers of a socket.
    :set_timer(socket, timer, active, repeat, time, switch, delta_time=None):
        To program a timer.
    :set_countdown(socket, time, switch, delta_time=None):
        To program a countdown.
    :activate_timer(socket, timer, activate=True): To activate or
        deactivate a programmed timer.
    :delete_timer(socket, timer): To delete a programmed timer.
    :absence_mode_query(socket): Returns data about absence mode.
    :set_absence_mode(socket, active, from, to): To program absence mode
    :delete_absence_mode(socket): To delete absence mode.

Final notes
-----------
UDP communication is error-prone, therefore you should always check if things
are as you expect them to be. E.g. a `find_sockets()` call may not necessarily
return a list of all connected sockets. The above shown series of commands

    >>> import wifisocket as ws
    >>> my_sockets = ws.find_sockets()
    >>> ws.switch(my_sockets[0], 'on')

is not really recommended, since `my_sockets` could be empty (although you
have several sockets operating) and the use of the `switch` function would
then result in an exception. In this example, you could check if `my_sockets`
is not empty.

Commands that do not retrieve data (like `switch()`) still receive a receipt
and will return `True` if the receipt was OK, otherwise they return
`'Timeout'`, `'Bad return data'` or an error message. It is recommended to
check the return values.
"""
import socket
import time
import datetime

from collections import namedtuple

from Crypto.Cipher import AES # Need to install 'pycryptodome' before


###### CONSTANTS
# En- and decryption
PASSKEY = b'0123456789abcdef'
INITIALIZATION_VECTOR = PASSKEY

# Device codes
SWS_A1 = 'C1 11 71 50'  # Silvercrest, sold by Lidl
DIS_120 = 'C2 11 92 DD'  # Aldi Easy Home
U_DEVICE = 'CA A1 88 98'  # (To me) Unknown device

# Commands
CMD_INIT = '01 40 {mac} ' # 01: constant, 40: send
CMD_HEADER = '00 {packet} {device} '

CMD_SEARCH = '23 {mac} 02 02'

CMD_SWITCH = '01 {switch} 04 04 04 04'  # 00 00 FF FF: on, 00 00 00 FF: off
CMD_GET_STATE = '02 00 00 00 00 04 04 04 04'

CMD_TIMER_QUERY = '04 00 00 06 06 06 06 06 06'
CMD_SET_TIMER = ('03 00 {timer} {repeat} {hour} {minute} {switch} '
                 '0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F 0F')
CMD_DELETE_TIMER = '05 00 {timer:02x} 06 06 06 06 06 06'

# EXPERIMENTAL! NOT TESTED!
CMD_SWITCH_SLAVE = '08 {slave} {switch} 04 04 04 04'  # switch: 60: on, 70: off

# AM is "absence mode" or "antithief"
CMD_AM_QUERY = '0A 08 08 08 08 08 08 08 08'
CMD_SET_AM = (
    '09 {active} {from_:08x} {to_:08x} 1E '
    '0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E')
CMD_DELETE_AM = (
    '09 00 00 00 00 00 00 00 00 00 0E '
    '0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E 0E')

CMD_HEARTBEAT = '61 55 93 26 54 04 04 04 04'
# CMD_HEARTBEAT = '61 {timestamp:08x} 04 04 04 04'  # in app: with timestamp

CMD_VERSION = '62 08 08 08 08 08 08 08 08'  # get version/name

###### DEFAULTS 
device = SWS_A1
packet = 'FF FF'

udp_port = 8530
timeout = 2

repeat = 3

my_ip = socket.gethostname()


def find_sockets(mac='FF FF FF FF FF FF', ip='255.255.255.255'):
    """Broadcast status query and collect MAC and IP data of all sockets.

    Using this function with standard arguments (`find_sockets()`) will return
    a list of all available/connected sockets. You can search for a certain
    socket either by giving its MAC or IP address.

    Note that the MAC address is a fixed number of a device, while the IP
    depends on the network to which the socket is connected and may also
    change dynamically over time.

    The return value is a list of named tuples `[(Socket(mac=..., ip=...)',
    ...]` or just a named tuple if the socket was defined by it's MAC or
    IP address.
    """
    s = create_socket(broadcast=True)
    socket_data = []
    Socket = namedtuple('Socket', 'mac ip')
    address = (ip, udp_port)

    cmd = assemble_command(mac, CMD_SEARCH.format(mac=mac))
    send_command = bytes.fromhex(cmd)
    s.sendto(send_command, address)

    while True:
        try:
            message = s.recv(1024)
        except socket.timeout:
            break
        if (message[1] != 66 or len(message[9:]) % 16 != 0):
            continue
        message = decrypt(message[9:])
        mac_ = message[12:18].hex()
        ip_ = f'{message[8]}.{message[9]}.{message[10]}.{message[11]}'
        socket_data.append(Socket(mac_, ip_))
    s.close()
    if mac != 'FF FF FF FF FF FF' or ip != '255.255.255.255':
        socket_data = socket_data[0]  # Don't need a list, just one socket
    return socket_data


def switch(socket_, on_off):
    """Switch the socket on or off.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket
    :on_off: `'on'` or `'off'` to switch on or off
    """
    mac, ip = socket_
    if on_off == 'on':
        cmd = assemble_command(mac, CMD_SWITCH.format(switch='00 00 FF FF'))
    elif on_off == 'off':
        cmd = assemble_command(mac, CMD_SWITCH.format(switch='00 00 00 FF'))

    success, message = send(ip, cmd)
    if success:
        return success
    else:
        return message


def switch_state(socket_):
    """Return the swicht state of a socket (`'on'` or `'off'`).

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket
    """
    mac, ip = socket_
    cmd = assemble_command(mac, CMD_GET_STATE)
    success, message = send(ip, cmd)
    if success:
        message = decrypt(message)
        if message[10] == 0:
            return 'off'
        elif message[10] == 255:
            return 'on'
    else:
        return message


def switch_slave(socket_, slave, on_off):
    """Switch the slave socket on or off.

    To switch the radio-controlled 433 Mhz slave sockets (e.g., ALDI Easy
    Home kit)

    EXPERIMENTAL! I haven't tested this.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :slave: 3-byte long hex, like '78fb12'. Like a MAC address, this is a
        specific number of the radio slave sockets.
    :on_off: `'on'` or `'off'` to switch on or off.
    """
    mac, ip = socket_
    if on_off == 'on':
        cmd = assemble_command(
            mac, CMD_SWITCH_SLAVE.format(slave=slave, switch='60'))
    elif on_off == 'off':
        cmd = assemble_command(
            mac, CMD_SWITCH_SLAVE.format(slave=slave, switch='70'))

    success, message = send(ip, cmd)
    if success:
        return success
    else:
        return message


def timer_query(socket_, which='all', delta_time=None):
    """Return the timer data for a given socket.

    Each socket has 10 timer slots (no. 1-10) and one countdown slot.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :which: Allows to select which timers are reported. Options:
        'all': all timers (default)
        1-10 or 'Countdown': the respective timer
        'set': all programmed timers (if active or not)
        'active': only the active timers
        'free': non-programmed timer slots, will only return a list of the
        free timer numbers.
    :delta_time: Difference between the socket's time and the local time.
        The modul assumes that the sockets are internally running UCT (GMT)
        time. The default setting corrects between your local time and UCT.
        If this is not correct, you can apply a different time difference
        (in seconds).

    The function either returns a named tuple (`'Timer'`) (if the `which`
    argument is set to one timer) or a list of named tuples:
    :number: The number of the timer. Ten timer slots are available (`1`-`10`).
        Another timer slot (no. 11) is the countdown timer and referred to
        as `'Countdown'`.
    :active: `'True'` or `'False'` when the timer is programmed (active or not)
        and `'None'` if the timer slot is empty.
    :repeat: A binary representation for daily repeat cycles, where each digit
        stands for a day in the week, starting at Monday. E.g.,
        `'1111100'`: repeat from Monday to Friday
        `'1111111'`: repeat every day
        `'0000000'`: never repeat, just switch today
    :time: When to switch, in 24-hour format (hh:mm). Note: This modul assumes
        that the sockest are using UCT internally and corrects this to local
        time. If this is not correct, use the 'time_delta' argument (see above).
    :switch: What to do. Switch `'on'` or `'off'`.
    """
    mac, ip = socket_
    cmd = assemble_command(mac, CMD_TIMER_QUERY)
    success, message = send(ip, cmd)
    data = []
    Timer = namedtuple('Timer', 'number active repeat time switch',
                       defaults=('', '', ''))
    
    if success:
        message = decrypt(message)
        m = message[9:]
        if not delta_time:
            delta_time = time.timezone
        for n in range(0, 88, 8):  # Rest of message are just padding bytes
            number = m[n] if n < 80 else 'Countdown'  # Timer 11 is Countdown
            active = True if f'{m[n + 1]:08b}'[0] == '1' else False
            repeat = f'{m[n + 1]:08b}'[-1:0:-1]  # discard bit 1 and reverse
            switch = 'on' if m[n+4:n+8].hex() == "0000ffff" else 'off'
            if m[n + 2] == 255:
                time_ = None
            else:
                hour, minute = f'{m[n + 2]} {m[n + 3]}'.split()
                time_ = (datetime.datetime(1, 1, 2, int(hour), int(minute))
                         - datetime.timedelta(seconds=delta_time))
                if number == 'Countdown':
                    now = datetime.datetime.now()
                    time_ -= datetime.timedelta(hours=now.hour,
                                                minutes=now.minute)
                hour, minute = time_.hour, time_.minute
                time_ = f'{hour:02d}:{minute:02d}'
            if (
                which == 'all' or which == number
                or (which == 'active' and active)
                or (which == 'set' and time_ != None)
                or (which =='free' and time_ == None)
                ):
                if time_ == None:
                    if which =='free':
                        data.append(number)
                    else:
                        data.append(Timer(number, None))
                else:
                    data.append(Timer(number, active, repeat, time_, switch))
            if which == number:
                data = data[0]  # Don't return a list, just the requested timer
                break
        return data
    else:
        return message


def set_timer(socket_, timer, active, repeat, time_, switch, delta_time=None):
    """Program a timer (or countdown) of a socket.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :timer: Each socket has 10 timer slots (`1`-`10`) and one countdown slot
        (`11` or `'Countdown'`).
    :active: A timer can be programmed but does not need to be active. `True`
        or `False`.
    :repeat: A binary representation for daily repeat cycles, where each digit
        stands for a day in the week, starting at Monday. E.g.,
        '1111100': repeat from Monday to Friday
        '1111111': repeat every day
        '0000000': never repeat, just switch today
    :time_: Time in hh:mm format, e.g., `'13:25'`.
    :switch: `'on'` or `'off'`
    :delta_time: Difference between the socket's time and the local time.
        The modul assumes that the sockets are internally running UCT (GMT)
        time. The default setting corrects between your local time and UCT.
        If this is not correct, you can apply a different time difference
        (in seconds).
    """
    mac, ip = socket_
    repeat = f'{int(("1" if active else "0") + repeat[::-1], 2):02x}'

    hour, minute = (int(x) for x in time_.split(':'))
    if timer == 11 or timer == 'Countdown':  # Countdown
        time_ = datetime.datetime.now()
        time_ += datetime.timedelta(hours=hour, minutes=minute)
        timer = 11
        # Countdowns are always active and don't repeat: 
        repeat = f'{int("10000000", 2):02x}'
    else:
        time_ = datetime.datetime(1, 1, 2, hour, minute)
    if not delta_time:
            delta_time = time.timezone
    time_ += datetime.timedelta(seconds=delta_time)
    hour, minute = f'{time_.hour:02x} {time_.minute:02x}'.split()

    timer = f'{timer:02x}'

    switch = '00 00 FF FF' if switch == 'on' else '00 00 00 FF'

    cmd = assemble_command(
        mac,
        CMD_SET_TIMER.format(
            timer=timer, repeat=repeat, hour=hour,
            minute=minute, switch=switch)
        )
    
    success, message = send(ip, cmd)
    if success:
        return success
    else:
        return message


def set_countdown(socket_, time_, switch, delta_time=None):
    """Call set_timer with countdown-specific defaults.

    Helper function for easy setting of the countdown.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :time_: Countdown time in hh:mm format, e.g., `'01:30'`.
    :switch: `'on'` or `'off'`
    :delta_time: Difference between the socket's time and the local time.
        The modul assumes that the sockets are internally running UCT (GMT)
        time. The default setting corrects between your local time and UCT.
        If this is not correct, you can apply a different time difference
        (in seconds).
    """
    set_timer(socket_, 11, True, '0000000', time_, switch, delta_time)


def activate_timer(socket_, timer, activate=True):
    """Activate or deactivate an existing timer.

    Helper function to activate or deactivate an already programmed timer.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :timer: The number of the programmed timer (1-10).
    :activate: `activate=True` (default) will activate the timer,
        `activate=False` will deactivate it. Deactivating a timer does not
        delete it, it's settings will be kept.
    """
    data = timer_query(socket_, which=timer)
    set_timer(socket_, timer, activate, data.repeat, data.time, data.switch)


def delete_timer(socket_, timer):
    """Delete the given timer of the given socket.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :timer: The number of the programmed timer (`1`-`10` or `'Countdown'`).
    """
    mac, ip = socket_
    if timer == 'Countdown':
        timer = 11
    cmd = assemble_command(mac, CMD_DELETE_TIMER.format(timer=timer))
    success, message = send(ip, cmd)
    if success:
        return success
    else:
        return message


def absence_mode_query(socket_):
    """Return the absence mode (antithief mode) data.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    """
    mac, ip = socket_
    cmd = assemble_command(mac, CMD_AM_QUERY)
    success, message = send(ip, cmd)
    if success:
        message = decrypt(message)[7:]
        on = True if message[1] == 128 else False
        Absence = namedtuple('Absence', 'active from_ to_',
                             defaults=(None, None))
        if on:
            timestamp = int.from_bytes(message[2:6], byteorder='big')
            date = datetime.datetime.fromtimestamp(timestamp)
            from_ = date.strftime('%d.%m.%Y %H:%M')
            timestamp = int.from_bytes(message[6:10], byteorder='big')
            date = datetime.datetime.fromtimestamp(timestamp)
            to_ = date.strftime('%d.%m.%Y %H:%M')
            return Absence(on, from_, to_)
        else:
            return Absence(on)
    else:
        return message


def set_absence_mode(socket_, active, from_, to_):
    """Set absence (antithief) mode.

    In absence (or antithief) mode the socket switches on and off every
    30 minutes.
    
    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    :active: `True` or `False` to activate absence mode. Actually, this
        parameter doesn't make too much sense, because the whole command
        must be send anyway. (Couldn't just send 'activate'...)
    :from_: Start of absence mode in dd.mm.yyyy hh:mm format, e.g.,
        `'20.01.2023 22:00'`.
    :to_: Like `from_`.
    """
    mac, ip = socket_
    active = '80' if active else '00'
    try:
        date = datetime.datetime.strptime(from_, '%d.%m.%Y %H:%M')
        from_ = int(date.timestamp())
        date = datetime.datetime.strptime(to_, '%d.%m.%Y %H:%M')
        to_ = int(date.timestamp())
    except Exception as e:
        return e
    cmd = assemble_command(
            mac, CMD_SET_AM.format(active=active, from_=from_, to_=to_))

    success, message = send(ip, cmd)
    if success:
        return success
    else:
        return message


def delete_absence_mode(socket_):
    """Delete absence mode.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket.
    """
    mac, ip = socket_
    cmd = assemble_command(mac, CMD_DELETE_AM)
    success, message = send(ip, cmd)
    if success:
        return True
    else:
        return message


def heartbeat(socket_):
    """Ask for heartbeat response of socket. Return `True` when alive.

    :socket_: A tuple of (MAC address, IP address) of the Wi-Fi socket."""
    mac, ip = socket_
    cmd = assemble_command(mac, CMD_HEARTBEAT)
    success, message = send(ip, cmd)  
    if success:
        return True
    else:
        return message


def send_password(password, time_=30):
    """Send the Wi-Fi password to a listening socket.

    Press the on/off button of the socket for 5 seconds until the LED starts
    flashing red quickly. Then use this command.
    
    :password: The password of the wireless network.
    :time_: Duration (in seconds) how long the process should proceed.
        Default: 30 sec.
    """
    UDP_PORT = 49999
    s = create_socket('None', broadcast=True)
    address = ('255.255.255.255', UDP_PORT)

    len_ = len(password)
    now = time.time()

    while time.time() < (now + time_):  # Try for 30 seconds
        # Init
        for n in range(60):
            s.sendto(bytes.fromhex(76 * '05'), address)
            time.sleep(0.01)

        # Transfer password
        for n in range(5):
            # 'Start'
            s.sendto(bytes.fromhex(89 * '05'), address)
            time.sleep(0.05)
            s.sendto(bytes.fromhex(89 * '05'), address)
            time.sleep(0.05)
            s.sendto(bytes.fromhex(89 * '05'), address)
            time.sleep(0.1)

            # 'Password'
            for letter in password:
                s.sendto(bytes.fromhex((ord(letter) + 76) * '05'), address)
                time.sleep(0.1)

            # 'End'
            s.sendto(bytes.fromhex(86 * '05'), address)
            time.sleep(0.05)
            s.sendto(bytes.fromhex(86 * '05'), address)
            time.sleep(0.05)
            s.sendto(bytes.fromhex(86 * '05'), address)
            time.sleep(0.2)

            # 'Length of Password'
            s.sendto(bytes.fromhex((len_ + 256 + 76) * '05'), address)
            time.sleep(0.05)
            s.sendto(bytes.fromhex((len_ + 256 + 76) * '05'), address)
            time.sleep(0.05)
            s.sendto(bytes.fromhex((len_ + 256 + 76) * '05'), address)
            time.sleep(0.5)


###### Helper functions, consider them 'PRIVAT'

def assemble_command(mac, command):
    """Assemble a valid command from different parts and return it.""" 
    uncrypted_part = CMD_INIT.format(mac=mac)
    header = CMD_HEADER.format(packet=packet, device=device)
    crypted_part = encrypt(bytes.fromhex(header + command))
    return (
        uncrypted_part
        + len(crypted_part).to_bytes(1, 'big').hex()
        + crypted_part.hex())    


def encrypt(command):
    """Encrypt the command with AES/CBC."""
    cipher =AES.new(PASSKEY, AES.MODE_CBC, iv=INITIALIZATION_VECTOR)
    return cipher.encrypt(command)


def decrypt(message):
    """Decrypt message with AES/CBS."""
    cipher = AES.new(PASSKEY, AES.MODE_CBC, iv=INITIALIZATION_VECTOR)
    return cipher.decrypt(message)


def create_socket(my_ip=my_ip, broadcast=False):
    """Create an internet socket for UDP communication to (real) sockets.

    :broadcast: Set to `True` if the socket is for broadcasting UDP to all
                listening devices. If broadcast is `True`, the IP address is
                automatically set to `'255.255.255.255'`. Default: `False`.

    Note that the IP address of a socket may change (when dynamically assigned).
    Use `find_sockets(mac)` to get the IP address of a certain device. 
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if broadcast:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(timeout)
    s.bind((my_ip, udp_port))
    return s


def send(ip, command, broadcast=False):
    """Send a command to a socket, receive and return the answer.

    :ip: The IP address of teh device, given as dot-separated string.
        Note that the IP address of a socket may change (when dynamically
        assigned). Use `find_sockets(mac)` to get the IP address of a
        certain device.
    :command: A command string in hex format (space-speparated or not)
    :broadcast: Send to all devices in the local wireless network. Default
        is `False` which means that commands are usually send to a given
        device, defined by it's IP.
    """
    if broadcast:
        s = create_socket(broadcast)
        ip = '255.255.255.255'
    else:
        s = create_socket()
    address = (ip, udp_port)
    send_command = bytes.fromhex(command)
    for n in range(repeat):
        try:
            s.sendto(send_command, address)
        except OSError as message:
            s.close()
            return False, message
        try:
            message = s.recv(1024)
        except socket.timeout:
            message = 'Timeout'
            continue
        if (message[1] != 66 or len(message[9:]) % 16 != 0):
            message = 'Bad return data'
            time.sleep(0.5)
            continue
        s.close()
        return True, message[9:]
    s.close()
    return False, message


def send_and_forget(ip, command, broadcast=False):
    """Just send a command to a socket once, do nothing else."""
    if broadcast:
        s = create_socket(broadcast)
        ip = '255.255.255.255'
    else:
        s = create_socket()
    s.sendto(bytes.fromhex(command), (ip, udp_port))
    s.close()
