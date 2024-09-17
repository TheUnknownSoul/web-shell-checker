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

Additional options
```
-debug: Optional parameter. Detailed request and response output.
-verbose: Optiuonal parameter. Prints result of what line is now in process and detailed message for current shell.
```

To add this script to scheduler run
```
chmod +x checker-cron-job.sh
sudo ./checker-cron-job.sh
```

## Technical information
Due to some technical reasons in this tool implemented some restrictions in requests setup.
First of all it ignores invalid or self-signed certificate. Second, timeout option, redirects and amount of retries. 
* Timeout = 7 sec 
* Max retries = 5
* Redirects = 3. 

Retries forced also on 500, 502, 503, 504 status code.
In some cases if amount of shell are huge and internet connection unstable implemented 5 retry for function that sends 
request after 10 seconds of pause. For now this feature hasn't tested properly.

Supports file in `.txt` and `.csv` file extension.