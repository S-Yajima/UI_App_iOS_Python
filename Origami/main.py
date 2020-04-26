import ui
import threading
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from figure import *


class Origami():
    # 折り紙のパーツの三角形の配列
    # triangles = [Triangle,Triangle,...]

    face_color = 'red'
    back_color = 'yellow'

    def __init__(self):
        # 折り紙のパーツの三角形の配列
        self.triangles = []
        # 折り紙を折る工程が終了済の場合:True
        self.is_finish_fold = False

    def add_triangle(self, triangle):
        if isinstance(triangle, Triangle) is True:
            self.triangles.append(triangle)


# 背景と床を描画する
class BaseView(ui.View):
    screen_depth = 400  # 視点から投影面までの距離

    light_x = 0
    light_y = 150
    light_z = 1000

    origamis = []

    def add_origami(self, origami):
        if isinstance(origami, Origami) is True:
            self.origamis.append(origami)

    def set_surface(self, surface):
        self.surface = surface

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

    # 色を表す文字列と内積の値からuiにRGBの値を設定する
    def set_ui_color(self, color, inner):
        value = abs(inner)
        if color == 'blue':
            ui.set_color((0.3, 0.3, value, 1.0))
        elif color == 'darkblue':
            ui.set_color((0.3, 0.3, value - 0.2, 1.0))
        elif color == 'green':
            ui.set_color((0.3, value, 0.3, 1.0))
        elif color == 'red':
            ui.set_color((value, 0.0, 0.0, 1.0))
        elif color == 'yellow':
            ui.set_color((value, value, 0.3, 1.0))
        elif color == 'brown':
            ui.set_color((value - 0.3, value - 0.8, value - 0.8, 1.0))
        elif color == 'silver':
            ui.set_color((value - 0.05, value - 0.05, value - 0.05, 1.0))
        elif color == 'black':
            ui.set_color((value - 0.7, value - 0.7, value - 0.7, 1.0))
        elif color == 'orange':
            ui.set_color((value, value - 0.2, 0.2, 1.0))
        else:
            ui.set_color((0.0, 0.0, 0.0, 1.0))

    # sort
    def sort_triangle(self, triangle):
        a_x, a_y, a_z = triangle.corner_A()
        b_x, b_y, b_z = triangle.corner_B()
        c_x, c_y, c_z = triangle.corner_C()

        # 視点焦点までのベクトルを算出する
        scr_vector = [
            self.width / 2 - (a_x + b_x + c_x) / 3,
            self.height / 2 - (a_y + b_y + c_y) / 3,
            self.screen_depth - (a_z + b_z + c_z) / 3]

        length = sqrt(
            scr_vector[0] ** 2 + scr_vector[1] ** 2 + \
            scr_vector[2] ** 2)
        # print(length)
        return length

    def sort_origami(self, origami):
        triangle = origami.triangles[10]
        a_x, a_y, a_z = triangle.corner_A()
        b_x, b_y, b_z = triangle.corner_B()
        c_x, c_y, c_z = triangle.corner_C()
        # 視点焦点までのベクトルを算出する
        scr_vector = [
            self.width / 2 - (a_x + b_x + c_x) / 3,
            self.height / 2 - (a_y + b_y + c_y) / 3,
            self.screen_depth - (a_z + b_z + c_z) / 3]

        length = sqrt(
            scr_vector[0] ** 2 + scr_vector[1] ** 2 + \
            scr_vector[2] ** 2)
        # print(length)
        return length

    # 描画
    def draw(self):
        # 水面
        if not self.surface is None:
            surface = self.surface
            a_x, a_y, a_z = surface.corner_A()
            b_x, b_y, b_z = surface.corner_B()
            c_x, c_y, c_z = surface.corner_C()
            d_x, d_y, d_z = surface.corner_D()

            a_x, a_y = self.projection(a_x, a_y, a_z)
            b_x, b_y = self.projection(b_x, b_y, b_z)
            c_x, c_y = self.projection(c_x, c_y, c_z)
            d_x, d_y = self.projection(d_x, d_y, d_z)

            path_s = ui.Path()
            path_s.move_to(a_x, a_y)
            path_s.line_to(b_x, b_y)
            path_s.line_to(c_x, c_y)
            path_s.line_to(d_x, d_y)
            path_s.line_to(a_x, a_y)

            ui.set_color(surface.color)
            path_s.fill()

        # 折り紙
        sorted_origamis = sorted(self.origamis, key=self.sort_origami, reverse=True)

        for origami in sorted_origamis:
            if isinstance(origami, Origami) is False:
                continue

            # 近くにあるポリゴンを、後で描画出来るようにソートする
            sorted_triangles = sorted(origami.triangles, key=self.sort_triangle, reverse=True)

            # 折り紙のパーツの描画を行う
            for triangle in sorted_triangles:
                if isinstance(triangle, Triangle) is False:
                    continue

                a_x, a_y, a_z = triangle.corner_A()
                b_x, b_y, b_z = triangle.corner_B()
                c_x, c_y, c_z = triangle.corner_C()

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
                    self.width / 2 - (a_x + b_x + c_x) / 3,
                    self.height / 2 - (a_y + b_y + c_y) / 3,
                    self.screen_depth - (a_z + b_z + c_z) / 3]
                scr_normal = normalize(scr_vector)
                scr_inner = dot_product(triangle_normal, scr_normal)

                # 折り紙が完成している and 折り紙の表面を向いてるパーツ(隠れて表示されないはずのパーツ)は表示しない
                if origami.is_finish_fold is True and \
                        scr_inner < 0.0:
                    continue

                p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
                p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
                p_c_x, p_c_y = self.projection(c_x, c_y, c_z)

                path_t = ui.Path()
                path_t.move_to(p_a_x, p_a_y)
                path_t.line_to(p_b_x, p_b_y)
                path_t.line_to(p_c_x, p_c_y)
                path_t.line_to(p_a_x, p_a_y)

                # 光源までのベクトルを算出する
                light_vector = [
                    self.light_x - (a_x + b_x + c_x) / 3,
                    self.light_y - (a_y + b_y + c_y) / 3,
                    self.light_z - (a_z + b_z + c_z) / 3]
                light_normal = normalize(light_vector)
                light_inner = dot_product(triangle_normal, light_normal)

                # 表裏判別し、描画色を設定する
                if scr_inner < 0.0:
                    self.set_ui_color(origami.face_color, light_inner)
                else:
                    self.set_ui_color(origami.back_color, light_inner)
                path_t.fill()


