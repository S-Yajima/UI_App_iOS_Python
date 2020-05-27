import ui
import threading
from math import cos
from math import sin
from math import radians
from figure import *
from PIL import Image


# 数字。
# 数字を構成するパーツとして複数の四角を保持する。
class MyNumeral(MyFigure):
	image_width = 10
	image_height = 50
	
	def __init__(self):
		super().__init__()
		self.squares = []
		self.is_enable_shadow = True
		self.shadow_color = 'black'
		self.texture_pixels = []
	
	
	def set_texture_image(self, image):
		self.texture_pixels.clear()
		
		# texture_pixels[row][colmn]
		for y in range(0, self.image_height):
			row_pixels = []
			for x in range(0, self.image_width):
				r, g, b = image.getpixel((x, y))
				row_pixels.append([r, g, b])
			self.texture_pixels.append(row_pixels)
				
		self.texture_image = image
	
	
	def square_count(self):
		return (len(self.squares))


	def add_square(self, square):
		self.squares.append(square)


	def corner_A(self, index):
		square = self.squares[index]
		x, y, z = self.queue(
			square.A_x, square.A_y, square.A_z)
		return (x, y, z)


	def corner_B(self, index):
		square = self.squares[index]
		x, y, z = self.queue(
			square.B_x, square.B_y, square.B_z)
		return (x, y, z)


	def corner_C(self, index):
		square = self.squares[index]
		x, y, z = self.queue(
			square.C_x, square.C_y, square.C_z)
		return (x, y, z)


	def corner_D(self, index):
		square = self.squares[index]
		x, y, z = self.queue(
			square.D_x, square.D_y, square.D_z)
		return (x, y, z)



# 背景と床を描画する
class BaseView(ui.View):
	triangles = []
	numbers = []
	round_angle = 0
	
	# スクリーン深度
	screen_depth = 350
	
	def add_number(self, number):
		self.numbers.append(number)
	
	def add_triangle(self, triangle):
		self.triangles.append(triangle)
	
	def set_needle_angle(self, angle):
		for triangle in self.triangles:
			triangle.set_rotate_angle(angle)
	
	
	def set_round_angle(self, angle):
		self.round_angle = angle
	
	
	# 三次元空間から二次元スクリーンへの投影を反映する
	# 三次元空間の起点座標(0,0,0)と
	# 二次元の起点座標(0,0)との差分を反映する
	def projection(self, x, y, z):
		# 視点からの距離
		depth = self.screen_depth * -1
		
		# 視点の中心座標
		center_x = self.width / 2
		center_y = self.height / 2
		r_x, r_y = x, y
		if (z + depth) != 0:
			r_x = ((depth / (z + depth)) * x) + center_x
			r_y = ((depth / (z + depth)) * y) + center_y
			
		return (r_x, r_y)
	
	
	# テクスチャを描画する
	def draw_texture_image(self, A_pos, AB_V3, AD_V3, pixels):
		width = 10
		height = 50
		
		# UV補間の考え方で画像を描画する方法
		for y in range(0, height):
			for x in range(0, width):
				u = x / width
				v = y / height
				
				# a + u(d - a)
				r_AD_V3 = [u * AD_V3[0],
									u * AD_V3[1],
									u * AD_V3[2]]
				# a + v(b - a)
				r_AB_V3 = [v * AB_V3[0],
									v * AB_V3[1],
									v * AB_V3[2]]
				# 
				r_V3 = [
					A_pos[0] + r_AB_V3[0] + r_AD_V3[0],
					A_pos[1] + r_AB_V3[1] + r_AD_V3[1],
					A_pos[2] + r_AB_V3[2] + r_AD_V3[2]]
				
				# 投影
				draw_x, draw_y = self.projection(
					r_V3[0], r_V3[1], r_V3[2])
				
				# 画像のピクセル数値を取得
				r = pixels[y][x][0]
				g = pixels[y][x][1]
				b = pixels[y][x][2]
				
				ui.set_color((r/255, g/255, b/255, 1.0))
				ui.fill_rect(draw_x, draw_y, 1, 1)
				
	
	# 描画
	def draw(self):
		
		# 数字を描画する
		for number in self.numbers:
			for square_index in range(0, number.square_count()):
				a_x, a_y, a_z = number.corner_A(square_index)
				b_x, b_y, b_z = number.corner_B(square_index)
				c_x, c_y, c_z = number.corner_C(square_index)
				d_x, d_y, d_z = number.corner_D(square_index)
				
				p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
				p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
				p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
				p_d_x, p_d_y = self.projection(d_x, d_y, d_z)
				
				# 影の描画を行う
				if number.is_enable_shadow is True:
					path_s = ui.Path()
					path_s.move_to(p_a_x + 5, p_a_y + 5)
					path_s.line_to(p_b_x + 5, p_b_y + 5)
					path_s.line_to(p_c_x + 5, p_c_y + 5)
					path_s.line_to(p_d_x + 5, p_d_y + 5)
				
					ui.set_color(number.shadow_color)
					path_s.fill()
				
				# テクスチャの描画
				A_pos = [a_x, a_y, a_z]
				AB_V3 = [b_x - a_x, b_y - a_y, b_z - a_z]
				AD_V3 = [d_x - a_x, d_y - a_y, d_z - a_z]
				
				self.draw_texture_image(A_pos, AB_V3, AD_V3, number.texture_pixels)
				
				
				
		# 円を描画する
		path_r = ui.Path()
		path_r.move_to(350, 100)
		path_r.add_arc(100, 100, 250, 0, radians(self.round_angle))
		ui.set_color('black')
		path_r.stroke()
		
		# 三角
		for triangle in self.triangles:
			a_x, a_y, a_z = triangle.corner_A()
			b_x, b_y, b_z = triangle.corner_B()
			c_x, c_y, c_z = triangle.corner_C()
		
			# 影の描画を行う
			if triangle.is_enable_shadow is True:
				path_t_s = ui.Path()
				path_t_s.move_to(a_x + 5, a_y + 5)
				path_t_s.line_to(b_x + 5, b_y + 5)
				path_t_s.line_to(c_x + 5, c_y + 5)
				
				ui.set_color(triangle.shadow_color)
				path_t_s.fill()
		
			path_t = ui.Path()
			path_t.move_to(a_x, a_y)
			path_t.line_to(b_x, b_y)
			path_t.line_to(c_x, c_y)
		
			ui.set_color(triangle.mycolor())
			path_t.fill()


