from figure import *
from dot_data import *
import ui
from math import sqrt


# 世界地図のクラス
# ドット絵で地図を表現する
class MyMap(MyFigure):
    # ドット一つの幅と高さ
    dot_size = 5
    # ドット一つの隙間
    dot_gap = 1
    # z軸のデフォルト座標
    dot_z = 1

    # ドットの色を表す二次元配列
    # [['#bcbcff', '#ffc8c8', None,...],
    #  ['#bcbcff', '#ffc8c8', None,...], ...
    def __init__(self, dots):
        self.dots = dots

    # 縦、横のインデックスから四辺の座標を二次元配列で返す
    # row, colmun
    # return [[A_x,A_y,A_x],[B_x,B_y,B_z],
    #					[C_x,C_y,C_x],[D_x,D_y,D_z]]
    def points(self, row, colmun):
        r_points = []

        if self.dots[row][colmun] is False:
            return None

        # A 左上
        a_x = (self.dot_size + self.dot_gap) * colmun
        a_y = (self.dot_size + self.dot_gap) * row
        a_z = self.dot_z
        # B 右上
        b_x = a_x + self.dot_size
        b_y = a_y
        b_z = a_z
        # C 右下
        c_x = b_x
        c_y = b_y + self.dot_size
        c_z = b_z
        # D 左下
        d_x = a_x
        d_y = c_y
        d_z = c_z

        # 3次元回転行列
        q_a_x, q_a_y, q_a_z = self.queue(a_x, a_y, a_z)
        q_b_x, q_b_y, q_b_z = self.queue(b_x, b_y, b_z)
        q_c_x, q_c_y, q_c_z = self.queue(c_x, c_y, c_z)
        q_d_x, q_d_y, q_d_z = self.queue(d_x, d_y, d_z)

        r_points.append([q_a_x, q_a_y, q_a_z])
        r_points.append([q_b_x, q_b_y, q_b_z])
        r_points.append([q_c_x, q_c_y, q_c_z])
        r_points.append([q_d_x, q_d_y, q_d_z])

        return r_points


class MyMapView(ui.View):
    screen_depth = 400  # 視点から投影面までの距離
    map = None

    is_enable_shadow = True
    # shadow_color = '#414141'
    shadow_color = 'gray'
    shadow_gap = 3

    # 光源座標
    light_x = 200
    light_y = 80
    light_z = 80

    def set_map(self, map):
        self.map = map

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
            r_x = ((depth / (z + depth)) * (x - center_x)) + center_x
            r_y = ((depth / (z + depth)) * (y - center_y)) + center_y

        return (r_x, r_y)

    # 表示中の図形の陰影を識別するためのベクトル内積を返す
    # 下記二つのベクトルを算出し、内積を計算する
    # ・三角形のABとACの外積
    # ・三角形からカメラ焦点のベクトル
    # 入力) 図形３つの頂点ABCのxyz座標
    # 出力) 内積[x,y,z]
    def dot_product(self, a_x, a_y, a_z,
                    b_x, b_y, b_z,
                    c_x, c_y, c_z):

        # 三角形の頂点Aから頂点Bへのベクトル(b - a)
        AB = [b_x - a_x, b_y - a_y, b_z - a_z]
        # 三角形の頂点Aから頂点Cへのベクトル(c - a)
        AC = [c_x - a_x, c_y - a_y, c_z - a_z]
        # ベクトルAB, AC の外積を求める
        cross_AB_AC = cross_product(AB, AC)
        # 法線ベクトルの正規化を実行する
        normal_AB_AC = normalize(cross_AB_AC)

        # 三角形の中心から光源へのベクトル
        light_vector = [
            self.light_x - (a_x + b_x + c_x) / 3,
            self.light_y - (a_y + b_y + c_y) / 3,
            self.light_z - (a_z + b_z + c_z) / 3]
        # 光源までのベクトルの正規化を行う
        normal_scr = normalize(light_vector)
        # 光源へのベクトルとAB,ACの外積との内積を求める
        return dot_product(normal_scr, normal_AB_AC)

    def draw(self):
        # map
        if not self.map is None:
            row_count = len(self.map.dots)
            col_count = len(self.map.dots[0])

            for row in range(row_count):
                for col in range(col_count):
                    points = self.map.points(row, col)

                    if points is None:
                        continue

                    p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
                    path_m = ui.Path()
                    path_s = None

                    if self.is_enable_shadow is True:
                        path_s = ui.Path()
                        path_s.move_to(p_x + self.shadow_gap, p_y + self.shadow_gap)

                    path_m.move_to(p_x, p_y)
                    for i in range(1, len(points)):
                        p_x, p_y = self.projection(points[i][0], points[i][1], points[i][2])

                        if self.is_enable_shadow is True:
                            path_s.line_to(p_x + self.shadow_gap, p_y + self.shadow_gap)

                        path_m.line_to(p_x, p_y)

                    p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])

                    if self.is_enable_shadow is True:
                        path_s.line_to(p_x + self.shadow_gap, p_y + self.shadow_gap)

                    path_m.line_to(p_x, p_y)

                    if self.is_enable_shadow is True:
                        ui.set_color(self.shadow_color)
                        path_s.fill()

                    inner = self.dot_product(
                        points[0][0], points[0][1], points[0][2],
                        points[3][0], points[3][1], points[3][2],
                        points[2][0], points[2][1], points[2][2]
                    )

                    ui.set_color((0.0, 0.0, (inner * -1) + 0.35, 1.0))
                    path_m.fill()



