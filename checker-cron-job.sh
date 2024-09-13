#!/bin/bash
current_directory=$(pwd)

directory="$current_directory"

if [ "$(python -V)" != 'Python 3.11.9' ]; then
    echo 'Need Python as symlink'
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
  echo 'Root rights required.'
  exit 1
else

touch /etc/cron.d/shell-checker.sh
cat << EOF > /etc/cron.d/shell-checker.sh
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
13 10 * * Mon python $directory/shell-checker.py
EOF

fi