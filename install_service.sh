#!/bin/bash

# Copy the service file to systemd directory
sudo cp clubalpin_rss.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start at boot
sudo systemctl enable clubalpin_rss

# Start the service
sudo systemctl start clubalpin_rss

# Check the status
sudo systemctl status clubalpin_rss
