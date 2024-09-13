![Static Badge](https://img.shields.io/badge/Language%3A_-_Python_v.3.11.9-blue)

# WEB SHELL CHECKER 
Simple tool for massive shells check. Checks few system commands on provided web shells  
and parses response, creates files with working and not working 

## Usage 
Install dependencies 
```
pip install -r requirements.txt
```

Run 
```
python shell-checker.py -l <path to list with web shells>
```

To add this script to scheduler run
```
chmod +x checker-cron-job.sh
sudo ./checker-cron-jib.sh
```