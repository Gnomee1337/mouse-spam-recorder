import random
import string
from time import sleep
from pyautogui import typewrite, press, mouseInfo, click, moveTo


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return str(result_str)
    # print("Random string of length", length, "is:", result_str)


sticker_button = [1854, 1013]
stickers_coords = [(1673, 563), (1740, 562), (1740, 562), (1874, 565), (1737, 631), (1807, 630), (1873, 635),
                   (1674, 701), (1741, 702), (1808, 698), (1877, 700), (1674, 792), (1742, 791), (1808, 786), (1874, 792)]
if __name__ == "__main__":
    # x3,y3 = sticker_button
    # #print(x3,y3)
    # click()
    # sleep(2)

    while (True):
        for i in range(len(stickers_coords)):
            moveTo(sticker_button[0], sticker_button[1])
            x3 = stickers_coords[i][0]
            y3 = stickers_coords[i][1]
            moveTo(x3, y3)
            click()
            sleep(1)
            print(x3, y3)

    # x3 = stickers_coords[0][0]
    # y3 = stickers_coords[0][1]
    # spam_massage = 'asd'
    # count = 10
    # while(True):
    #     typewrite(get_random_string(random.randint(0,9)))
    #     #count =- 1
    #     press("enter")
