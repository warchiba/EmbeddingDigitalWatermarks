from tkinter import *
from tkinter import filedialog
import numpy as np
from utils import *
import cv2
import math


file = ''
S = 10.
X = 6
Y = 6
data = np.array(list(map(int, list("1111000011110100"))))

# 1111000011110100


def start():
    if file == '':
        pass
    parts = file.split('.')
    final_name = parts[0] + "_mod." + parts[1]

    codedData = conv_code(data)

    cap = cv2.VideoCapture(file)

    frames = list()

    if cap.isOpened():
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if ret:
                frames.append(frame)
            else:
                break
        # When everything done, release the capture
        cap.release()
    else:
        print("video isn't opened")

    frames = np.array(frames)

    codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    out = cv2.VideoWriter(final_name, codec, 24.0, (frames.shape[2], frames.shape[1]))
    vidW, vidH = frames.shape[2], frames.shape[1]
    blW, blH = math.floor(vidW / X), math.floor(vidH / Y)
    spat = np.zeros((Y, X))
    step = 0
    for j in range(0, Y):
        for i in range(0, X):
            if (i == 0 and j == 0) or (i == X - 1 and j == 0) or (i == 0 and j == Y - 1) or (i == X - 1 and j == Y - 1):
                spat[j, i] = 1
            else:
                spat[j, i] = codedData[step] * 2 - 1
                step += 1
    for frame in range(1, len(frames)):
        cFrame = np.array(frames[frame - 1], dtype='int32')
        dFrame = cFrame - frames[frame]
        for j in range(Y):
            for i in range(X):
                d = dFrame[(blH * j):(blH * (j + 1) - 1), (blW * i):(blW * (i + 1) - 1), :].mean()
                # calculating T
                if spat[j, i] == 1:
                    if d < S:
                        T = math_round((S - d) / 2.)
                    else:
                        T = 0
                else:
                    if d > -S:
                        T = math_round((S + d) / 2.)
                    else:
                        T = 0
                # Frame modification
                if math_round(frame / 2.) % 2 == 0:
                    cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), 0] += int(T * spat[j, i])
                else:
                    cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), 0] -= int(T * spat[j, i])
        cFrame = np.where(cFrame > 255, 255, cFrame)
        cFrame = np.where(cFrame < 0, 0, cFrame)
        tmp_frame = np.array(cFrame, dtype='uint8')
        out.write(tmp_frame)
    out.release()

    lbl_ans.configure(text="Готовый файл: " + final_name)


def set_settings():
    settingsWindow = Toplevel(window)
    settingsWindow.title("Настройки")
    settingsWindow.geometry('200x125')
    lbl_s = Label(settingsWindow, text="S = ")
    lbl_s.grid(column=0, row=0, sticky="w")
    txt_s = Entry(settingsWindow, width=5)
    txt_s.grid(column=1, row=0, sticky="w")
    txt_s.insert(0, "10")
    lbl_x = Label(settingsWindow, text="X = ")
    lbl_x.grid(column=0, row=1, sticky="w")
    txt_x = Entry(settingsWindow, width=5)
    txt_x.grid(column=1, row=1, sticky="w")
    txt_x.insert(0, "6")
    lbl_y = Label(settingsWindow, text="Y = ")
    lbl_y.grid(column=0, row=2, sticky="w")
    txt_y = Entry(settingsWindow, width=5)
    txt_y.grid(column=1, row=2, sticky="w")
    txt_y.insert(0, "6")
    lbl_data = Label(settingsWindow, text="Data: ")
    lbl_data.grid(column=0, row=3, sticky="w")
    txt_data = Entry(settingsWindow, width=15)
    txt_data.grid(column=1, row=3, sticky="w")
    txt_data.insert(0, "1111000011110100")

    def set_new_params():
        global S, X, Y, data
        S = float(int(txt_s.get()))
        X = int(txt_x.get())
        Y = int(txt_y.get())
        data = np.array(list(map(int, list(txt_data.get()))))
        settingsWindow.quit()

    btn_ready = Button(settingsWindow, text="Готово", command=set_new_params)
    btn_ready.grid(column=0, row=4, sticky="w")


def selectFile():
    global file
    file = filedialog.askopenfilename()
    lbl_file_name_2.configure(text=file)


window = Tk()
window.title("Встраивание ЦВЗ в видео")
window.geometry('500x200')

# Меню

mainMenu = Menu(window)
window.config(menu=mainMenu)

fileMenu = Menu(window, tearoff=0)
fileMenu.add_command(label='Открыть...', command=selectFile)
fileMenu.add_command(label="Настройки", command=set_settings)
fileMenu.add_separator()
fileMenu.add_command(label='Выход', command=window.quit)

mainMenu.add_cascade(label='Файл', menu=fileMenu)
mainMenu.add_command(label='Справка')

# Основные элементы

lbl = Label(window, text="Выберите файл", font=("Arial Bold", 14))
lbl.grid(column=0, row=0, sticky="w")

btn_open_file = Button(window, text="Выбрать Файл!", command=selectFile)
btn_open_file.grid(column=0, row=1, sticky="w")

lbl_file_name_1 = Label(window, text="Выбранный файл: ")
lbl_file_name_1.grid(column=0, row=2, sticky="w")

lbl_file_name_2 = Label(window, text="")
lbl_file_name_2.grid(column=1, row=2)

btn = Button(window, text="Встроить!", command=start)
btn.grid(column=0, row=8, sticky="w")

lbl_ans = Label(window, text="")
lbl_ans.grid(column=1, row=8, sticky="w")

window.mainloop()
