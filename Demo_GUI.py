import tkinter as tk
import tkinter.ttk as ttk

import wifisocket as ws


# Socket data, keys are the MACs. Replace data with your own set-up!
socket_data = {
    '00aa11bb22cc': {'name': 'Coffee Machine'},
    '00aa11bb44c0': {'name': 'Xmas Illumination'},
    '00aa11bb33ce': {'name': 'Dishwasher'}
}


def switch_button_state(mac):
    socket = (mac, socket_data[mac]['ip'])
    if ws.switch_state(socket) == 'on':
        on_buttons[mac].state(['disabled'])
        off_buttons[mac].state(['!disabled'])
    else:
        on_buttons[mac].state(['!disabled'])
        off_buttons[mac].state(['disabled'])


# Find IPs
ws.timeout = 5  # may be useful to find all devices
for key in socket_data:
    socket_data[key]['ip'] = ws.find_sockets(key).ip
ws.timeout = 3


# Set-up GUI
main_window = tk.Tk()
main_window.title('Demo GUI for wifisocket')
socket_panel = ttk.LabelFrame(main_window, text='Wi-Fi Sockets', padding=5)
socket_panel.pack()

on_buttons = {}
off_buttons = {}

for key in socket_data:
    temp_frame = ttk.LabelFrame(socket_panel, text=socket_data[key]['name'])

    on_buttons[key] = ttk.Button(
        temp_frame, text='ON', command=lambda key=key: switch(key, 'on')
    )
    off_buttons[key] = ttk.Button(
        temp_frame, text='OFF', command=lambda key=key: switch(key, 'off')
    )
    temp_frame.pack(padx=2, pady=10)
    on_buttons[key].pack(side='left', padx=5, pady=5)
    off_buttons[key].pack(side='left', padx=5, pady=5)

    switch_button_state(key)


def switch(mac, on_off):
    socket = (mac, socket_data[mac]['ip'])
    ws.switch(socket, on_off)
    switch_button_state(mac)


main_window.mainloop()
