#! /usr/bin/bash

path=$PWD

if ! python3 setup.py "$path" ; then
    >&2 echo "生成service文件失败，退出"
    exit 1
fi

if [ ! -f "tgbot.service" ]; then
    >&2 echo "service文件经检测未生成或无法找到。安装失败。"
else
    if [ ! -d "/lib/systemd/system" ]; then
        mkdir /lib/systemd/system
    fi

    if cp ./tgbot.service /lib/systemd/system/ ; then
        echo "安装成功。"
        echo "现在你可以使用 'systemctl start tgbot' 启动"
        echo "或使用 'systemctl enable tgbot' 设置开机启动"
    else 
        >&2 echo "安装失败。"
    fi
fi
