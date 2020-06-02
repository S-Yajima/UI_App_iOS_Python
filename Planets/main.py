import ui
import threading
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from figure import *


# 太陽。球を継承して別クラスとして扱う
class MySun(Sphere):
    brightness = 20000
    pass


# 床。タイルにする。
class MyFloor():
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
    screen_depth = 400  # 視点から投影面までの距離

    # 床
    froor = None

    # 球
    spheres = []
    sun = None

    # camera vector
    camera_x = 0  # カメラの位置座標
    camera_y = 0
    camera_z = 0
    lookat_x = 0  # カメラの注視点
    lookat_y = 0
    lookat_z = 0
    CXV = []  # カメラ座標のXYZ軸ベクトル
    CYV = []
    CZV = []
    CPX = 0  # カメラ座標とカメラX軸との内積
    CPY = 0
    CPZ = 0

    # camera vector

    # 球を追加する
    def add_sphere(self, sphere):
        if isinstance(sphere, Sphere) is True:
            self.spheres.append(sphere)

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
        CXV = self.CXV  # ビュー座標のxyz軸ベクトル
        CYV = self.CYV
        CZV = self.CZV

        if len(CXV) != 3 or len(CYV) != 3 or len(CZV) != 3:
            return (x, y, z)

        CPX = self.CPX  # カメラ移動計算用の内積
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

    # sort
    # ビュー変換後の座標で、視点からの距離の値を比較しソートを行う
    def sort_triangle(self, corners):
        a_x, a_y, a_z = (corners[0][0], corners[0][1], corners[0][2])
        b_x, b_y, b_z = (corners[1][0], corners[1][1], corners[1][2])
        c_x, c_y, c_z = (corners[2][0], corners[2][1], corners[2][2])

        # 視点焦点までのベクトルを算出する
        scr_vector = [
            0 - (a_x + b_x + c_x) / 3,
            0 - (a_y + b_y + c_y) / 3,
            self.screen_depth - (a_z + b_z + c_z) / 3]
        length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

        return length

    # 球のソート
    def sort_sphere(self, sphere):
        c_x, c_y, c_z = self.camera_rotation(
            sphere.center[0], sphere.center[1], sphere.center[2])

        # 視点焦点までのベクトルを算出する
        scr_vector = [
            0 - c_x,
            0 - c_y,
            self.screen_depth - c_z]

        length = scr_vector[0] ** 2 + scr_vector[1] ** 2 + scr_vector[2] ** 2

        return length

    # 内積の値cosθと光源との距離からuiにRGBの値を設定する
    # light_inner : 光源との角度(cosθ)
    # 1=0度, 0=90度, -1=180度, 0=270度
    # light_length : 光源との距離の二乗
    # 入光する光の色は白(1.0,1.0,1.0)を前提とする
    def set_ui_color(self, color, light_inner, light_length, brightness=60000):
        # (光源光量 * cosθ) / 距離の二乗
        value = (-1 * brightness * light_inner) / light_length
        # print(value)

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
        elif color == 'black':
            # ui.set_color('black')
            r_ref, g_ref, b_ref = (0.0, 0.0, 0.0)
        elif color == 'orange':
            # ui.set_color((value, value-0.2, 0.2, 1.0))
            r_ref, g_ref, b_ref = (1.0, 0.8, 0.1)

        ui.set_color((r_ref * value, g_ref * value, b_ref * value, 1.0))

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

    # 三角関数の数値
    def trigono_value(self, triangle):
        rad_x = radians(triangle.rotate_angle_x)
        rad_y = radians(triangle.rotate_angle_y)
        rad_z = radians(triangle.rotate_angle_z)

        return (cos(rad_x), cos(rad_y), cos(rad_z), sin(rad_x), sin(rad_y), sin(rad_z))

    # 描画
    def draw(self):

        # 光源
        light_x, light_y, light_z = self.light_point()
        light_x, light_y, light_z = self.camera_rotation(light_x, light_y, light_z)

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

                # 光源までの距離の二乗
                light_distance = light_vector[0] ** 2 + light_vector[1] ** 2 + light_vector[2] ** 2
                # 透視投影
                p_a_x, p_a_y = self.projection(a_x, a_y, a_z)
                p_b_x, p_b_y = self.projection(b_x, b_y, b_z)
                p_c_x, p_c_y = self.projection(c_x, c_y, c_z)
                p_d_x, p_d_y = self.projection(d_x, d_y, d_z)
                # 床を描画
                path_t = ui.Path()
                path_t.move_to(p_a_x, p_a_y)
                path_t.line_to(p_b_x, p_b_y)
                path_t.line_to(p_c_x, p_c_y)
                path_t.line_to(p_d_x, p_d_y)
                path_t.line_to(p_a_x, p_a_y)
                # 描画色を設定する
                if scr_inner < 0.0:
                    self.set_ui_color('blue', light_inner, light_distance, self.sun.brightness)
                path_t.fill()

        # 球の座標をビュー座標に変換し配列に格納する
        # 太陽と惑星を含めた球体
        all_spheres = self.spheres + [sun]
        # 球体をソートする
        sorted_spheres = sorted(all_spheres, key=self.sort_sphere, reverse=True)

        for sphere in sorted_spheres:
            triangles = []

            # 三角関数の値を予め取得。
            # 結果が同じ値のcos,sin処理の繰り返しを避ける為。
            cos_x, cos_y, cos_z, sin_x, sin_y, sin_z = self.trigono_value(sphere.triangles[0])
            # ビュー座標を配列に格納
            for triangle in sphere.triangles:
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
                    light_x - (a_x + b_x + c_x) / 3,
                    light_y - (a_y + b_y + c_y) / 3,
                    light_z - (a_z + b_z + c_z) / 3]
                light_normal = normalize(light_vector)
                # 光源との角度を算出する
                light_inner = dot_product(triangle_normal, light_normal)

                # 光源までの距離の二乗
                light_distance = light_vector[0] ** 2 + light_vector[1] ** 2 + light_vector[2] ** 2

                # 表裏判別し、描画色を設定する
                if scr_inner < 0.0:
                    if isinstance(sphere, MySun) is True:
                        ui.set_color('white')  # 太陽の場合は明るい白で固定
                    else:
                        self.set_ui_color(sphere.face_color, light_inner, light_distance, self.sun.brightness)
                else:
                    self.set_ui_color(sphere.back_color, light_inner, light_distance, self.sun.brightness)
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
    # main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True and isclose(angle, goal_angle) is False:
        t = threading.Timer(0.02, change_view_round_schedule, args=[main_view, angle, goal_angle, lock])
        t.start()


