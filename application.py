from tkinter import *
from tkinter import filedialog
import PIL.Image
import PIL.ImageTk
import numpy as np
from utils import *
import cv2
import math

color = 0


class Settings(Toplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		self.title("Настройки")
		self.geometry('200x185')
		self.lbl_s = Label(self, text="S = ")
		self.lbl_s.grid(column=0, row=0, sticky="w")
		self.txt_s = Entry(self, width=5)
		self.txt_s.grid(column=1, row=0, sticky="w")
		self.txt_s.insert(0, "10")
		self.lbl_x = Label(self, text="X = ")
		self.lbl_x.grid(column=0, row=1, sticky="w")
		self.txt_x = Entry(self, width=5)
		self.txt_x.grid(column=1, row=1, sticky="w")
		self.txt_x.insert(0, "6")
		self.lbl_y = Label(self, text="Y = ")
		self.lbl_y.grid(column=0, row=2, sticky="w")
		self.txt_y = Entry(self, width=5)
		self.txt_y.grid(column=1, row=2, sticky="w")
		self.txt_y.insert(0, "6")
		self.lbl_data = Label(self, text="Data: ")
		self.lbl_data.grid(column=0, row=3, sticky="w")
		self.txt_data = Entry(self, width=15)
		self.txt_data.grid(column=1, row=3, sticky="w")
		self.txt_data.insert(0, "1111000011110100")
		self.clr = IntVar(value=color)
		self.r1 = Radiobutton(self, text='Синий', variable=self.clr, value=0)
		self.r2 = Radiobutton(self, text='Красный', variable=self.clr, value=2)
		self.r3 = Radiobutton(self, text='Фиолетовый', variable=self.clr, value=1)
		self.r1.grid(column=0, row=4, sticky="w")
		self.r2.grid(column=0, row=5, sticky="w")
		self.r3.grid(column=0, row=6, sticky="w")
		self.btn_ready = Button(self, text="Готово", command=self.set_new_params)
		self.btn_ready.grid(column=0, row=7, sticky="w")

	def set_new_params(self):
		self.parent.S = float(int(self.txt_s.get()))
		self.parent.X = int(self.txt_x.get())
		self.parent.Y = int(self.txt_y.get())
		self.parent.data = np.array(list(map(int, list(self.txt_data.get()))))
		global color
		color = self.clr.get()
		self.destroy()


class App:
	def __init__(self):
		self.file = ''
		self.S = 10.
		self.X = 6
		self.Y = 6
		self.data = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0])

		self.window = Tk()
		self.window.title("Встраивание ЦВЗ в видео")
		self.window.geometry('2400x1600')
		self.window.grid_columnconfigure(4, weight=1)
		self.window.grid_columnconfigure(5, weight=1)
		self.window.grid_columnconfigure(6, weight=1)

		self.mainMenu = Menu(self.window)
		self.window.config(menu=self.mainMenu)

		self.fileMenu = Menu(self.window, tearoff=0)
		self.fileMenu.add_command(label='Открыть...', command=self.selectFile)
		self.fileMenu.add_command(label="Настройки", command=self.set_settings)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label='Выход', command=self.window.quit)

		self.mainMenu.add_cascade(label='Файл', menu=self.fileMenu)
		self.mainMenu.add_command(label='Справка')

		self.lbl = Label(self.window, text="Выберите файл", font=("Arial Bold", 14))
		self.lbl.grid(column=0, row=0, columnspan=2)

		self.btn_open_file = Button(self.window, text="Выбрать Файл!", command=self.selectFile, width=20)
		self.btn_open_file.grid(column=0, row=1, columnspan=2)

		self.lbl_file_name_2 = Label(self.window, text="")
		self.lbl_file_name_2.grid(column=0, row=2, sticky="we")

		self.btn = Button(self.window, text="Встроить!", command=self.start, width=40, pady = 10, bg = '#ffffff')
		self.btn.grid(column=0, row=5, columnspan=2, sticky="s")

		self.lbl_ans = Label(self.window, text="")
		self.lbl_ans.grid(column=1, row=2, sticky="we")

		img = PIL.Image.open("play.png").resize((150, 150))
		self.image_old = PIL.ImageTk.PhotoImage(image=img)
		self.image_new = PIL.ImageTk.PhotoImage(image=img)

		self.canvas_old_video = Canvas(self.window, width=800, height=400)
		self.canvas_old_video.grid(column=0, row=3, sticky="e")
		self.canvas_old_video.create_image(200, 200, image=self.image_old, anchor=W)

		self.canvas_new_video = Canvas(self.window, width=800, height=400)
		self.canvas_new_video.grid(column=1, row=3, sticky="w")
		self.canvas_new_video.create_image(200, 200, image=self.image_new)

		self.cut_size = []

		self.window.mainloop()

	def update_cut_size(self, width, height):
		if width > height:
			self.cut_size = (800, int(height * 800 / width))
		else:
			self.cut_size = (int(width * 800 / height), 800)

	def selectFile(self):
		self.file = filedialog.askopenfilename(filetypes=(("avi files", "*.avi"), ("all files", "*.*")))
		self.lbl_file_name_2.configure(text=self.file)

	def set_settings(self):
		settingsWindow = Settings(self.window)
		settingsWindow.mainloop()

	def start(self):
		if self.file == '':
			pass
		parts = self.file.split('.')
		final_name = parts[0] + "_mod." + parts[1]
		codedData = conv_code(self.data)
		cap = cv2.VideoCapture(self.file)
		frames = list()
		if cap.isOpened():
			while True:
				ret, frame = cap.read()

				if ret:
					frames.append(frame)
				else:
					break
			cap.release()
		else:
			print("video isn't opened")
			exit(1)
		frames = np.array(frames)
		codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
		out = cv2.VideoWriter(final_name, codec, 24.0, (frames.shape[2], frames.shape[1]))
		vidW, vidH = frames.shape[2], frames.shape[1]
		blW, blH = math.floor(vidW / self.X), math.floor(vidH / self.Y)
		spat = np.zeros((self.Y, self.X))
		step = 0
		self.update_cut_size(frames.shape[2], frames.shape[1])
		for j in range(0, self.Y):
			for i in range(0, self.X):
				if (i == 0 and j == 0) or (i == self.X - 1 and j == 0) or (i == 0 and j == self.Y - 1) or (
						i == self.X - 1 and j == self.Y - 1):
					spat[j, i] = 1
				else:
					spat[j, i] = codedData[step] * 2 - 1
					step += 1
		for frame in range(1, len(frames)):
			if frame % 4 == 0:
				self.image_old = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frames[frame, :, :, ::-1]).resize(self.cut_size))
			cFrame = np.array(frames[frame - 1], dtype='int32')
			dFrame = cFrame - frames[frame]
			for j in range(self.Y):
				for i in range(self.X):
					d = dFrame[(blH * j):(blH * (j + 1) - 1), (blW * i):(blW * (i + 1) - 1), :].mean()
					# calculating T
					if spat[j, i] == 1:
						if d < self.S:
							T = math_round((self.S - d) / 2.)
						else:
							T = 0
					else:
						if d > -self.S:
							T = math_round((self.S + d) / 2.)
						else:
							T = 0
					# Frame modification
					if color != 1:
						if math_round(frame / 2.) % 2 == 0:
							cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), color] += int(T * spat[j, i])
						else:
							cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), color] -= int(T * spat[j, i])
					else:
						if math_round(frame / 2.) % 2 == 0:
							cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), 0] += int(T * spat[j, i] / 2)
							cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), 2] += int(T * spat[j, i] / 2)
						else:
							cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), 0] -= int(T * spat[j, i] / 2)
							cFrame[(blH * j): (blH * (j + 1) - 1), (blW * i): (blW * (i + 1) - 1), 2] -= int(T * spat[j, i] / 2)
			cFrame = np.where(cFrame > 255, 255, cFrame)
			cFrame = np.where(cFrame < 0, 0, cFrame)
			tmp_frame = np.array(cFrame, dtype='uint8')
			if frame % 4 == 0:
				self.image_new = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(tmp_frame[:, :, ::-1]).resize(self.cut_size))
				self.canvas_old_video.create_image(200, 200, image=self.image_old, anchor=W)
				self.canvas_new_video.create_image(200, 200, image=self.image_new)
				self.window.update()
			out.write(tmp_frame)
		out.release()

		self.lbl_ans.configure(text="Готовый файл: " + final_name)


app = App()
