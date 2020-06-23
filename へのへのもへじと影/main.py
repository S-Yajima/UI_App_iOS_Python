import ui
import threading
import copy
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from figure import *
from glyph import *
from character import *


# 床。タイルにする。
class  MyFloor():
	position = []
	
	dot_size = 40
	dot_gap = 3
	
	dot_row = 20
	dot_col = 20
	
	def __init__(self, x=0, y=0, z=0):
		self.position = [x, y, z]
	
	
	# 縦、横のインデックスから四辺の座標を二次元配列で返す
	# row, colmun
	# return [[A_x,A_y,A_x],[B_x,B_y,B_z],
	#					[C_x,C_y,C_x],[D_x,D_y,D_z]]
	def points(self, row, colmun):
		r_points = []
		
		# A 左上
		a_x = self.position[0] + (self.dot_size + self.dot_gap) * colmun
		a_y = self.position[1] 
		a_z = self.position[2] - (self.dot_size + self.dot_gap) * row
		
		# B 左下
		b_x = a_x 
		b_y = a_y
		b_z = a_z + self.dot_size
		# C 右下
		c_x = b_x + self.dot_size
		c_y = b_y 
		c_z = b_z
		# D 右上
		d_x = c_x
		d_y = c_y
		d_z = a_z
		
		r_points.append([a_x, a_y, a_z])
		r_points.append([b_x, b_y, b_z])
		r_points.append([c_x, c_y, c_z])
		r_points.append([d_x, d_y, d_z])
		
		return r_points


