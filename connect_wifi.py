def connect():
    import network
    from utime import sleep
    import wifi_cred

    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    # ap_if.active(True)
    # ap_if.config(essid='esp_red_blue', channel=6, password='logonpass')
    ap_if.active(False)

    print('connecting to network', end='')
    if sta_if.isconnected():
        print('\nAlready connected')
        return True

    sta_if.active(True)
    sta_if.connect(wifi_cred.SSID, wifi_cred.PASS)

    count = 0
    while not sta_if.isconnected() and count < 20:
        print('.', end='')
        sleep(1)
        count += 1

    print()
    if count == 20:
        return False

    return True

def disconnect():
    import network

    sta_if = network.WLAN(network.STA_IF)
    sta_if.disconnect()
    sta_if.active(False)

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

def reconnect():
    import network
    from utime import sleep

    print('Reconnecting to network')
    disconnect()
    sleep(2)
    connect()
