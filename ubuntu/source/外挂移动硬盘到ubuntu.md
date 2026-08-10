# 查看新接入的块设备（对比插拔前后输出）
lsblk -f

# 或通过内核日志确认设备名
dmesg | tail -20 | grep -iE "sd|usb.*storage"