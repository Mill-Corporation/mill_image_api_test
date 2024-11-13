#!/bin/bash

# 스크립트에 인자로 새로운 번호를 전달 (예: 1234)
NEW_NUMBER=$1

if [ -z "$NEW_NUMBER" ]; then
  echo "Usage: $0 <new_number>"
  exit 1
fi

# 1. sudo pkill -f python (Python 프로세스 종료)
sudo pkill -f python

# 2. crontab에서 9999를 새로운 번호로 변경
# 현재 crontab을 임시 파일로 저장
crontab -l > temp_crontab

# temp_crontab 파일에서 9999를 NEW_NUMBER로 치환
sed -i "s/9999/$NEW_NUMBER/g" temp_crontab

# 수정된 crontab 파일 다시 로드
sudo crontab temp_crontab
rm temp_crontab

# 3. /etc/hostname 파일에서 9999를 NEW_NUMBER로 변경
sudo sed -i "s/MVPC9999/MVPC$NEW_NUMBER/g" /etc/hostname

# 4. /etc/hosts 파일에서 9999를 NEW_NUMBER로 변경
sudo sed -i "s/MVPC9999/MVPC$NEW_NUMBER/g" /etc/hosts

echo "Script execution completed. Please reboot the system for changes to take effect."