# 全ての折り紙をy軸(水平)に回転する
# angle から goal_angle まで　2.5°ずつ回転する
# angleがgoal_angleの角度に到達するまで繰返し呼ばれる
def rotate_origami_schedule(main_view, angle, goal_angle, lock):
    lock.acquire()

    if isinstance(main_view, BaseView) is False:
        return

    angle += 2.5
    if angle >= goal_angle:
        angle = 0

    for origami in main_view.origamis:
        if isinstance(origami, Origami) is False:
            continue

        for triangle in origami.triangles:
            if isinstance(triangle, Triangle) is False:
                continue

            triangle.set_center(-10, 0, 25)
            triangle.rotate_angle_y += 2.5

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True and 0 < angle and angle < goal_angle:
        t = threading.Timer(0.02, rotate_origami_schedule, args=[main_view, angle, goal_angle, lock])
        t.start()


# 完成した風車をz軸に回転させる
# 回転角度のメンバ変数ではなく、頂点座標を変更する
# ↑ y軸に水平回転しながら風車を回転させながら
# 影響を与えず同時にz軸に回転させるために上記採用した
def rotate_z_schedule(main_view, origami, lock):
    lock.acquire()

    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(origami, Origami) is False:
        return

    angle = -2.5

    for triangle in origami.triangles:
        if isinstance(triangle, Triangle) is False:
            continue

        triangle.move(0, 0, angle, -10, -10, 0)

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.02, rotate_z_schedule, args=[main_view, origami, lock])
        t.start()


