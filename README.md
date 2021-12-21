# SurfShark VPN GUI

A GUI client for connecting to the SurfShark VPN.

![surfshark-vpn-gui](https://user-images.githubusercontent.com/554899/79762280-8f876b00-82f0-11ea-9d4a-e050498f8bc7.png)

### About

There is currently no official GUI client for the SurfShark VPN on Linux, so this is to fill the need! This client uses OpenVPN to setup the connection, so the surfshark-vpn package is not required.

### Instructions

0. (Prep) Install Dependencies:
  ```
   sudo apt install git openvpn python3 python3-pip libgtk-3-dev python3-requests python3-setuptools python3-wxgtk4.0
  ```
1. Clone the surfshark-vpn-gui repo:
  ```
   git clone --depth 1 https://github.com/jakeday/surfshark-vpn-gui.git
  ```
2. Change directory to surfshark-vpn-gui repo:
  ```
   cd surfshark-vpn-gui/
  ```
3. Install the app:
  ```
   pip install .
  ```
4. With the client open, be sure to enter your SurfShark credentials by clicking the Enter Credentials button.

### Donations Appreciated!

PayPal: https://www.paypal.me/jakeday42

Bitcoin: 1AH7ByeJBjMoAwsgi9oeNvVLmZHvGoQg68
