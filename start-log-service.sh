#pkill -9 node

# Old
#nohup log.io-startup &> /var/log/log.io.txt &

# New
#nohup log.io-file-input &> /var/log/log.io.txt & 
#nohup log.io-server &> /var/log/log.io.txt &