# 背景と床を描画する
class BaseView(ui.View):
	
	screen_depth = 400	# 視点から投影面までの距離
	
	# 光源
	light_x = 0
	light_y = -500
	light_z = 100
	
	# 床
	froor = None
	
	# 文字
	characters = []
	
	# camera vector
	camera_x = 0		# カメラの位置座標
	camera_y = 0
	camera_z = 0
	lookat_x = 0		# カメラの注視点
	lookat_y = 0
	lookat_z = 0
	CXV = []				# カメラ座標のXYZ軸ベクトル
	CYV = []
	CZV = []
	CPX = 0					# カメラ座標とカメラX軸との内積
	CPY = 0
	CPZ = 0
	# camera vector

	def add_character(self, character):
		self.characters.append(character)
		
		
	# glyph座標からフォントのアウトライン描画を行う
	# point   : 座標 x, y, z
	# control : 制御点 x, y, z
	def draw_glyph(self, point, controls, path):
		p_x, p_y = self.projection(point[0], point[1], point[2])
		
		if point[3] == TYPE.LINE:
			path.line_to(p_x, p_y)
		elif point[3] == TYPE.CONTROL:
			controls.append(
								[p_x, p_y, point[2]])
		elif point[3] == TYPE.CURVE:
			if len(controls) == 2:
				path.add_curve(p_x, p_y, 
					controls[0][0], controls[0][1], 
					controls[1][0], controls[1][1])
			elif len(controls) == 1:
				path.add_quad_curve(p_x, p_y, 
					controls[0][0], controls[0][1])
			controls.clear()


	# 制御点とグリフ座標点を描画する
	# 投影した座標を描画する
	# points : 
	#	座標[[x,y,z,type,flag],[x,y,z,type,flag],...
	# typeがlineまたはcurveの場合は黒塗りの四角
	# typeがcontrolの場合は白抜きの四角
	def draw_glyph_points(self, points):
		point_size = 5
		for point in points:
			p_x, p_y = self.projection(point[0], point[1], point[2])
			
			if point[4] is True:
				p_path = ui.Path.rect(
					p_x, p_y, point_size, point_size)
				ui.set_color('black')
				if point[3] == TYPE.CONTROL:
					p_path.stroke()
				else:
					p_path.fill()


	# 床を設定する
	def set_floor(self, floor):
		if isinstance(floor, MyFloor) is True:
			self.floor = floor
	
	
	# カメラの位置座標を設定する
	def set_camera_position(self, x, y, z):
		self.camera_x = x
		self.camera_y = y
		self.camera_z = z


	# カメラの注視点を設定する
	def set_lookat_position(self, x, y, z):
		self.lookat_x = x
		self.lookat_y = y
		self.lookat_z = z
	
	
	# ビュー座標XYZ軸を作成する
	def set_camera_coodinate_vector(self):
		# カメラのZ軸ベクトルを算出する
		# カメラの位置座標と、注視点の座標を使用する
		CV = [
			self.camera_x - self.lookat_x, self.camera_y - self.lookat_y, 
			self.camera_z - self.lookat_z]
		CZV_normal = normalize(CV)
		
		# カメラのX軸ベクトルを算出する
		# 注意)iOS のビューはY軸上に行くほど値減少
		# 注意)外積対象のベクトルの順序でX軸の方向が事なる
		CXV_cross = cross_product(CZV_normal, [0, -1, 0])
		CXV_normal = normalize(CXV_cross)
		
		# カメラのY軸ベクトルを算出する
		# 注意)外積対象のベクトルの順序でY軸の方向が異なる
		# 注意)正規化されたベクトル同士の外積なので改めて正規化は必要なし
		CYV_normal = cross_product(CZV_normal, CXV_normal)
		
		# カメラ移動計算用の内積を算出する
		camera_position = [self.camera_x, self.camera_y, self.camera_z]
		self.CPX = dot_product(camera_position, CXV_normal)
		self.CPY = dot_product(camera_position, CYV_normal)
		self.CPZ = dot_product(camera_position, CZV_normal)
		
		# 算出したビュー座標XYZ軸ベクトルをメンバ変数に格納
		self.CXV = CXV_normal
		self.CYV = CYV_normal
		self.CZV = CZV_normal
		
	
	# ビュー座標回転
	def camera_rotation(self, x, y, z):
		CXV = self.CXV	# ビュー座標のxyz軸ベクトル
		CYV = self.CYV
		CZV = self.CZV
		
		if len(CXV) != 3 or len(CYV) != 3 or len(CZV) != 3:
			return (x, y, z)
			
		CPX = self.CPX	# カメラ移動計算用の内積
		CPY = self.CPY
		CPZ = self.CPZ
		
		# カメラ座標への回転
		r_x = ((x * CXV[0]) + (y * CXV[1]) + (z * CXV[2]) + (-1 * CPX))
		r_y = ((x * CYV[0]) + (y * CYV[1]) + (z * CYV[2]) + (-1 * CPY))
		r_z = ((x * CZV[0]) + (y * CZV[1]) + (z * CZV[2]) + (-1 * CPZ))
		
		return (r_x, r_y, r_z)
	
	
	
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


	# 床の色を光源との角度、距離、光量から設定する
	# 床は青色である事を前提とする
	def set_floor_color(self, color, light_inner, light_length=1, brightness=1):
		
		# (光源光量 * cosθ) / 距離の二乗
		value = (-1 * brightness * light_inner) / light_length
		
		#value = (-1 * light_inner)
		# 反射率 RGB 基本的に青色を設定する
		r_ref, g_ref, b_ref = (0.5, 0.5, 1.0)
		#r_ref, g_ref, b_ref = (1.0, 1.0, 1.0)
		ui.set_color((r_ref * value, g_ref * value, b_ref * value, 1.0))
		
		
	
	# 内積の値cosθと光源との距離からuiにRGBの値を設定する
	# light_inner : 光源との角度(cosθ) 
	# 1=0度, 0=90度, -1=180度, 0=270度
	# light_length : 光源との距離の二乗
	# 入光する光の色は白(1.0, 1.0, 1.0)を前提とする
	# 鏡面度 specular
	# 反射受光角度　reflect_cos(視線と反射光の角度)
	def set_ui_color(self, color, light_inner, light_length=1, brightness=1, specular=0, specular_inner=1):
		
		# 拡散反射
		# (光源光量 * cosθ) / 距離の二乗
		diffused_value = 0
		if light_inner < 0:
			diffused_value = (-1 * brightness * light_inner) / light_length
		
		# 鏡面反射
		# (光源光量 * (反射光と視線の角度cosθ**鏡面度) / 距離の二乗
		# reflect_cos 反射光と視線のなす角度(cos)
		# 0未満: 光が鋭角で、当たっている
		#specular_light_value = (brightness * ((-1*reflect_cos)**specular)) / light_length
		specular_value = 0
		if specular_inner < 0:
			specular_value = (brightness * ((-1*specular_inner)**specular)) / light_length
		
		# 反射率 RGB
		r_ref, g_ref, b_ref = (1.0, 1.0, 1.0)
		
		if color == 'white':
			r_ref, g_ref, b_ref = (1.0, 1.0, 1.0)
		elif color == 'blue':
			r_ref, g_ref, b_ref = (0.05, 0.05, 1.0)
		elif color == 'green':
			r_ref, g_ref, b_ref = (0.05, 1.0, 0.05)
		elif color == 'red':
			r_ref, g_ref, b_ref = (1.0, 0.05, 0.05)
		elif color == 'yellow':
			r_ref, g_ref, b_ref = (1.0, 1.0, 0.1)
		elif color == 'orange':
			r_ref, g_ref, b_ref = (1.0, 0.8, 0.1)
		
		ui.set_color((
				r_ref * diffused_value + specular_value, 
				g_ref * diffused_value + specular_value, 
				b_ref * diffused_value + specular_value, 1.0))
	
	
	# 描画
	def draw(self):
		# 光源
		light_x ,light_y ,light_z = self.camera_rotation(self.light_x ,self.light_y ,self.light_z)
		
		# 床
		dot_row = self.floor.dot_row
		dot_col = self.floor.dot_col
		
		for row in range(0, dot_row):
			for col in range(0, dot_col):
				point = self.floor.points(row, col)
				a_x, a_y, a_z = self.camera_rotation(point[0][0], point[0][1], point[0][2])
				b_x, b_y, b_z = self.camera_rotation(point[1][0], point[1][1], point[1][2])
				c_x, c_y, c_z = self.camera_rotation(point[2][0], point[2][1], point[2][2])
				d_x, d_y, d_z = self.camera_rotation(point[3][0], point[3][1], point[3][2])
				
				# 法線ベクトルから表裏と陰影を算出する
				# 折り紙の部品の二辺のベクトルを算出する
				AB_vector = [b_x - a_x, b_y - a_y, b_z - a_z]
				AC_vector = [c_x - a_x, c_y - a_y, c_z - a_z]
				# 外積(法線ベクトル)を算出する
				triangle_cross_product = cross_product(AB_vector, AC_vector)
				# 正規化を行う
				triangle_normal = normalize(triangle_cross_product)
				
				# 視点焦点までのベクトルを算出する
				scr_vector = [
					0 - (a_x + b_x + c_x) / 3,
					0 - (a_y + b_y + c_y) / 3,
					self.screen_depth - (a_z + b_z + c_z) / 3]
				scr_normal = normalize(scr_vector)
				scr_inner = dot_product(triangle_normal, scr_normal)
				
				# 光源までのベクトルを算出する
				light_vector = [
					light_x - (a_x + b_x + c_x) / 3,
					light_y - (a_y + b_y + c_y) / 3,
					light_z - (a_z + b_z + c_z) / 3]
				light_normal = normalize(light_vector)
				# 光源との角度を算出する
				light_inner = dot_product(triangle_normal, light_normal)
				
				# 透視投影
				p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
				p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
				p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
				p_d_x, p_d_y = self.projection(d_x, d_y, d_z)
				# 床を描画
				path_f = ui.Path()
				path_f.move_to(p_a_x, p_a_y)
				path_f.line_to(p_b_x, p_b_y)
				path_f.line_to(p_c_x, p_c_y)
				path_f.line_to(p_d_x, p_d_y)
				path_f.line_to(p_a_x, p_a_y)
				# 描画色を設定する
				if scr_inner < 0.0:
					self.set_floor_color('blue', light_inner)
				path_f.fill()
		
		
		# 文字の座標をビュー座標に変換し配列に格納する
		# 文字を描画する
		for character in self.characters:
			# [[x,y,z,type,flag],[],...],[]
			contours = character.glyph(self.height)
			# ビュー座標変換
			for contour in contours:
				for i in range(0, len(contour)):
					f_x, f_y, f_z = self.camera_rotation(
						contour[i][0], contour[i][1], contour[i][2])
					contour[i][0], contour[i][1], contour[i][2] = f_x, f_y, f_z
					
			# 法線ベクトルの為の座標を取得
			point_for_vector = character.point_for_vector(self.height)
			
			# 影を描画する
			self.draw_round_shadow(point_for_vector)
			
			# 影の位置を算出する為の座標を確保する
			#point_for_vector_org = copy.deepcopy(point_for_vector)
			# ビュー座標変換
			for i in range(0, len(point_for_vector)):
				f_x, f_y, f_z = self.camera_rotation(
						point_for_vector[i][0], point_for_vector[i][1], point_for_vector[i][2])
				point_for_vector[i][0], point_for_vector[i][1], point_for_vector[i][2] = f_x, f_y, f_z
				
			# A→B、A→Cのベクトルを算出する
			font_v1 = [
				point_for_vector[1][0] - point_for_vector[0][0],
				point_for_vector[1][1] - point_for_vector[0][1],
				point_for_vector[1][2] - point_for_vector[0][2]]
			font_v2 = [
				point_for_vector[2][0] - point_for_vector[0][0],
				point_for_vector[2][1] - point_for_vector[0][1],
				point_for_vector[2][2] - point_for_vector[0][2]]
			
			# フォントの外積を算出し法線を取得する
			font_cross_vector = cross_product(font_v1, font_v2)
			# フォントの法線ベクトルを正規化する
			font_normal_vector = normalize(font_cross_vector)
			
			# フォントから視点焦点へのベクトルを算出する
			scr_vector = [
				0 - (point_for_vector[0][0] + point_for_vector[1][0] + point_for_vector[2][0]) / 3, 
				0 - (point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3, 
				self.screen_depth - (point_for_vector[0][2] + point_for_vector[1][2] + point_for_vector[2][2]) / 3]
			# 視点焦点までのベクトルを正規化する
			scr_normal_vector = normalize(scr_vector)
			# 正規化したフォントの法線ベクトルと視点焦点ベクトルとの内積を取得する
			scr_inner = dot_product(font_normal_vector, scr_normal_vector)
			
			# フォントから光源までのベクトルを算出する
			light_vector = [
				light_x - (point_for_vector[0][0] + point_for_vector[1][0] + point_for_vector[2][0]) / 3, 
				light_y - (point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3, 
				light_z - (point_for_vector[0][2] + point_for_vector[1][2] + point_for_vector[2][2]) / 3]
			# フォントから光源までのベクトルを正規化する
			light_normal_vector = normalize(light_vector)
			# 正規化したフォントの法線ベクトルと光源ベクトルとの内積を取得する
			light_inner = dot_product(font_normal_vector, light_normal_vector)
			
			# フォントを描画する
			path = ui.Path()
			for points in contours:
				if len(points) < 3:
					continue
				
				# 最初のglyph座標
				p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
				path.move_to(p_x, p_y)
			
				controls = []		# 制御点を格納する
				# 2番目以降のglyph座標
				for i in range(1, len(points)):
					self.draw_glyph(points[i], controls, path)
				# 最後のglyph座標
				self.draw_glyph(points[0], controls, path)
				
			# フォントの色設定と塗り潰し
			if scr_inner < 0.0:
				self.set_ui_color(
					character.mycolor(), light_inner)
			else:
				ui.set_color('black')
			path.fill()
			
	
	# 丸い影を描画する
	# point_for_vector: 法線ベクトルの作成に使用する文字の座標
	def draw_round_shadow(self, point_for_vector):
		#床の適当な座標を取得
		point = self.floor.points(0, 0)
		
		# 床の水平位置から、床の中央に適当な円を描画する
		shadow_r = 50 * (500 / abs((point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3 - point[0][1]))	
		step = 10			# 丸影の図形の頂点頻度　少ない程丸に近い
			
		# character の x, z 位置を取得する
		shadow_center_x = (point_for_vector[1][0] + point_for_vector[2][0]) / 2
		shadow_center_z = (point_for_vector[1][2] + point_for_vector[2][2]) / 2
			
		path_s = ui.Path()
		for angle in range(0, 361, step):
			s_x = shadow_r * cos(radians(angle)) + shadow_center_x
			s_y = point[0][1]
			s_z = shadow_r * sin(radians(angle)) + shadow_center_z
				
			# ビュー座標
			s_x, s_y, s_z = self.camera_rotation(s_x, s_y, s_z)
			# 透視投影
			p_s_x, p_s_y = self.projection(s_x, s_y, s_z)
			
			if angle == 0:
				path_s.move_to(p_s_x, p_s_y)
			else:
				path_s.line_to(p_s_x, p_s_y)
		
		ui.set_color((0.0, 0.0, 0.0, 0.6))
		path_s.fill()
			
	
	
	# 正規化した反射光のベクトルと視線のベクトルの
	# なす角度を算出してcos数値で返す
	# light_vector: 光源から図形のベクトル
	# triangle_normal: 図形の法線(正規化済)
	# scr_normal: 図形への視線(正規化済)
	def specular_inner(self, light_vector, triangle_normal, scr_normal):
		nega_light_vector = [
			-1 * light_vector[0],
			-1 * light_vector[1],
			-1 * light_vector[2]]
		# 入光ベクトルと法線の内積で光源までの距離cosを算出
		light_cos = dot_product(nega_light_vector, triangle_normal)
		# 反射光ベクトル R = F + 2(-F・N)N
		r_light_vector = [
			light_vector[0] + (2 * light_cos * triangle_normal[0]),
			light_vector[1] + (2 * light_cos * triangle_normal[1]),
			light_vector[2] + (2 * light_cos * triangle_normal[2])]
		
		# 視線と反射光のなす角度を求める
		# 反射光のベクトルを正規化する
		r_light_normal = normalize(r_light_vector)
		# 反射受光角度を算出する
		specular_inner = dot_product(scr_normal, r_light_normal)
		
		return specular_inner



# カメラの位置上昇下降
# goal_y: カメラ位置目的y座標値
# add_y: 上昇下降移動量
def change_view_y_schedule(main_view, goal_y, add_y, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
		
	lock.acquire()
	
	main_view.camera_y += add_y
	
	if abs(main_view.camera_y - goal_y) < add_y:
		main_view.camera_y = goal_y
	# ビュー座標を更新する
	main_view.set_camera_coodinate_vector()
	
	lock.release()
	
	if main_view.on_screen is True and isclose(main_view.camera_y, goal_y) is False:
		t = threading.Timer(0.02, change_view_y_schedule, args=[main_view, goal_y, add_y, lock])
		t.start()


# カメラが外周を円旋回する
def change_view_round_schedule(main_view, angle, goal_angle, lock):
	
	if isinstance(main_view, BaseView) is False:
		return
	
	round = 450
	add_angle = 0.5
	
	lock.acquire()
	
	angle += add_angle
	if abs(goal_angle - angle) < add_angle:
		angle = goal_angle
	
	main_view.camera_x = round * cos(radians(angle))
	main_view.camera_z = round * sin(radians(angle)) + (-250)
	main_view.set_camera_coodinate_vector()
	#main_view.set_needs_display()
	
	lock.release()
	
	if main_view.on_screen is True and isclose(angle, goal_angle) is False:
		t = threading.Timer(0.02, change_view_round_schedule, args=[main_view, angle, goal_angle, lock])
		t.start()
		

# 再描画処理
def display_schedule(main_view, lock):
	if isinstance(main_view, BaseView) is False:
		return
		
	#lock.acquire()
	main_view.set_needs_display()
	#lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.012, display_schedule, args=[main_view, lock])
		#t = threading.Timer(0.024, display_schedule, args=[main_view, lock])
		t.start()


# font をY軸に回転させる
# 一周するまで本関数が繰り返し呼ばれる
# 回転中に文字の「文字列を表示するフラグ」を設定する
def rotate_y_font_schedule(main_view, character):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(character, Character) is False:
		return
	
	character.rotate_angle_y += 10
	if character.rotate_angle_y >= 360:
		character.set_angle_y(0)
	
	if character.rotate_angle_y >= 270 and character.rotate_angle_y < 290:
		character.set_enable_name(True)

	
	if main_view.on_screen is True and character.rotate_angle_y > 0:
		t = threading.Timer(0.02, rotate_y_font_schedule, args=[main_view, character])
		t.start()


# font x軸に回転させる
# 一周するまで本関数が繰り返し呼ばれる
def rotate_x_font_schedule(main_view, character):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(character, Character) is False:
		return
	
	character.rotate_angle_x += 10
	if character.rotate_angle_x >= 360:
		character.set_angle_x(0)
	
	main_view.set_needs_display()
	
	if main_view.on_screen is True and character.rotate_angle_x > 0:
		t = threading.Timer(0.02, rotate_x_font_schedule, args=[main_view, character])
		t.start()


# 目的地座標に移動する
# goal_point 目的地座標xyz
def set_proceed_character(character, goal_point, frame, lock):
	if isinstance(character, Character) is False:
		return
	
	process_v3 = [
		goal_point[0] - character.position[0],
		goal_point[1] - character.position[1],
		goal_point[2] - character.position[2]]
	# 進行ベクトル
	proceed_v3 = [
		process_v3[0] / frame, 
		process_v3[1] / frame,
		process_v3[2] / frame]
		
	lock.acquire()
	character.proceed_v3 = proceed_v3
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.012, proceed_character, args=[character, goal_point, lock])
		t.start()
	


# 目的地座標に移動する
# goal_point 目的地座標xyz
def proceed_character(character, goal_point, lock):
	if isinstance(character, Character) is False:
		return
	
	# 進行ベクトルの長さ(の二乗)を算出する
	proceed_length = character.proceed_v3[0] ** 2 + character.proceed_v3[1] ** 2 + character.proceed_v3[2] ** 2
	# 目的地までの距離(の二乗)を算出する
	process_v3 = [
		goal_point[0] - character.position[0],
		goal_point[1] - character.position[1],
		goal_point[2] - character.position[2]]
	goal_length = process_v3[0] ** 2 + process_v3[1] ** 2 + process_v3[2] ** 2
	
	lock.acquire()
	is_goal = False
	# 進行ベクトルの長さが目的地までの距離より長い場合
	if proceed_length < goal_length:
		character.proceed()
	else:
		character.translate(
			goal_point[0], goal_point[1], goal_point[2])
		character.proceed_v3[0] = 0
		character.proceed_v3[1] = 0
		character.proceed_v3[2] = 0
		is_goal = True
	lock.release()
	
	if main_view.on_screen is True and is_goal is False:
		t = threading.Timer(0.012, proceed_character, args=[character, goal_point, lock])
		t.start()


# 文字を周回させる
# angle 太陽を中心とした周回位置の角度
# add_angle 角度の更新量
# r 周回半径
def round_character_schedule(main_view, character, angle, add_angle, r, lock):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(character, Character) is False:
		return
	if add_angle == 0:
		return 
	
	angle += add_angle
	if angle > 360 or angle < 0:
		angle %= 360
	
	round_center_x = -1000
	round_center_y = 7500
	
	x = cos(radians(angle)) * r + round_center_x
	y = sin(radians(angle)) * r + round_center_y
	
	lock.acquire()
	
	character.position[0] = x
	character.position[1] = y
	
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.02, round_character_schedule, args=[main_view, character, angle, add_angle, r, lock])
		t.start()
	


if __name__ == '__main__':
	# メイン画面の作成
	main_view = BaseView(frame=(0, 0, 375, 667))
	main_view.name = 'へのへのもへじ'
	main_view.background_color = 'lightblue'
	
	# カメラの位置
	main_view.set_camera_position(0, 0, 200)
	# カメラの注視点
	main_view.set_lookat_position(0, 0, -250)
	# ビュー座標の軸を生成する
	main_view.set_camera_coodinate_vector()
	
	# 床
	floor = MyFloor(-420, 300, 150)
	main_view.set_floor(floor)

	# 文字
	rotate_center_x = -800
	rotate_center_y = -800
	start_scale = 0.10
	
	char_HE_1 = Character(glyph_HE_JP())
	char_HE_1.set_center(rotate_center_x, rotate_center_y, 0)
	# 注意! Characterクラスのy座標は上がプラス値
	char_HE_1.translate(0, 9000, -2500)
	char_HE_1.set_scale(start_scale)
	char_HE_1.set_color('green')
	main_view.add_character(char_HE_1)
	
	char_NO_1 = Character(glyph_NO_JP())
	char_NO_1.set_center(rotate_center_x, rotate_center_y, 0)
	char_NO_1.translate(0, 7000, -2500)
	char_NO_1.set_scale(start_scale)
	char_NO_1.set_color('white')
	main_view.add_character(char_NO_1)
	
	char_HE_2 = Character(glyph_HE_JP())
	char_HE_2.set_center(rotate_center_x, rotate_center_y, 0)
	char_HE_2.translate(-2000, 9000, -2500)
	char_HE_2.set_scale(start_scale)
	char_HE_2.set_color('green')
	main_view.add_character(char_HE_2)
	
	char_NO_2 = Character(glyph_NO_JP())
	char_NO_2.set_center(rotate_center_x, rotate_center_y, 0)
	char_NO_2.translate(-2000, 7000, -2500)
	char_NO_2.set_scale(start_scale)
	char_NO_2.set_color('white')
	main_view.add_character(char_NO_2)
	
	char_MO = Character(glyph_MO_JP())
	char_MO.set_center(rotate_center_x, rotate_center_y, 0)
	char_MO.translate(-1000, 5000, -2500)
	char_MO.set_scale(start_scale)
	char_MO.set_color('blue')
	main_view.add_character(char_MO)
	
	main_view.present()
	
	# タイマー処理を設定する
	lock = threading.Lock()
	
	# 文字リスト
	character_list = [char_HE_1, char_NO_1, char_HE_2, char_NO_2, char_MO]
	
	# 中心
	round_center_x = -1000
	round_center_y = 7500
	radius = 2500
	
	delay = 1.5
	# _文字をY軸に回転させる
	for character in character_list:
		tr1 = threading.Timer(delay, rotate_y_font_schedule, args=[main_view, character])
		tr1.start()
		delay += 0.5
	
	
	delay += 2.0
	# 文字を円陣に移動する
	angle = 0
	for character in character_list:
		x = radius * cos(radians(angle)) + round_center_x
		y = radius * sin(radians(angle)) + round_center_y
		angle += 72
		
		ts1 = threading.Timer(
			delay, set_proceed_character, args=[character, [x, y, -2500], 100, lock])
		ts1.start()
		
	
	delay += 3.0
	# 文字をX軸に回転させる
	for character in character_list:
		tr2 = threading.Timer(delay, rotate_x_font_schedule, args=[main_view, character])
		tr2.start()
		delay += 0.5
	
	delay += 3.0
	# 文字が周回
	angle = 0
	for character in character_list:
		tr3 = threading.Timer(delay, round_character_schedule, args=[main_view, character, angle, 2, 2500, lock])
		tr3.start()
		angle += 72

	
	delay += 5.0
	# 視点移動　上昇
	tv1 = threading.Timer(delay, change_view_y_schedule, args=[main_view, -200, -4, lock])
	tv1.start()
	
	
	# 視点移動　周回
	delay += 0.5
	tv2 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 90+360, lock])
	tv2.start()
	
	for i in range(3):
		delay += 3.0
		# 文字をY軸に回転させる
		for character in character_list:
			tr4 = threading.Timer(delay, rotate_y_font_schedule, args=[main_view, character])
			tr4.start()
			delay += 0.5
	
		delay += 3.0
		# 文字をX軸に回転させる
		for character in character_list:
			tr5 = threading.Timer(delay, rotate_x_font_schedule, args=[main_view, character])
			tr5.start()
			delay += 0.5
	
	delay += 0.1
	# 視点移動　下降
	tv3 = threading.Timer(delay, change_view_y_schedule, args=[main_view, 0, 4, lock])
	tv3.start()
	
	td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
	td.start()
	
	