# 球を動かす設定を行い動かすタイマーメソッドを呼び出す
def move_sphere_setting_schedule(main_view, sphere, goal_pos, speed, lock):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(sphere, Sphere) is False:
        return

    lock.acquire()

    # これから移動する総量のベクトル
    move_vec3 = [
        goal_pos[0] - sphere.center[0],
        goal_pos[1] - sphere.center[1],
        goal_pos[2] - sphere.center[2]]
    # 正規化
    move_normal = normalize(move_vec3)
    # 目的地に向かって進むベクトルを算出
    proceed_vec3 = [
        move_normal[0] * speed,
        move_normal[1] * speed,
        move_normal[2] * speed]
    # 球体の進行ベクトルを設定する
    sphere.proceed_vector = proceed_vec3

    lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.02, move_sphere_schedule, args=[main_view, sphere, goal_pos, lock])
        t.start()


# 球を動かす設定を行い動かすタイマーメソッドを呼び出す
def move_sphere_schedule(main_view, sphere, goal_pos, lock):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(sphere, Sphere) is False:
        return

    lock.acquire()

    # 進行ベクトルの長さを算出
    proceed_length = sphere.proceed_vector[0] ** 2 + sphere.proceed_vector[1] ** 2 + sphere.proceed_vector[2] ** 2

    # 目的地までの長さを算出
    move_vec3 = [
        goal_pos[0] - sphere.center[0],
        goal_pos[1] - sphere.center[1],
        goal_pos[2] - sphere.center[2]]
    move_length = move_vec3[0] ** 2 + move_vec3[1] ** 2 + move_vec3[2] ** 2

    # 進行ベクトルの長さが目的地までの長さと
    # 同じか大きい場合
    is_goal = False
    if proceed_length >= move_length:
        sphere.set_center(goal_pos[0], goal_pos[1], goal_pos[2])
        sphere.proceed_vector = [0, 0, 0]
        is_goal = True
    else:
        sphere.proceed()

    lock.release()

    if main_view.on_screen is True and is_goal is False:
        t = threading.Timer(0.02, move_sphere_schedule, args=[main_view, sphere, goal_pos, lock])
        t.start()


