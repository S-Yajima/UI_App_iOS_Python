import ui
import threading
import copy
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from math import isclose
from figure import *
from glyph import *
from character import *

# 光源。球を継承して別クラスとして扱う
class MySun(Sphere):
	brightness = 60000
	pass

# 床。タイルにする。
class  MyFloor():
	position = []
	
	dot_size = 50
	dot_gap = 3
	
	dot_row = 30
	dot_col = 25 
	
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

	def level(self):
		return self.position[1]
	
	
	
# 背景と床を描画する
class BaseView(ui.View):
	
	screen_depth = 400	# 視点から投影面までの距離
	
	# 光源
	sun = None
	
	# 床
	floor = None
	floor_normal_v3 = None				# 床の法線
	floor_any_point = None
	
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
		else:
			return
			
		#床の法線を算出する
		points = floor.points(0, 0)
		AB_v3 = [points[1][0] - points[0][0], 
							points[1][1] - points[0][1], 
							points[1][2] - points[0][2]]
		AC_v3 = [points[2][0] - points[0][0], 
							points[2][1] - points[0][1], 
							points[2][2] - points[0][2]]
		AB_AC_cross_v3 = cross_product(AB_v3, AC_v3)
		self.floor_normal_v3 = normalize(AB_AC_cross_v3)
		self.floor_any_point = [
			points[1][0], points[1][1], points[1][2]]
			
	
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
		if z != 0:
			
			r_x = ((depth / z) * x) + center_x
			r_y = ((depth / z) * y) + center_y
			'''
			r_x = ((depth / (z + depth)) * x) + center_x
			r_y = ((depth / (z + depth)) * y) + center_y
			'''
		return (r_x, r_y)

	
	# 文字のソート
	def sort_character(self, character):
		c_x, c_y, c_z = self.camera_rotation(
			sphere.center[0], sphere.center[1], sphere.center[2])
		
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			0 - c_x,
			0 - c_y,
			self.screen_depth - c_z]
		
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

		return length
	
	
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


	# sort
	# ビュー変換後の座標で、視点からの距離の値を比較しソートを行う
	def sort_triangle(self, corners):
		a_x, a_y, a_z = (corners[0][0], corners[0][1],corners[0][2])
		b_x, b_y, b_z = (corners[1][0], corners[1][1],corners[1][2])
		c_x, c_y, c_z = (corners[2][0], corners[2][1],corners[2][2])
		
		# 視点焦点までのベクトルを算出する
		scr_vector = [
			0 - (a_x + b_x + c_x) / 3,
			0 - (a_y + b_y + c_y) / 3,
			self.screen_depth - (a_z + b_z + c_z) / 3]
		length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2
			
		return length


	# 光源を返す
	def light_point(self):
		x, y, z = (0, 0, 0)
		if self.sun != None:
			x, y, z = (
				self.sun.center[0], 
				self.sun.center[1], 
				self.sun.center[2], 
			)
		return (x, y, z)


	# 描画
	def draw(self):
		# 光源
		local_light_x ,local_light_y ,local_light_z = self.light_point()
		light_x ,light_y ,light_z = self.camera_rotation(local_light_x ,local_light_y ,local_light_z)
		
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
				
				# 床の法線ベクトルを算出する
				# 法線ベクトルから表裏と陰影を算出する
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
				
				# 光源までの距離の二乗
				light_distance = light_vector[0] ** 2 + light_vector[1] ** 2 + light_vector[2] ** 2
				
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
					self.set_floor_color('blue', light_inner, light_distance, self.sun.brightness)
				path_f.fill()
		
		
		# 文字の座標をビュー座標に変換し配列に格納する
		# 文字を描画する
		for character in self.characters:
			# [[x,y,z,type,flag],[],...],[]
			contours = character.glyph(self.height)
			# 影の位置を算出する為の座標を確保する
			local_contours = copy.deepcopy(contours)
			
			# フォント本体のビュー座標変換
			for contour in contours:
				for i in range(0, len(contour)):
					contour[i][0], contour[i][1], contour[i][2] = self.camera_rotation(
						contour[i][0], contour[i][1], contour[i][2])
			
			# 法線ベクトルの為の座標を取得
			point_for_vector = character.point_for_vector(self.height)
			
			# 影の位置を算出する為の座標を確保する
			local_points = copy.deepcopy(point_for_vector)
			# ローカル座標の法線ベクトルを算出
			local_font_normal = self.normal_with_points(local_points)
			
			# 影を描画する
			self.draw_shadow(local_contours, [local_light_x, local_light_y, local_light_z], local_font_normal)
			
			# フォント本体を描画するための法線をビュー座標変換し算出する
			for i in range(0, len(point_for_vector)):
				point_for_vector[i][0], point_for_vector[i][1], point_for_vector[i][2] = self.camera_rotation(point_for_vector[i][0], point_for_vector[i][1], point_for_vector[i][2])
			font_normal_vector = self.normal_with_points(point_for_vector)
			
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
				
			# 光源までの距離の二乗
			light_distance = light_vector[0] ** 2 + light_vector[1] ** 2 + light_vector[2] ** 2
			
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
					character.mycolor(), light_inner, light_distance, self.sun.brightness)
			else:
				ui.set_color('black')
			path.fill()
			
		# 光源の球を描画する
		self.draw_light_sphere()


	# 光源からのベクトルを反映した文字の影を描画する
	# 床の法線はビュー変換に対応してないため、ローカル座標で影の座標を計算する
	# contours		: 影の描画に使用する文字の座標
	# light_point	: 光源のxyz座標配列
	# font_normal_v3 :	フォントの法線
	def draw_shadow(self, contours, light_point, font_normal_v3):
		# 法線の逆ベクトル
		r_font_normal_v3 = [
			-1 * font_normal_v3[0], 
			-1 * font_normal_v3[1],
			-1 * font_normal_v3[2]]
		
		#フォントの影をを描画する
		path_s = ui.Path()
		for points in contours:
			if len(points) < 3:
				continue
			
			for point in points:
				# 光源からの影を描画するように修正する
				light_figure_v3 = [
					point[0] - light_point[0], 
					point[1] - light_point[1], 
					point[2] - light_point[2]]
				# フォントと光源の距離
				light_figure_distance = abs(dot_product(light_figure_v3, font_normal_v3))
				
				# 床の任意の点からフォント座標へのベクトル
				floor_figure_v3 = [
					point[0] - self.floor_any_point[0],
					point[1] - self.floor_any_point[1],
					point[2] - self.floor_any_point[2]]
				
				# フォントと床の距離
				floor_figure_distance = abs(dot_product(floor_figure_v3, self.floor_normal_v3))
				
				# 影の座標を算出する
				if light_figure_distance != 0:
					rate = floor_figure_distance / light_figure_distance
					point[0] = point[0] + (light_figure_v3[0] * rate)
					point[1] = point[1] + (light_figure_v3[1] * rate)
					point[2] = point[2] + (light_figure_v3[2] * rate)
				
				# ビュー座標変換を行う
				point[0], point[1], point[2] = self.camera_rotation(
					point[0], point[1], point[2])
				
			# 最初のglyph座標
			p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
			path_s.move_to(p_x, p_y)
			
			controls = []		# 制御点を格納する
			# 2番目以降のglyph座標
			for i in range(1, len(points)):
				self.draw_glyph(points[i], controls, path_s)
			# 最後のglyph座標
			self.draw_glyph(points[0], controls, path_s)
				
		# フォントの色設定と塗り潰し
		ui.set_color((0.0, 0.0, 0.0, 0.5))
		path_s.fill()
	
	
	# 三点のx,y,z座標の配列から法線を算出して返す
	# points : 頂点A,B,Cの三次元座標配列
	# 				[x,y,z],[x,y,z],[x,y,z]
	def normal_with_points(self, points):
		# A→B、A→Cのベクトルを算出する
		font_v1 = [
			points[1][0] - points[0][0],
			points[1][1] - points[0][1],
			points[1][2] - points[0][2]]
		font_v2 = [
			points[2][0] - points[0][0],
			points[2][1] - points[0][1],
			points[2][2] - points[0][2]]
			
		# フォントの外積を算出し法線を取得する
		font_cross_vector = cross_product(font_v1, font_v2)
		# フォントの法線ベクトルを正規化し返す
		return normalize(font_cross_vector)
		
		
	
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


	# 三角関数の数値
	def trigono_value(self, triangle):
		rad_x = radians(triangle.rotate_angle_x)
		rad_y = radians(triangle.rotate_angle_y) 
		rad_z = radians(triangle.rotate_angle_z)
		
		return (cos(rad_x), cos(rad_y), cos(rad_z), sin(rad_x), sin(rad_y), sin(rad_z))

	
	# 光源球を描画する
	def draw_light_sphere(self):
		###
		# 球の座標をビュー座標に変換し配列に格納する
		# 太陽と惑星を含めた球体
		triangles = []
		
		# 三角関数の値を予め取得。
		# 結果が同じ値のcos,sin処理の繰り返しを避ける為。
		cos_x, cos_y, cos_z, sin_x, sin_y, sin_z = self.trigono_value(self.sun.triangles[0])
		# ビュー座標を配列に格納
		for triangle in self.sun.triangles:
			corners = []
			a_x, a_y, a_z = triangle.corner_A_with_trigono(cos_x, cos_y, cos_z, sin_x, sin_y, sin_z)
			b_x, b_y, b_z = triangle.corner_B_with_trigono(cos_x, cos_y, cos_z, sin_x, sin_y, sin_z)
			c_x, c_y, c_z = triangle.corner_C_with_trigono(cos_x, cos_y, cos_z, sin_x, sin_y, sin_z)
				
			a_x, a_y, a_z = self.camera_rotation(a_x, a_y, a_z)
			b_x, b_y, b_z = self.camera_rotation(b_x, b_y, b_z)
			c_x, c_y, c_z = self.camera_rotation(c_x, c_y, c_z)
				
			corners.append([a_x, a_y, a_z])
			corners.append([b_x, b_y, b_z])
			corners.append([c_x, c_y, c_z])
			triangles.append(corners)
			
		# 取得したビュー座標を視点からの距離でソートする
		sorted_triangles = sorted(triangles, key=self.sort_triangle, reverse=True)
			
		# ソート済の三角形ビュー座標の配列で描画を行う
		for corners in sorted_triangles:
			a_x, a_y, a_z = (corners[0][0], corners[0][1], corners[0][2])
			b_x, b_y, b_z = (corners[1][0], corners[1][1], corners[1][2])
			c_x, c_y, c_z = (corners[2][0], corners[2][1], corners[2][2])
				
			p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
			p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
			p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
				
			path_t = ui.Path()
			path_t.move_to(p_a_x, p_a_y)
			path_t.line_to(p_b_x, p_b_y)
			path_t.line_to(p_c_x, p_c_y)
			path_t.line_to(p_a_x, p_a_y)
				
			# 太陽の場合は明るい白で固定
			ui.set_color('white')
			path_t.fill()
			


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


