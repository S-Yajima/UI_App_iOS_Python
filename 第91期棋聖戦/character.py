from figure import *
from glyph import *

# Glyph Point Type
class TYPE():
	LINE = 'line'
	CURVE = 'curve'
	CONTROL = 'control'


# 文字
class Character(MyFigure):
	# points 座標の配列 [[[x,y,z,'type',flag],[x,y,z],...]]
	
	def __init__(self, contours):
		super().__init__()
		# 法線ベクトル取得の為の座標
		self.min_x = 0
		self.min_y = 0
		self.max_x = 100
		self.max_y = 100
		# 基本的なz座標は下記の値とする
		#self.default_z = 0
		self.default_z = 0
		
		self.base_points = []
		for contour in contours:
			points = []
			for point in contour:
				work_list = []
				work_list.append(point[0])	# x座標
				work_list.append(point[1])	# y座標
				work_list.append(self.default_z)
				work_list.append(point[2])	# line/curve/control
				work_list.append(True)			# 表示/非表示
				points.append(work_list)
				
				# 法線ベクトルを取得するための最大、最小のx、y座標を更新する
				if point[0] < self.min_x:
					self.min_x = point[0]
				if point[0] > self.max_x:
					self.max_x = point[0]
				if point[1] < self.min_y:
					self.min_y = point[1]
				if point[1] > self.max_y:
					self.max_y = point[1]
				
			self.base_points.append(points)
		
		self.name_string = ''
		self.name_x = 0
		self.name_y = 0
		self.is_enable_name = False


	def set_name_string(self, name_string, name_x, name_y):
		self.name_string = name_string
		self.name_x = name_x
		self.name_y = name_y


	def set_enable_name(self, flag):
		self.is_enable_name = flag

	
	# 法線ベクトルを取得するためのxyz座標を返す
	# 従来ならA→B→Cが半時計周りで表が見えるよう設定するが、
	# 使用中のglyphのy座標が上下逆の数値であるため、
	# 時計周りで面になるような配列の並びを返している。
	def point_for_vector(self, screen_height):
		a_x, a_y, a_z = self.queue(
			self.min_x, self.max_y, self.default_z)
		# スクリーンとglyphのy座標の上下の違いを吸収する
		a_y = screen_height - a_y
		
		b_x, b_y, b_z = self.queue(
			self.min_x, self.min_y, self.default_z)
		b_y = screen_height - b_y
		
		c_x, c_y, c_z = self.queue(
			self.max_x, self.max_y, self.default_z)
		c_y = screen_height - c_y
	
		return [[a_x, a_y, a_z], [b_x, b_y, b_z], [c_x, c_y, c_z]]
	
	
	# 文字の描画のための3D座標を返す
	def glyph(self, screen_height):
		r_points = []
		
		for contours in self.base_points:
			points = []
			for point in contours:
				x, y, z = self.queue(point[0], point[1], point[2])
				
				# glyphデータのy座標とViewのy座標は
				# 上下逆転しているので吸収する
				y = screen_height - y
				
				points.append([x, y, z, point[3], point[4]])
			r_points.append(points)

		return r_points
		

