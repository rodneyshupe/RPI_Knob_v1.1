import os


def play_audio(filename):
    os.system('mpg321 '+filename+' &')