# 再描画処理
def display_schedule(main_view, lock):
	if isinstance(main_view, BaseView) is False:
		return
		
	#lock.acquire()
	main_view.set_needs_display()
	#lock.release()
	
	if main_view.on_screen is True:
		#t = threading.Timer(0.012, display_schedule, args=[main_view, lock])
		t = threading.Timer(0.024, display_schedule, args=[main_view, lock])
		t.start()


# 目的地座標に移動する
# goal_point 目的地座標xyz
def set_proceed_sphere(sphere, goal_point, frame, lock):
	if isinstance(sphere, Sphere) is False:
		return
	
	process_v3 = [
		goal_point[0] - sphere.center[0],
		goal_point[1] - sphere.center[1],
		goal_point[2] - sphere.center[2]]
	# 進行ベクトル
	proceed_v3 = [
		process_v3[0] / frame, 
		process_v3[1] / frame,
		process_v3[2] / frame]
		
	lock.acquire()
	sphere.set_proceed_vector(
		proceed_v3[0], proceed_v3[1], proceed_v3[2])
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.012, proceed_sphere, args=[sphere, goal_point, lock])
		t.start()


# 目的地座標に移動する
# goal_point 目的地座標 xyz
def proceed_sphere(sphere, goal_point, lock):
	if isinstance(sphere, Sphere) is False:
		return
	
	# 進行ベクトルの長さ(の二乗)を算出する
	proceed_length = sphere.proceed_vector[0] ** 2 + sphere.proceed_vector[1] ** 2 + sphere.proceed_vector[2] ** 2
	# 目的地までの距離(の二乗)を算出する
	process_v3 = [
		goal_point[0] - sphere.center[0],
		goal_point[1] - sphere.center[1],
		goal_point[2] - sphere.center[2]]
	goal_length = process_v3[0] ** 2 + process_v3[1] ** 2 + process_v3[2] ** 2
	
	lock.acquire()
	is_goal = False
	# 進行ベクトルの長さが目的地までの距離より長い場合
	if proceed_length < goal_length:
		sphere.proceed()
	else:
		sphere.set_center(
			goal_point[0], goal_point[1], goal_point[2])
		sphere.set_proceed_vector(0, 0, 0)
		is_goal = True
	lock.release()
	
	if main_view.on_screen is True and is_goal is False:
		t = threading.Timer(0.012, proceed_sphere, args=[sphere, goal_point, lock])
		t.start()