# 明るさを変更する
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


# 球を周回させる
# angle 太陽を中心とした周回位置の角度
# add_angle 角度の更新量
# r 周回半径
def round_sphere_schedule(main_view, sphere, angle, add_angle, r, lock):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(sphere, Sphere) is False:
        return
    if add_angle == 0:
        return

    lock.acquire()

    angle += add_angle
    if angle > 360 or angle < 0:
        angle %= 360

    x = cos(radians(angle)) * r + main_view.sun.center[0]
    y = sphere.center[1]
    z = sin(radians(angle)) * r + main_view.sun.center[2]
    sphere.set_center(x, y, z)

    lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.02, round_sphere_schedule, args=[main_view, sphere, angle, add_angle, r, lock])
        t.start()


# 全部の球を回す(スピン)
def spin_all_sphere(main_view):
    if isinstance(main_view, BaseView) is False:
        return

    main_view.sun.spin()
    for sphere in main_view.spheres:
        sphere.spin()


# 再描画処理
def display_schedule(main_view, lock):
    if isinstance(main_view, BaseView) is False:
        return

    # lock.acquire()
    spin_all_sphere(main_view)
    main_view.set_needs_display()
    # lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.012, display_schedule, args=[main_view, lock])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '天体'
    # main_view.background_color = 'lightblue'
    # main_view.background_color = 'black'
    main_view.background_color = '#000080'

    # カメラの位置
    main_view.set_camera_position(0, 0, 200)
    # カメラの注視点
    main_view.set_lookat_position(0, 0, -250)
    # ビュー座標の軸を生成する
    main_view.set_camera_coodinate_vector()

    # 床
    floor = MyFloor(-420, 200, 150)
    main_view.set_floor(floor)

    # 1つ目の球(太陽)
    sun = MySun(50, is_hide=False)
    sun.set_center(0, -300, -250)
    sun.face_color = 'white'
    main_view.sun = sun

    # 球2
    sphere_2 = Sphere(50, is_hide=False)
    sphere_2.set_center(-200, 0, -250)
    sphere_2.face_color = 'blue'
    main_view.add_sphere(sphere_2)

    # 球3
    sphere_3 = Sphere(50, is_hide=False)
    sphere_3.set_center(300, 0, -250)
    sphere_3.face_color = 'red'
    main_view.add_sphere(sphere_3)

    # 球4
    sphere_4 = Sphere(50, is_hide=False)
    sphere_4.set_center(-400, 0, -250)
    sphere_4.face_color = 'orange'
    main_view.add_sphere(sphere_4)

    # 球5
    sphere_5 = Sphere(50, is_hide=False)
    sphere_5.set_center(500, 0, -250)
    sphere_5.face_color = 'white'
    main_view.add_sphere(sphere_5)
    main_view.present()

    # タイマー処理を設定する
    lock = threading.Lock()

    # 一つ目の球
    delay = 1.0

    # 球を動かす(下)
    tm1 = threading.Timer(delay, move_sphere_setting_schedule, args=[main_view, sun, [0, 0, -250], 5, lock])
    tm1.start()

    # 太陽の明るさを変える
    delay += 8.0
    tb1 = threading.Timer(delay, change_bright_schedule, args=[main_view, sun, 80000, 2000, lock])
    tb1.start()

    # 球2を周回させる
    delay += 3.0
    tr1 = threading.Timer(delay, round_sphere_schedule, args=[main_view, sphere_2, 180, 1, 200, lock])
    tr1.start()

    # 球3を周回させる
    delay += 10.0
    tr2 = threading.Timer(delay, round_sphere_schedule, args=[main_view, sphere_3, 0, -0.5, 300, lock])
    tr2.start()

    # 球4を周回させる
    delay += 10.0
    tr3 = threading.Timer(delay, round_sphere_schedule, args=[main_view, sphere_4, 180, 0.5, 400, lock])
    tr3.start()

    # 視点移動　上昇
    delay += 0.5
    tv1 = threading.Timer(delay, change_view_y_schedule, args=[main_view, -200, -4, lock])
    tv1.start()

    # 球5を周回させる
    delay += 10.0
    tr4 = threading.Timer(delay, round_sphere_schedule, args=[main_view, sphere_5, 0, -0.2, 500, lock])
    tr4.start()

    # 視点移動　周回
    delay += 0.5
    tv2 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 90 + 360, lock])
    tv2.start()

    td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
    td.start()