# 折り紙を折る手順 1
# angle 紙を折った角度。
# 関数を繰り返し呼ぶ度に更新した値を入力する
def fold_origami_1_schedule(main_view, origami, angle, lock):
    lock.acquire()

    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(origami, Origami) is False:
        return
    if len(origami.triangles) < 22:
        return

    angle += 5
    right_indexes = [15, 16, 17, 18, 19, 20, 21]
    left_indexes = [0, 1, 2, 3, 4, 5, 6]

    for index in right_indexes:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(0, -5, 0, -15, 0, 0)

    for index in left_indexes:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(0, 5, 0, -5, 0, 0)

    if angle == 0 or angle >= 180:
        add_z = 0.3
        for index in right_indexes:
            triangle = origami.triangles[index]
            triangle.A_z += add_z
            triangle.B_z += add_z
            triangle.C_z += add_z

        for index in left_indexes:
            triangle = origami.triangles[index]
            triangle.A_z += add_z
            triangle.B_z += add_z
            triangle.C_z += add_z

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True and 0 < angle and angle < 180:
        t = threading.Timer(0.04, fold_origami_1_schedule, args=[main_view, origami, angle, lock])
        t.start()


# 折り紙を折る手順 2
# angle 紙を折った角度。
# 関数を繰り返し呼ぶ度に更新した値を入力する
def fold_origami_2_schedule(
        main_view, origami, angle, lock):
    lock.acquire()

    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(origami, Origami) is False:
        return
    if len(origami.triangles) < 22:
        return

    angle += 5

    # パーツの回転速度の違いを擬似的に算出する
    x_adjust_angle = 150 / 18
    if angle > 90:
        x_adjust_angle = 30 / 18

    for index in [12, 13, 14]:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(5, 0, 0, 0, -15, 0)

    for index in [4, 5]:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(0, 0, 45, -5, -15, 0)
        triangle.move(x_adjust_angle, 0, 0, 0, -15, 0)
        triangle.move(0, 0, -45, -5, -15, 0)

    if isinstance(origami.triangles[6], Triangle) is True:
        origami.triangles[6].B_x = origami.triangles[5].B_x
        origami.triangles[6].B_y = origami.triangles[5].B_y
        origami.triangles[6].B_z = origami.triangles[5].B_z

        origami.triangles[6].C_x = origami.triangles[12].B_x
        origami.triangles[6].C_y = origami.triangles[12].B_y
        origami.triangles[6].C_z = origami.triangles[12].B_z

    for index in [19, 20]:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue

        triangle.move(0, 0, -45, -15, -15, 0)
        triangle.move(x_adjust_angle, 0, 0, 0, -15, 0)
        triangle.move(0, 0, 45, -15, -15, 0)

    if isinstance(origami.triangles[21], Triangle) is True:
        origami.triangles[21].B_x = origami.triangles[14].C_x
        origami.triangles[21].B_y = origami.triangles[14].C_y
        origami.triangles[21].B_z = origami.triangles[14].C_z

        origami.triangles[21].C_x = origami.triangles[20].B_x
        origami.triangles[21].C_y = origami.triangles[20].B_y
        origami.triangles[21].C_z = origami.triangles[20].B_z

    for index in [7, 8, 9]:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(-5, 0, 0, 0, -5, 0)

    for index in [1, 2]:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(0, 0, -45, -5, -5, 0)
        triangle.move(-1 * x_adjust_angle, 0, 0, 0, -5, 0)
        triangle.move(0, 0, 45, -5, -5, 0)

    if isinstance(origami.triangles[0], Triangle) is True:
        origami.triangles[0].A_x = origami.triangles[1].A_x
        origami.triangles[0].A_y = origami.triangles[1].A_y
        origami.triangles[0].A_z = origami.triangles[1].A_z

        origami.triangles[0].C_x = origami.triangles[7].A_x
        origami.triangles[0].C_y = origami.triangles[7].A_y
        origami.triangles[0].C_z = origami.triangles[7].A_z

    for index in [16, 17]:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue
        triangle.move(0, 0, 45, -15, -5, 0)
        triangle.move(-1 * x_adjust_angle, 0, 0, 0, -5, 0)
        triangle.move(0, 0, -45, -15, -5, 0)

    if isinstance(origami.triangles[15], Triangle) is True:
        origami.triangles[15].A_x = origami.triangles[9].C_x
        origami.triangles[15].A_y = origami.triangles[9].C_y
        origami.triangles[15].A_z = origami.triangles[9].C_z

        origami.triangles[15].C_x = origami.triangles[16].A_x
        origami.triangles[15].C_y = origami.triangles[16].A_y
        origami.triangles[15].C_z = origami.triangles[16].A_z

    if angle == 0 or angle >= 180:
        add_z = 0.3
        indexes = [0, 1, 2, 7, 8, 9, 15, 16, 17, 5, 6, 12, 13, 14, 20, 21]
        for index in indexes:
            triangle = origami.triangles[index]
            triangle.A_z += add_z
            triangle.B_z += add_z
            triangle.C_z += add_z

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True and 0 < angle and angle < 180:
        t = threading.Timer(0.04, fold_origami_2_schedule, args=[main_view, origami, angle, lock])
        t.start()