# 文字座標を上昇させる
# goal_y 目的地座標y
def set_proceed_character(character, goal_y, speed, lock):
	if isinstance(character, Character) is False:
		return
	
	# 進行ベクトル
	proceed_v3 = [0, speed, 0]
		
	lock.acquire()
	character.proceed_v3 = proceed_v3
	lock.release()
	
	if main_view.on_screen is True:
		t = threading.Timer(0.012, proceed_character, args=[character, goal_y, lock])
		t.start()
	

# 文字座標を上昇させる
# goal_y 目的地座標 y
def proceed_character(character, goal_y, lock):
	if isinstance(character, Character) is False:
		return
	
	lock.acquire()
	is_goal = False
	# 
	if character.position[1] < goal_y:
		character.proceed()
	else:
		character.translate(
			character.position[0], goal_y, character.position[2])
		character.proceed_v3[0] = 0
		character.proceed_v3[1] = 0
		character.proceed_v3[2] = 0
		is_goal = True
	lock.release()
	
	if main_view.on_screen is True and is_goal is False:
		t = threading.Timer(0.012, proceed_character, args=[character, goal_y, lock])
		t.start()


# 太陽の明るさを変更する
def change_bright_schedule(main_view, sphere, goal_bright, add_bright, lock):
	if isinstance(main_view, BaseView) is False:
		return
	if isinstance(sphere, MySun) is False:
		return
	if add_bright == 0:
		return 
	
	lock.acquire()
	
	is_goal = False
	# 明るさが目標よりも明るく変化する明るさがプラスの場合
	if sphere.brightness >= goal_bright and 0 <= add_bright:
		is_goal = True
		sphere.brightness = goal_bright
	# 明るさが目標よりも暗く変化する明るさがマイナスの場合
	elif sphere.brightness <= goal_bright and 0 >= add_bright:
		is_goal = True
		sphere.brightness = goal_bright
	else:
		sphere.brightness += add_bright
	
	lock.release()
		
	if main_view.on_screen is True and is_goal is False:
		t = threading.Timer(0.02, change_bright_schedule, args=[main_view, sphere, goal_bright, add_bright, lock])
		t.start()