# 円を描く
def round_schedule(main_view, round_angle):
	if isinstance(main_view, BaseView) is True:
		main_view.set_round_angle(round_angle)
		main_view.set_needs_display()
		
		if round_angle < 360:
			round_angle += 3
		
	if main_view.on_screen is True and round_angle <= 360:
		t = threading.Timer(0.02, round_schedule, args=[main_view, round_angle])
		t.start()


# 数字を縮小
def scale_schedule(main_view, index):
	if isinstance(main_view, BaseView) is True:
		number = main_view.numbers[index]
		scale = number.scale
		
		if scale > 1.1:
			scale -= 0.1
		else:
			scale = 1.0
			index += 1
		
		number.set_scale(scale)
		main_view.set_needs_display()
		
	if main_view.on_screen is True and index < len(main_view.numbers):
		t = threading.Timer(0.02, scale_schedule, args=[main_view, index])
		t.start()
	
	if main_view.on_screen is True and index >= len(main_view.numbers):
		t = threading.Timer(1.0, needle_scale_schedule, args=[main_view, 0])
		t.start()
	
	pass


# 針を縮小
def needle_scale_schedule(main_view, index):
	if isinstance(main_view, BaseView) is True:
		triangle = main_view.triangles[index]
		scale = triangle.scale
		
		if scale > 1.1:
			scale -= 0.1
		else:
			scale = 1.0
			index += 1
		
		triangle.set_scale(scale)
		main_view.set_needs_display()
		
	if main_view.on_screen is True and index < len(main_view.triangles):
		t = threading.Timer(0.02, needle_scale_schedule, args=[main_view, index])
		t.start()
	
	if main_view.on_screen is True and index >= len(main_view.triangles):
		t = threading.Timer(1.0, needle_rotate_schedule, args=[main_view, 0, 0])
		t.start()
		
		t2 = threading.Timer(16.0, number_rotate_schedule, args=[main_view, 0, 0])
		t2.start()
		pass


