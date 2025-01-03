chmod +x /home/pi/KotamechWireSpooler/program.py
ln -s /home/pi/KotamechWireSpooler/setup/wire_spooler.service /etc/systemd/system/wire_spooler.service
systemctl enable wire_spooler.service
