from multiprocessing import Process, Manager
from datetime import datetime
from config import TRASH_DAYS, DAYS
import time
import random
import os

from playsound import playsound

# Check Trash Day Logic
def is_trash_day(trash_days: set = TRASH_DAYS) -> bool:
    """
    This checks if tomorrow or today is trash day.
    Takes in a set, trash_days, that represents the days of the week.
    """
    day = datetime.now().weekday()

    if day in trash_days:
        """
        Trash gets picked up early morning. If we miss it, its technically not trash day any more.
        """
        if datetime.now().hour > 7:
            return False

        print(f"Today is {DAYS[day]}, which is trash day!")
        return True
    
    days_before = {day - 1 if day - 1 >= 0 else 6 for day in trash_days}
    if day in days_before:
        print(f"Today is {DAYS[day]} which means tomorrow is trash day!")
        return True

    return False

def remind(data, lock):
    """
    Does some action to remind someone to take out the trash.
    """
    while True:
        if is_trash_day({0, 4}):
            lock.acquire()

            if data["is_taken_out"]:
                print("Great job!")
                play_audio("praise")
            else:
                print("TAKE THE TRASH OUT!")
                play_audio("reminders")

            lock.release()

        time.sleep(5)

def play_audio(directory: str):
    """
    Play a random audio clip from directory
    """
    try:
        file_name = random.choice(os.listdir(f"./{directory}/"))
        path = f"{os.getcwd()}\\{directory}\\{file_name}"
        playsound(path)
    except Exception as e:
        print(e)
        pass

# Manage Trash State Logic
def check_trash_state(data: dict, lock):
    while True:
        lock.acquire()
        now = datetime.now()
        lock.release()

        time.sleep(3)

if __name__ == "__main__":
    """
    TODO: Run trash day check on a schedule. (Is this really needed?)

    Notes:
    A smart thing to do is schedule the checks since we already know what days we need to check.
    However, it's probably fine to just keep it like this for now.

    What NEEDS to be done is a way to reset the state of the trash. After we've surpassed trash day, we need to reset
    the "is_taken_out" to False.

    We can just keep trash state set as TRUE until 24 hrs has elapsed from the "last_taken_out" time. 
    Unsophisticated, but who cares? Its my project.
    """

    with Manager() as manager:
        lock = manager.Lock()
        data = manager.dict()

        data["is_taken_out"] = False
        data["last_taken_out"] = datetime.now()

        process_check_trash_day = Process(target=remind, args=(data, lock))
        process_trash_state = Process(target=check_trash_state, args=(data, lock))

        process_check_trash_day.start()
        process_trash_state.start()

        while True:
            if input():
                lock.acquire()
                data["is_taken_out"] = True
                data["last_taken_out"] = datetime.now()
                lock.release()

                time.sleep(1)

    