# 折り紙を折る手順 3
# angle 紙を折った角度。
# 関数を繰り返し呼ぶ度に更新した値を入力する
def fold_origami_3_schedule(main_view, origami, angle, lock):
    lock.acquire()

    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(origami, Origami) is False:
        return
    if len(origami.triangles) < 22:
        return

    angle += 5

    indexes_1 = [0, 1, 2, 7]
    for index in indexes_1:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue

        triangle.move(0, 0, -45, -5, -5, 0)
        triangle.move(5, 0, 0, 0, -5, 0)
        triangle.move(0, 0, 45, -5, -5, 0)

    indexes_2 = [14, 19, 20, 21]
    for index in indexes_2:
        triangle = origami.triangles[index]
        if isinstance(triangle, Triangle) is False:
            continue

        triangle.move(0, 0, -45, -15, -15, 0)
        triangle.move(-5, 0, 0, 0, -15, 0)
        triangle.move(0, 0, 45, -15, -15, 0)

    if angle == 0 or angle >= 180:
        add_z = 0.3
        for index in [0, 1, 2, 7, 14, 19, 20, 21]:
            triangle = origami.triangles[index]
            triangle.A_z += add_z
            triangle.B_z += add_z
            triangle.C_z += add_z
        origami.is_finish_fold = True

        t = threading.Timer(3, rotate_z_schedule, args=[main_view, origami, lock])
        t.start()

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True and 0 < angle and angle < 180:
        t = threading.Timer(0.04, fold_origami_3_schedule, args=[main_view, origami, angle, lock])
        t.start()


