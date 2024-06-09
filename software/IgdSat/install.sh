# by Megazar21 at 9/6/2024
# IgdSat full installation script starting from a clean Raspberry Pi OS Lite on a Raspberry Pi Zero 2W 
#

sudo apt update && apt upgrade
sudo apt install git python3-pip openvpn -y
sudo apt install -y python3-picamera2 --no-install-recommends 
mkdir ~/IgdSat-DATA
mkdir ~/IgdSat-DATA/IMAGES

# Enable i2c and serial interfaces
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial_hw 0
# Disable console on serial ports
sudo raspi-config nonint do_serial_cons 1

# Disable ModemManager to avoid interferences with AT commands
sudo systemctl disable ModemManager

# Clone the git repo
cd ~/
git clone https://github.com/IgualadaSat/IgdSat.git

# Add service file
sudo cp ~/IgdSat/software/IgdSat/igdsat.service /lib/systemd/system/igdsat.service
# enable service file
sudo systemctl enable igdsat

# Finally, reboot the system
sudo reboot