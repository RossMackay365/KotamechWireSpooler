chmod +x /home/pi/KotamechWireSpooler/program.py
ln -s /home/pi/KotamechWireSpooler/setup/wire_spooler.service /etc/systemd/system/wire_spooler.service
systemctl enable wire_spooler.service

# Update service
chmod +x /home/pi/KotamechWireSpooler/update/update.py
ln -s /home/pi/KotamechWireSpooler/update/wire_spooler_oneshot_update.service /etc/systemd/system/wire_spooler_oneshot_update.service
systemctl enable wire_spooler_oneshot_update.service