# 3Dフォントを生成する
def character_with_info(glyph, x, y, z, glyph_scale):
	rotate_center_x = -800
	rotate_center_y = -800
	scale = 0.1
	
	if isclose(glyph_scale, 1.000) is False:
		for contour in glyph:
			for point in contour:
				point[0] *= glyph_scale
				point[1] *= glyph_scale
				
	character = Character(glyph)
	character.set_center(rotate_center_x, rotate_center_y, 0)
	
	character.set_angle_x(270) # x=360 に回すと立つ
	
	character.translate(x, y, z)
	character.set_scale(scale)
	character.set_color('blue')
	
	return character

	

if __name__ == '__main__':
	# メイン画面の作成
	main_view = BaseView(frame=(0, 0, 375, 667))
	main_view.name = '将棋棋聖戦'
	main_view.background_color = '#00009f'
	
	camera_pos_z = -400
	camera_pos_x = 200
	camera_pos_y = -1000
	
	# カメラの位置
	# 真横
	#main_view.set_camera_position(0, 0, 600) 
	# 真上
	main_view.set_camera_position(
		camera_pos_x, camera_pos_y, camera_pos_z + 1)
	# 斜め上
	#main_view.set_camera_position(0, -450, -150)	
	# カメラの注視点
	main_view.set_lookat_position(
		camera_pos_x, 0, camera_pos_z)
	#main_view.set_lookat_position(0, 0, -250)
	# ビュー座標の軸を生成する
	main_view.set_camera_coodinate_vector()

	# 床
	floor = MyFloor(-450, 300, 300)
	main_view.set_floor(floor)
	
	# 太陽
	sun_pos_x = camera_pos_x
	sun_pos_y = 50
	sun_pos_z = -1000
	sun = MySun(10, is_hide=False)
	sun.set_center(sun_pos_x, sun_pos_y, sun_pos_z)
	sun.brightness = 10000 * 0.2
	sun.face_color = 'white'
	main_view.sun = sun

	start_scale = 0.4
	def_y = 1900
	#def_y = 2500
	
	# タイトル　タ
	def_z = -10000
	
	char_Title_Ta = character_with_info(glyph_タ_JP(), -3000, def_y, def_z, start_scale)
	main_view.add_character(char_Title_Ta)
	# タイトル　イ
	char_Title_I = character_with_info(glyph_イ_JP(), -2200, def_y, def_z, start_scale)
	main_view.add_character(char_Title_I)
	# タイトル　ト
	char_Title_To = character_with_info(glyph_ト_JP(), -1400, def_y, def_z, start_scale)
	main_view.add_character(char_Title_To)
	# タイトル　ル
	char_Title_Ru = character_with_info(glyph_ル_JP(), -600, def_y, def_z, start_scale)
	main_view.add_character(char_Title_Ru)
	# ホルダー　ホ
	char_Holder_Ho = character_with_info(glyph_ホ_JP(), 200, def_y, def_z, start_scale)
	main_view.add_character(char_Holder_Ho)
	# ホルダー　ル
	char_Holder_Ru = character_with_info(glyph_ル_JP(), 1000, def_y, def_z, start_scale)
	main_view.add_character(char_Holder_Ru)
	# ホルダー　ダ
	char_Holder_Da = character_with_info(glyph_ダ_JP(), 1800, def_y, def_z, start_scale)
	main_view.add_character(char_Holder_Da)
	# ホルダー　ー
	char_Holder_Long = character_with_info(glyph_ー_JP(), 2600, def_y, def_z, start_scale)
	main_view.add_character(char_Holder_Long)
	
	
	def_z = -8000
	start_scale = 1.0
	# 渡辺明　渡
	char_Watanabe_Wata = character_with_info(glyph_渡_JP(), -3000, def_y, def_z, start_scale)
	main_view.add_character(char_Watanabe_Wata)
	# 渡辺明　辺
	char_Watanabe_Nabe = character_with_info(glyph_辺_JP(), -1000, def_y, def_z, start_scale)
	main_view.add_character(char_Watanabe_Nabe)
	# 渡辺明　明
	char_Akira = character_with_info(glyph_明_JP(), 1000, def_y, def_z, start_scale)
	main_view.add_character(char_Akira)
	
	# 三冠　三
	start_scale = 0.6
	char_3Kan_3 = character_with_info(glyph_三_JP(), 3000, def_y, def_z, start_scale)
	main_view.add_character(char_3Kan_3)
	# 三冠　冠
	char_3Kan_Kan = character_with_info(glyph_冠_JP(), 4200, def_y, def_z, start_scale)
	main_view.add_character(char_3Kan_Kan)
	
	
	def_z = -6000
	start_scale = 0.4
	# 挑戦者　挑
	char_Tyosensya_Tyou = character_with_info(glyph_挑_JP(), -3000, def_y, def_z, start_scale)
	main_view.add_character(char_Tyosensya_Tyou)
	# 挑戦者　戦
	char_Tyosensya_Sen = character_with_info(glyph_戦_JP(), -2100, def_y, def_z, start_scale)
	main_view.add_character(char_Tyosensya_Sen)
	# 挑戦者　者
	char_Tyosensya_Sya = character_with_info(glyph_者_JP(), -1200, def_y, def_z, start_scale)
	main_view.add_character(char_Tyosensya_Sya)
	
	def_z = -4000
	start_scale = 1.0
	# 藤井 藤
	char_Fujii_Fuji = character_with_info(glyph_藤_JP(), -3000, def_y, def_z, start_scale)
	main_view.add_character(char_Fujii_Fuji)
	# 藤井 井
	char_Fujii_I = character_with_info(glyph_井_JP(), -1000, def_y, def_z, start_scale)
	main_view.add_character(char_Fujii_I)
	# 聡太　聡
	char_Souta_Sou = character_with_info(glyph_聡_JP(), 1000, def_y, def_z, start_scale)
	main_view.add_character(char_Souta_Sou)
	# 聡太　太
	char_Souta_Ta = character_with_info(glyph_太_JP(), 3000, def_y, def_z, start_scale)
	main_view.add_character(char_Souta_Ta)
	
	start_scale = 0.6
	# 7段 七
	char_7Dan_7 = character_with_info(glyph_七_JP(), 5000, def_y, def_z, start_scale)
	main_view.add_character(char_7Dan_7)
	# 7段 段
	char_7Dan_Dan = character_with_info(glyph_段_JP(), 6200, def_y, def_z, start_scale)
	main_view.add_character(char_7Dan_Dan)
	
	
	# 棋聖戦	棋
	def_z = 0
	start_scale = 1.0
	
	char_Kiseisen_Ki = character_with_info(glyph_棋_JP(), -1000, def_y, def_z, start_scale)
	main_view.add_character(char_Kiseisen_Ki)
	# 棋聖戦	聖
	char_Kiseisen_Sei = character_with_info(glyph_聖_JP(), 1000, def_y, def_z, start_scale)
	main_view.add_character(char_Kiseisen_Sei)
	#	棋聖戦	戦
	char_Kiseisen_Sen = character_with_info(glyph_戦_JP(), 3000, def_y, def_z, start_scale)
	main_view.add_character(char_Kiseisen_Sen)
	
	main_view.present()
	
	# タイマー処理を設定する
	lock = threading.Lock()
	
	delay = 1.5
	sun_pos_z += 280
	
	# 光源を動かす
	goal_pos = [sun_pos_x, sun_pos_y, sun_pos_z]
	tsp1 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 70, lock])
	tsp1.start()
	
	# 光源を動かす
	delay += 4
	sun_pos_x += -200
	goal_pos = [sun_pos_x, 0, sun_pos_z]
	tsp2 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 50, lock])
	tsp2.start()
	
	# 太陽の明るさを変える
	delay += 2.0
	tb1 = threading.Timer(delay, change_bright_schedule, args=[main_view, sun, 120000, 5000, lock])
	tb1.start()
	
	# 文字を動かす
	goal_y = 2300
	charcters = [
		char_Title_Ta, char_Title_I, char_Title_To, char_Title_Ru, char_Holder_Ho, char_Holder_Ru, char_Holder_Da, char_Holder_Long, char_Watanabe_Wata, char_Watanabe_Nabe, char_Akira, char_3Kan_3, char_3Kan_Kan]
	delay += 5
	for character in charcters:
		tsc1 = threading.Timer(
			delay, set_proceed_character, args=[character, goal_y, 10, lock])
		tsc1.start()
	
	# 光源を動かす
	delay += 5
	sun_pos_z += 250
	goal_pos = [sun_pos_x, 0, sun_pos_z]
	tsp3 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 70, lock])
	tsp3.start()
	
	# 光源を動かす
	delay += 5
	sun_pos_x += 100
	goal_pos = [sun_pos_x, 0, sun_pos_z]
	tsp4 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 70, lock])
	tsp4.start()
	
	# 文字を動かす
	charcters = [
		char_Tyosensya_Tyou, char_Tyosensya_Sen, char_Tyosensya_Sya, char_Fujii_Fuji, char_Fujii_I, char_Souta_Sou, char_Souta_Ta, char_7Dan_7, char_7Dan_Dan]
	goal_y = 2300
	delay += 3
	for character in charcters:
		tsc2 = threading.Timer(
			delay, set_proceed_character, args=[character, goal_y, 10, lock])
		tsc2.start()
	
	
	# 光源を動かす
	delay += 6
	sun_pos_x += 300
	goal_pos = [sun_pos_x, 0, sun_pos_z]
	tsp5 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 50, lock])
	tsp5.start()
	
	# 光源を動かす
	delay += 5
	sun_pos_z += 280
	goal_pos = [sun_pos_x, 0, sun_pos_z]
	tsp6 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 70, lock])
	tsp6.start()
	
	# 光源を動かす
	delay += 6
	sun_pos_x += -400
	goal_pos = [sun_pos_x, 0, sun_pos_z]
	tsp7 = threading.Timer(
		delay, set_proceed_sphere, args=[sun, goal_pos, 50, lock])
	tsp7.start()
	
	# 文字を動かす
	charcters = [
		char_Kiseisen_Ki, char_Kiseisen_Sei, char_Kiseisen_Sen]
	goal_y = 2300
	delay += 3
	for character in charcters:
		tsc3 = threading.Timer(
			delay, set_proceed_character, args=[character, goal_y, 10, lock])
		tsc3.start()
	
	td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
	td.start()
	
	