# 数字を回す
def number_rotate_schedule(main_view, angle, index):
	delay = 0.01
	if isinstance(main_view, BaseView) is True:
		if index < len(main_view.numbers):
			angle += 13
			#angle += 10
			if angle >= 360:
				angle = 0
			
			if index % 3 == 0:
				main_view.numbers[index].set_angle_z(angle)
			elif index % 3 == 1:
				main_view.numbers[index].set_angle_x(angle)
			elif index % 3 == 2:
				main_view.numbers[index].set_angle_y(angle)
			else:
				main_view.numbers[index].set_angle_z(angle)
			
			if angle == 0:
				index += 1
				delay = 0.5
			if index >= len(main_view.numbers):
				index = 0
				delay = 5.0
	
	if main_view.on_screen is True:
		t = threading.Timer(delay, number_rotate_schedule, args=[main_view, angle, index])
		t.start()
		pass


# 針を回す
def needle_rotate_schedule(main_view, l_angle, s_angle):
	if isinstance(main_view, BaseView) is True:
		if len(main_view.triangles) > 0:
			l_triangle = main_view.triangles[1]
			l_triangle.set_angle_z(l_angle)
			s_triangle = main_view.triangles[0]
			s_triangle.set_angle_z(s_angle)
			
			main_view.set_needs_display()
			
			l_angle = (l_angle + 1) % 360
			s_angle = (s_angle + (1.0 / 12)) % 360
			
	if main_view.on_screen is True:
		t = threading.Timer(0.012, needle_rotate_schedule, args=[main_view, l_angle, s_angle])
		t.start()
	pass


# 数字のパーツを落とす
def parts_parts_schedule(squares, fall_speed):
	for i in range(0, len(squares)):
		square = squares[i]
		if isinstance(square, Square) is True:
			square.A_y += fall_speed
			square.B_y += fall_speed
			square.C_y += fall_speed
			square.D_y += fall_speed
			fall_speed += 0.4

	if main_view.on_screen is True and fall_speed < 60.0:
		t = threading.Timer(0.02, parts_parts_schedule, args=[squares, fall_speed])
		t.start()
	pass
	

