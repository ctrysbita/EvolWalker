import os
import random
import subprocess
import sys
import time
from enum import Enum
from PIL import Image

from common import screenshot
from button_models import s1080x1920 as button_points

debug_mode = False
Status = Enum('Status', ('START', 'CAN_TALK', 'TALKING', "GOING"))

global marked_point
marked_point = [0, 0]


def drift():
    return random.uniform(0, 10)


def pixel_match(im, target_point, target_rgb, loss, debug=False):
    pixel = im.getpixel((target_point[0], target_point[1]))
    if (debug):
        print("Debug:pixel_rgb:", pixel[0], pixel[1], pixel[2])
        print("Debug:target_rgb:", target_rgb[0], target_rgb[1], target_rgb[2])
    return True if (abs(pixel[0] - target_rgb[0]) <= loss
                    and abs(pixel[1] - target_rgb[1]) <= loss
                    and abs(pixel[2] - target_rgb[2]) <= loss) else False


def array_match(im, target_points, target_rgb, loss):
    global marked_point
    for point in target_points:
        if pixel_match(im, point, target_rgb, loss):
            marked_point = point
            return True
    return False


def check_status(im):
    if array_match(im, button_points.LOCATIONS, [243, 113, 147], 30):
        return Status["CAN_TALK"]
    elif pixel_match(
            im, button_points.AUTO, [240, 125, 145], 50, debug=debug_mode):
        return Status["TALKING"]
    elif pixel_match(
            im, button_points.GO, [126, 186, 232], 30, debug=debug_mode):
        return Status["GOING"]
    elif pixel_match(
            im, button_points.START, [250, 140, 155], 30, debug=debug_mode):
        return Status["START"]


def action(status):
    if status is None:
        return
    elif status.value == Status["CAN_TALK"].value:
        do_talk()
    elif status.value == Status["TALKING"].value:
        do_auto_talk()
    elif status.value == Status["GOING"].value:
        do_going()
    elif status.value == Status["START"].value:
        do_start()


def do_talk():
    global marked_point
    print("INFO:开始对话")
    tap(marked_point)
    time.sleep(1)


def do_auto_talk():
    tap(button_points.AUTO)
    print("INFO:开启自动对话，等待结束")
    time.sleep(10)
    while True:
        temp_im = screenshot.pull_screenshot()
        if not (check_status(temp_im) == Status["TALKING"]):
            break
        else:
            temp_im.close()
            time.sleep(0.5)


def do_going():
    print("INFO:开始前往")
    tap(button_points.GO)
    time.sleep(1)


def do_start():
    print("INFO:开始出发")
    tap(button_points.START)
    time.sleep(1)


def tap(point):
    point[0] = point[0] + drift()
    point[1] = point[1] + drift()
    print("INFO:模拟点击({},{})".format(point[0], point[1]))
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    cmd = 'adb shell input tap {x} {y}'.format(x=point[0], y=point[1])
    subprocess.Popen(cmd, startupinfo=si)
    time.sleep(0.1)


def main():
    screenshot.check_screenshot()
    while True:
        print("INFO:正在截取手机屏幕")
        im = screenshot.pull_screenshot()
        if debug_mode:
            print("Debug:image_size:", im.size)
        print("INFO:正在检查状态")
        status = check_status(im)
        print("INFO:当前状态:", status)
        action(status)
        time.sleep(random.uniform(1, 2))
        im.close()


if __name__ == "__main__":
    main()
