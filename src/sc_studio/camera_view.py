'''
sc_studio.camera_view

Author: Ming Tsang
Copyright (c) 2014-2015 HKUST SmartCar Team
Refer to LICENSE for details
'''

import binascii
import logging
from PIL import Image, ImageTk
import time
import tkinter
from tkinter import Tk, Canvas
from sc_studio.view import View

class CameraView(View):
	def __init__(self, params):
		super(CameraView, self).__init__(params)

		self._multiplier = int(params["multiplier"]) if "multiplier" in params \
				else 1
		self._multiplier = max(self._multiplier, 1)

		self._tk = Tk()
		self._canvas = Canvas(self._tk, width = 80 * self._multiplier,
				height = 60 * self._multiplier)

		self._tk.title("Camera view")
		self._tk.resizable(width = False, height = False)
		self._canvas.pack(side = tkinter.LEFT, fill = tkinter.BOTH,
				expand = True)

		self._tk.protocol("WM_DELETE_WINDOW", self.on_press_close)

		self._file = open("camera_" + str(int(time.time() * 1000)), "w")

	def run(self):
		super(CameraView, self).run()
		self._tk.mainloop()

	def on_new_input(self):
		try:
			hex_str = self.get_input()
			text = self._get_display_list(hex_str)
			bmp = self._get_bitmap(hex_str)
		except Exception as e:
			logging.debug(str(e))
			return
		if bmp is None:
			return

		self._canvas.create_image(0, 0, image = bmp, anchor = tkinter.NW)
		self._image = bmp

		self._file.write(time.strftime("[%x %X]\n"))
		for line in text:
			string = line.decode("UTF-8")
			self._file.write(string)
			self._file.write('\n')

	def on_dismiss(self):
		self._tk.after_idle(self.on_press_close)

	def on_press_close(self):
		self._tk.destroy()
		self.join_io_thread()

	def _get_bitmap(self, hex_str):
		try:
			hex_data = binascii.unhexlify(hex_str)
		except TypeError as e:
			logging.debug(str(e))
			return

		img = Image.frombytes(mode = '1', size = (80, 60), data = hex_data)
		img = img.resize((80 * self._multiplier, 60 * self._multiplier))
		bmp = ImageTk.BitmapImage(image = img, foreground = "black",
				background = "white")
		return bmp

	def _get_display_list(self, hex_str):
		try:
			hex_data = binascii.unhexlify(hex_str)
		except TypeError as e:
			logging.debug(str(e))
			return None

		byte_pos = 0
		bit_pos = 0
		display = [bytearray(b' ' * 160) for i in range(60)]
		for i in range(60):
			for j in range(80):
				if hex_data[byte_pos] & (0x80 >> bit_pos):
					display[i][j * 2] = ord('#');
					display[i][j * 2 + 1] = ord('#');
				bit_pos += 1
				if bit_pos >= 8:
					bit_pos = 0
					byte_pos += 1
		return display
