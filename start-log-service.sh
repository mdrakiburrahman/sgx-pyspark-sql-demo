pkill -9 node
nohup log.io-startup &> /var/log/log.io.txt &
nohup log.io-file-input &> /var/log/log.io.txt & 
nohup log.io-server &> /var/log/log.io.txt &
