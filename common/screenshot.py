# -*- coding: utf-8 -*-
# 获取 Android 屏幕截图

import subprocess
import os
import sys
from PIL import Image, ImageFile

# SCREENSHOT_WAY 是截图方法，经过 check_screenshot 后，会自动递减，不需手动修改
SCREENSHOT_WAY = 3


def pull_screenshot():
    """
    获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
    可根据效率及适用性由高到低排序
    """
    global SCREENSHOT_WAY
    if 1 <= SCREENSHOT_WAY <= 3:
        process = subprocess.Popen(
            'adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        binary_screenshot = process.stdout.read()
        if SCREENSHOT_WAY == 2:
            binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
        elif SCREENSHOT_WAY == 1:
            binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
        '''
        f = open('autojump.png', 'wb')
        f.write(binary_screenshot)
        f.close()
        '''
        f = ImageFile.Parser()
        f.feed(binary_screenshot)
        return f.close()
    elif SCREENSHOT_WAY == 0:
        os.system('adb shell screencap -p /sdcard/autojump.png')
        os.system('adb pull /sdcard/autojump.png .')
        return Image.open("autojump.png")


def check_screenshot():
    """
    检查获取截图的方式
    """
    global SCREENSHOT_WAY
    if os.path.isfile('autojump.png'):
        try:
            os.remove('autojump.png')
        except Exception:
            pass
    if SCREENSHOT_WAY < 0:
        print('Error:获取屏幕失败,请检查手机adb是否已经打开并授权')
        sys.exit()
    try:
        im = pull_screenshot()
        print('INFO:采用方式 {} 获取截图'.format(SCREENSHOT_WAY))
    except IOError:
        SCREENSHOT_WAY -= 1
        check_screenshot()