if __name__ == '__main__':
	# メイン画面の作成
	main_view = BaseView(frame=(0, 0, 375, 667))
	main_view.name = '時計のような何か'
	main_view.background_color = 'lightblue'
	
	# 短針
	triangle_1 = Triangle(0,140,0, 10,0,0, 20,140,0)
	triangle_1.translate(95, -28, 0)
	triangle_1.set_center(-10, -130, 0)
	triangle_1.set_scale(1)
	main_view.add_triangle(triangle_1)
	
	# 長針
	triangle_2 = Triangle(0,240,0, 10,0,0, 20,240,0)
	triangle_2.translate(95, -123, 0)
	triangle_2.set_center(-10, -230, 0)
	triangle_2.set_scale(1)
	main_view.add_triangle(triangle_2)
	
	
	image_red = Image.open("赤_白_チェス目_細.png")
	image_green = Image.open("緑_白_チェス目_細.png")
	image_blue = Image.open("青_白_チェス目_細.png")
	
	# Ⅱ
	number_2 = MyNumeral()
	number_2.translate(105, -285, 0)
	square_2_0 = Square(0,0,0, 0,50,0, 10,50,0, 10,0,0)
	number_2.add_square(square_2_0)
	square_2_1 = Square(15,0,0, 15,50,0, 25,50,0, 25,0,0)
	number_2.add_square(square_2_1)
	number_2.set_center(-12.5, -25, 0)
	number_2.set_scale(1)
	number_2.set_texture_image(image_red)
	main_view.add_number(number_2)
	
	# Ⅲ
	number_3 = MyNumeral()
	number_3.translate(110, -200, 0)
	square_3_0 = Square(0,0,0, 0,50,0, 10,50,0, 10,0,0)
	number_3.add_square(square_3_0)
	square_3_1 = Square(15,0,0, 15,50,0, 25,50,0, 25,0,0)
	number_3.add_square(square_3_1)
	square_3_2 = Square(30,0,0, 30,50,0, 40,50,0, 40,0,0)
	number_3.add_square(square_3_2)
	number_3.set_center(-20, -25, 0)
	number_3.set_scale(1)
	number_3.set_texture_image(image_green)
	main_view.add_number(number_3)
	
	# Ⅳ
	number_4 = MyNumeral()
	number_4.translate(75, -105, 0)
	square_4_0 = Square(0,0,0, 0,50,0, 10,50,0, 10,0,0)
	number_4.add_square(square_4_0)
	number_4.add_square(Square(15,0,0, 25,50,0, 35,50,0, 25,0,0))
	number_4.add_square(Square(45,0,0, 35,50,0, 45,50,0, 55,0,0))
	number_4.set_center(-25, -25, 0)
	number_4.set_scale(1)
	number_4.set_texture_image(image_blue)
	main_view.add_number(number_4)
	
	# Ⅴ
	number_5 = MyNumeral()
	number_5.translate(15, -30, 0)
	square_5_0 = Square(0,0,0, 10,50,0, 20,50,0, 10,0,0)
	number_5.add_square(square_5_0)
	square_5_1 = Square(30,0,0, 20,50,0, 30,50,0, 40,0,0)
	number_5.add_square(square_5_1)
	number_5.set_center(-20, -25, 0)
	number_5.set_scale(1)
	number_5.set_texture_image(image_red)
	main_view.add_number(number_5)
	
	# Ⅵ
	number_6 = MyNumeral()
	number_6.translate(-100, 0, 0)
	square_6_0 = Square(0,0,0, 10,50,0, 20,50,0, 10,0,0)
	number_6.add_square(square_6_0)
	square_6_1 = Square(30,0,0, 20,50,0, 30,50,0, 40,0,0)
	number_6.add_square(square_6_1)
	square_6_2 = Square(45,0,0, 45,50,0, 55,50,0, 55,0,0)
	number_6.add_square(square_6_2)
	number_6.set_center(-22.5, -25, 0)
	number_6.set_scale(1)
	number_6.set_texture_image(image_green)
	main_view.add_number(number_6)
	
	#Ⅶ
	number_7 = MyNumeral()
	number_7.translate(-235, -30, 0)
	square_7_0 = Square(0,0,0, 10,50,0, 20,50,0, 10,0,0)
	number_7.add_square(square_7_0)
	square_7_1 = Square(30,0,0, 20,50,0, 30,50,0, 40,0,0)
	number_7.add_square(square_7_1)
	square_7_2 = Square(45,0,0, 45,50,0, 55,50,0, 55,0,0)
	number_7.add_square(square_7_2)
	square_7_3 = Square(60,0,0, 60,50,0, 70,50,0, 70,0,0)
	number_7.add_square(square_7_3)
	number_7.set_center(-35, -25, 0)
	number_7.set_scale(1)
	number_7.set_texture_image(image_blue)
	main_view.add_number(number_7)
	
	image_red.close()
	image_blue.close()
	image_green.close()
	
	main_view.present()
	
	t1 = threading.Timer(0.02, round_schedule, args=[main_view, 0])
	t1.start()
	
	t2 = threading.Timer(6.0, scale_schedule, args=[main_view, 0])
	t2.start()
	'''
	t3 = threading.Timer(60.0, parts_parts_schedule, args=[[square_4_0], 0])
	t3.start()
	
	t4 = threading.Timer(90.0, parts_parts_schedule, args=[[square_6_1], 0])
	t4.start()
	
	t5 = threading.Timer(90.5, parts_parts_schedule, args=[[square_6_2], 0])
	t5.start()
	'''
	squares = [square_2_0, square_2_1, 
						 square_3_0, square_3_1, square_3_2,
						 square_5_0, square_5_1,
						 square_7_0, square_7_1, square_7_2, square_7_3,]
	t6 = threading.Timer(105.0, parts_parts_schedule, args=[squares, 0])
	t6.start()
	