# y軸に回転してる起動をz軸に少しずつずらす
def displacing_z_angle_schedule(main_view, lock):
    lock.acquire()

    if isinstance(main_view, BaseView) is False:
        return

    angle = 0.5

    for origami in main_view.origamis:
        if isinstance(origami, Origami) is False:
            continue

        for triangle in origami.triangles:
            if isinstance(triangle, Triangle) is False:
                continue

            triangle.rotate_angle_z += angle

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.02, displacing_z_angle_schedule, args=[main_view, lock])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '折り紙_風車'
    main_view.background_color = 'lightblue'

    # 水面
    surface = Square(0, 0, 0, 0, 300, 0, 400, 300, 0, 400, 0, 0)
    surface.set_center(0, 0, 0)
    surface.set_shift(-12, 550, 0)
    surface.set_scale(1)
    surface.set_angle_x(270)
    main_view.set_surface(surface)

    # 三角形座標の配列
    triangle_points = [
        [0, 0, 0, 5, 5, 0, 5, 0, 0],  # 0
        [0, 0, 0, 0, 5, 0, 5, 5, 0],
        [0, 5, 0, 0, 10, 0, 5, 5, 0],
        [5, 5, 0, 0, 10, 0, 5, 15, 0],
        [0, 10, 0, 0, 15, 0, 5, 15, 0],
        [0, 15, 0, 0, 20, 0, 5, 15, 0],
        [5, 15, 0, 0, 20, 0, 5, 20, 0],  # 6
        [5, 0, 0, 5, 5, 0, 10, 0, 0],  # 7
        [10, 0, 0, 5, 5, 0, 15, 5, 0],
        [10, 0, 0, 15, 5, 0, 15, 0, 0],  # 9
        [5, 5, 0, 5, 15, 0, 15, 5, 0],  # 10
        [15, 5, 0, 5, 15, 0, 15, 15, 0],  # 11
        [5, 15, 0, 5, 20, 0, 10, 20, 0],  # 12
        [5, 15, 0, 10, 20, 0, 15, 15, 0],
        [15, 15, 0, 10, 20, 0, 15, 20, 0],  # 14
        [15, 0, 0, 15, 5, 0, 20, 0, 0],  # 15
        [20, 0, 0, 15, 5, 0, 20, 5, 0],
        [15, 5, 0, 20, 10, 0, 20, 5, 0],
        [15, 5, 0, 15, 15, 0, 20, 10, 0],
        [20, 10, 0, 15, 15, 0, 20, 15, 0],
        [15, 15, 0, 20, 20, 0, 20, 15, 0],
        [15, 15, 0, 15, 20, 0, 20, 20, 0],  # 21
    ]

    scale_value = 8
    init_x = 13.43
    init_y = 21.68
    center_z = 25

    # 折り紙を生成
    origami_1 = Origami()
    for point in triangle_points:
        triangle = Triangle(point[0], point[1], point[2],
                            point[3], point[4], point[5],
                            point[6], point[7], point[8])
        triangle.set_scale(scale_value)
        triangle.set_shift(init_x, init_y, 0)
        origami_1.add_triangle(triangle)
    main_view.add_origami(origami_1)

    origami_2 = Origami()
    origami_2.face_color = 'orange'
    origami_2.back_color = 'blue'
    for point in triangle_points:
        triangle = Triangle(point[0], point[1], point[2],
                            point[3], point[4], point[5],
                            point[6], point[7], point[8])
        triangle.set_scale(scale_value)
        triangle.set_center(-10, 0, center_z)
        triangle.set_angle_y(240)
        triangle.set_shift(init_x, init_y, 0)
        origami_2.add_triangle(triangle)
    main_view.add_origami(origami_2)

    origami_3 = Origami()
    origami_3.face_color = 'silver'
    origami_3.back_color = 'green'
    for point in triangle_points:
        triangle = Triangle(point[0], point[1], point[2],
                            point[3], point[4], point[5],
                            point[6], point[7], point[8])
        triangle.set_scale(scale_value)
        triangle.set_center(-10, 0, center_z)
        triangle.set_angle_y(120)
        triangle.set_shift(init_x, init_y, 0)
        origami_3.add_triangle(triangle)
    main_view.add_origami(origami_3)

    main_view.present()

    # タイマー処理を設定する
    lock = threading.Lock()

    delay = 1
    t1 = threading.Timer(delay, rotate_origami_schedule, args=[main_view, 0, 360, lock])
    t1.start()

    delay += 7
    t2 = threading.Timer(delay, fold_origami_1_schedule, args=[main_view, origami_1, 0, lock])
    t2.start()

    delay += 4
    t3 = threading.Timer(delay, fold_origami_2_schedule, args=[main_view, origami_1, 0, lock])
    t3.start()

    delay += 4
    t4 = threading.Timer(delay, fold_origami_3_schedule, args=[main_view, origami_1, 0, lock])
    t4.start()

    delay += 7
    t5 = threading.Timer(delay, rotate_origami_schedule, args=[main_view, 0, 480, lock])
    t5.start()

    delay += 9
    t6 = threading.Timer(delay, fold_origami_1_schedule, args=[main_view, origami_2, 0, lock])
    t6.start()

    delay += 4
    t7 = threading.Timer(delay, fold_origami_2_schedule, args=[main_view, origami_2, 0, lock])
    t7.start()

    delay += 4
    t8 = threading.Timer(delay, fold_origami_3_schedule, args=[main_view, origami_2, 0, lock])
    t8.start()

    delay += 7
    t9 = threading.Timer(delay, rotate_origami_schedule, args=[main_view, 0, 10000, lock])
    t9.start()

    delay += 7
    t10 = threading.Timer(delay, fold_origami_1_schedule, args=[main_view, origami_3, 0, lock])
    t10.start()

    delay += 4
    t11 = threading.Timer(delay, fold_origami_2_schedule, args=[main_view, origami_3, 0, lock])
    t11.start()

    delay += 4
    t12 = threading.Timer(delay, fold_origami_3_schedule, args=[main_view, origami_3, 0, lock])
    t12.start()

    delay += 10
    t13 = threading.Timer(delay, displacing_z_angle_schedule, args=[main_view, lock])
    t13.start()

