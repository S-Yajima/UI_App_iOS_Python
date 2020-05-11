import ui
import threading
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from figure import *


# 背景と床を描画する
class BaseView(ui.View):
    screen_depth = 400  # 視点から投影面までの距離

    light_x = 500
    light_y = -500
    light_z = 1000

    # 床
    surface = None
    surface_V_n = []  # 床の法線

    # 天井
    ceiling = None
    ceiling_V_n = []  # 天井の法線

    # 壁
    left_wall_V_n = []  # 壁の法線
    right_wall_V_n = []
    front_wall_V_n = []
    back_wall_V_n = []

    # 球
    spheres = []

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

    def add_sphere(self, sphere):
        if isinstance(sphere, Sphere) is True:
            self.spheres.append(sphere)

    def set_surface(self, surface):
        if isinstance(surface, Square) is True:
            self.surface = surface

            a_x, a_y, a_z = surface.corner_A()
            b_x, b_y, b_z = surface.corner_B()
            c_x, c_y, c_z = surface.corner_C()
            d_x, d_y, d_z = surface.corner_D()

            # 床の法線
            AB_vector = [b_x - a_x, b_y - a_y, b_z - a_z]
            AC_vector = [c_x - a_x, c_y - a_y, c_z - a_z]
            surface_cross = cross_product(AC_vector, AB_vector)
            self.surface_V_n = normalize(surface_cross)

            # 左の壁の法線
            self.left_wall_V_n = normalize(
                cross_product(AB_vector, [0, -1, 0]))
            # 手間の壁の法線
            BC_vector = [b_x - c_x, b_y - c_y, b_z - c_z]
            self.front_wall_V_n = normalize(
                cross_product([0, -1, 0], BC_vector))
            # 右の壁の法線
            CD_vector = [c_x - d_x, c_y - d_y, c_z - d_z]
            self.right_wall_V_n = normalize(
                cross_product([0, -1, 0], CD_vector))
            # 奥の壁の法線
            AD_vector = [a_x - d_x, a_y - d_y, a_z - d_z]
            self.back_wall_V_n = normalize(
                cross_product(AD_vector, [0, -1, 0]))

    def set_ceiling(self, ceiling):
        if isinstance(ceiling, Square) is True:
            self.ceiling = ceiling

            a_x, a_y, a_z = ceiling.corner_A()
            b_x, b_y, b_z = ceiling.corner_B()
            c_x, c_y, c_z = ceiling.corner_C()
            d_x, d_y, d_z = ceiling.corner_D()

            # 床の法線
            AB_vector = [b_x - a_x, b_y - a_y, b_z - a_z]
            AC_vector = [c_x - a_x, c_y - a_y, c_z - a_z]
            ceiling_cross = cross_product(AB_vector, AC_vector)
            self.ceiling_V_n = normalize(ceiling_cross)

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

    #
    def draw_wall(self, wall):
        # 水面
        if isinstance(wall, Square) is True:
            surface = self.surface
            a_x, a_y, a_z = wall.corner_A()
            b_x, b_y, b_z = wall.corner_B()
            c_x, c_y, c_z = wall.corner_C()
            d_x, d_y, d_z = wall.corner_D()

            a_x, a_y, a_z = self.camera_rotation(a_x, a_y, a_z)
            b_x, b_y, b_z = self.camera_rotation(b_x, b_y, b_z)
            c_x, c_y, c_z = self.camera_rotation(c_x, c_y, c_z)
            d_x, d_y, d_z = self.camera_rotation(d_x, d_y, d_z)

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

            ui.set_color(wall.color)
            path_s.fill()

    # sort
    def sort_triangle(self, triangle):
        a_x, a_y, a_z = triangle.corner_A()
        b_x, b_y, b_z = triangle.corner_B()
        c_x, c_y, c_z = triangle.corner_C()

        a_x, a_y, a_z = self.camera_rotation(a_x, a_y, a_z)
        b_x, b_y, b_z = self.camera_rotation(b_x, b_y, b_z)
        c_x, c_y, c_z = self.camera_rotation(c_x, c_y, c_z)

        # 視点焦点までのベクトルを算出する
        scr_vector = [
            0 - (a_x + b_x + c_x) / 3,
            0 - (a_y + b_y + c_y) / 3,
            self.screen_depth - (a_z + b_z + c_z) / 3]

        length = sqrt(
            scr_vector[0] ** 2 + scr_vector[1] ** 2 + \
            scr_vector[2] ** 2)
        # print(length)
        return length

    def sort_sphere(self, sphere):
        c_x, c_y, c_z = self.camera_rotation(
            sphere.center[0], sphere.center[1], sphere.center[2])

        # 視点焦点までのベクトルを算出する
        scr_vector = [
            0 - c_x,
            0 - c_y,
            self.screen_depth - c_z]

        length = sqrt(
            scr_vector[0] ** 2 + scr_vector[1] ** 2 + \
            scr_vector[2] ** 2)
        # print(length)
        return length

    # 描画
    def draw(self):
        # 床や天井を描画する
        self.draw_wall(self.surface)
        self.draw_wall(self.ceiling)

        # 球
        sorted_spheres = sorted(self.spheres, key=self.sort_sphere, reverse=True)

        for sphere in sorted_spheres:

            sorted_triangles = sorted(sphere.triangles, key=self.sort_triangle, reverse=True)

            for triangle in sorted_triangles:
                if triangle.is_hide is True:
                    continue

                a_x, a_y, a_z = triangle.corner_A()
                b_x, b_y, b_z = triangle.corner_B()
                c_x, c_y, c_z = triangle.corner_C()

                a_x, a_y, a_z = self.camera_rotation(a_x, a_y, a_z)
                b_x, b_y, b_z = self.camera_rotation(b_x, b_y, b_z)
                c_x, c_y, c_z = self.camera_rotation(c_x, c_y, c_z)

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
                    self.light_x - (a_x + b_x + c_x) / 3,
                    self.light_y - (a_y + b_y + c_y) / 3,
                    self.light_z - (a_z + b_z + c_z) / 3]
                light_normal = normalize(light_vector)
                light_inner = dot_product(triangle_normal, light_normal)

                # 表裏判別し、描画色を設定する
                if scr_inner < 0.0:
                    self.set_ui_color(sphere.face_color, light_inner)
                else:
                    self.set_ui_color(sphere.back_color, light_inner)
                path_t.fill()


# カメラの位置上昇下降
def change_view_y_schedule(main_view, goal_y, add_y, lock):
    if isinstance(main_view, BaseView) is False:
        return

    lock.acquire()
    main_view.camera_y += add_y

    if abs(main_view.camera_y - goal_y) < add_y:
        main_view.camera_y = goal_y

    main_view.set_camera_coodinate_vector()

    # main_view.set_needs_display()

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


# 球を落とす
def fall_sphere_schedule(main_view, sphere, r_vector, lock):
    lock.acquire()
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(sphere, Sphere) is False:
        return
    if len(r_vector) < 3:
        r_vector = [-5, 3, -1]

    # 加速させる
    sphere.accel()

    # 床の法線ベクトル(正規化済)
    surface_V_n = main_view.surface_V_n
    # 床から球の中心までのベクトルを算出する
    s_a_x, s_a_y, s_a_z = main_view.surface.corner_A()
    center_V = [sphere.center[0] - s_a_x,
                sphere.center[1] - s_a_y,
                sphere.center[2] - s_a_z]
    # 床からの法線ベクトルと球の中心からの距離を算出する
    distance = abs(dot_product(surface_V_n, center_V))

    # 進行ベクトルの長さを算出
    fall_vector = sphere.proceed_vector
    fall_length = sqrt(fall_vector[0] ** 2 + \
                       fall_vector[1] ** 2 + fall_vector[2] ** 2)

    is_on_floor = False
    if distance - sphere.radius > fall_length:
        sphere.proceed()
    else:
        # 球が床にめり込む場合
        rate = 0
        if fall_length != 0:
            rate = (distance - sphere.radius) / fall_length

        sphere.set_center(
            sphere.center[0] + fall_vector[0] * rate,
            sphere.center[1] + fall_vector[1] * rate,
            sphere.center[2] + fall_vector[2] * rate)
        sphere.proceed_vector = r_vector

        is_on_floor = True

    # main_view.set_needs_display()
    lock.release()

    if main_view.on_screen is True and is_on_floor is False:
        t = threading.Timer(0.02, fall_sphere_schedule, args=[main_view, sphere, r_vector, lock])
        t.start()
    elif main_view.on_screen is True and is_on_floor is True:
        t = threading.Timer(0.02, move_sphere_schedule, args=[main_view, sphere, lock])
        t.start()


# 壁と球が接触するか判別してフラグを返す
# True:接触する	/ False:接触しない
# 壁に減り込み場合は壁に丁度接触する位置に球を移動する
# 球の進行ベクトルを使った移動はここでは実施しない。
# 全ての壁がFalseを返した場合に球を進行させる
#
# wall_V_n  : 正規化した壁の法線
# wall_x,y,z: 壁の一点の座標.壁との距離の算出に利用
def reflect_sphere(sphere, wall_V_n, wall_x, wall_y, wall_z):
    is_reflect = False

    # 床から球の中心までのベクトルを算出する
    center_V = [sphere.center[0] - wall_x,
                sphere.center[1] - wall_y,
                sphere.center[2] - wall_z]

    # 壁からの法線ベクトルと球の中心からの距離を算出する
    distance = abs(dot_product(wall_V_n, center_V))

    # 進行ベクトルの長さを算出
    proceed_vector = sphere.proceed_vector
    proceed_length = sqrt(proceed_vector[0] ** 2 + proceed_vector[1] ** 2 + proceed_vector[2] ** 2)

    # 進行ベクトルと壁のなす角
    proceed_cos_theta = dot_product(wall_V_n, normalize(proceed_vector))

    # 壁と球の接触判定(なす角も判別条件に加える)
    if distance - sphere.radius <= proceed_length and proceed_cos_theta < 0:
        rate = 1
        if proceed_length != 0:
            rate = (distance - sphere.radius) / proceed_length
        sphere.set_center(
            sphere.center[0] + proceed_vector[0] * rate,
            sphere.center[1] + proceed_vector[1] * rate,
            sphere.center[2] + proceed_vector[2] * rate)

        # R = F + 2(-F・N)N
        # 進行の逆ベクトル dot 正規化した法線
        r_proceed_vector = [
            -1 * proceed_vector[0],
            -1 * proceed_vector[1],
            -1 * proceed_vector[2]]
        r_proceed_dot_n_value = dot_product(r_proceed_vector, wall_V_n)
        new_proceed_vector = [
            proceed_vector[0] + (2 * r_proceed_dot_n_value * wall_V_n[0]),
            proceed_vector[1] + (2 * r_proceed_dot_n_value * wall_V_n[1]),
            proceed_vector[2] + (2 * r_proceed_dot_n_value * wall_V_n[2]),
        ]
        sphere.proceed_vector = new_proceed_vector
        is_reflect = True

    return is_reflect


# 球を動かす
# 球が床の上にあるときに動作する
def move_sphere_schedule(main_view, sphere, lock):
    lock.acquire()
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(sphere, Sphere) is False:
        return

    # 手前の壁
    wall_x, wall_y, wall_z = main_view.surface.corner_B()
    is_reflect = reflect_sphere(
        sphere, main_view.front_wall_V_n, wall_x, wall_y, wall_z)

    # 左の壁
    if is_reflect is False:
        is_reflect = reflect_sphere(
            sphere, main_view.left_wall_V_n, wall_x, wall_y, wall_z)

    # 奥の壁
    if is_reflect is False:
        wall_x, wall_y, wall_z = main_view.surface.corner_D()
        is_reflect = reflect_sphere(
            sphere, main_view.back_wall_V_n, wall_x, wall_y, wall_z)

    # 右の壁
    if is_reflect is False:
        wall_x, wall_y, wall_z = main_view.surface.corner_D()
        is_reflect = reflect_sphere(
            sphere, main_view.right_wall_V_n, wall_x, wall_y, wall_z)

    # 天井の壁
    if is_reflect is False:
        wall_x, wall_y, wall_z = main_view.ceiling.corner_A()
        is_reflect = reflect_sphere(
            sphere, main_view.ceiling_V_n, wall_x, wall_y, wall_z)

    # 床の壁
    if is_reflect is False:
        wall_x, wall_y, wall_z = main_view.surface.corner_A()
        is_reflect = reflect_sphere(
            sphere, main_view.surface_V_n, wall_x, wall_y, wall_z)

    if is_reflect is False:
        sphere.proceed()

    sphere.spin()
    # main_view.set_needs_display()
    lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.02, move_sphere_schedule, args=[main_view, sphere, lock])
        t.start()


# 球のパーツを順次表示させる
def show_sphere_schedule(sphere, lock):
    if isinstance(sphere, Sphere) is False:
        return

    count = 0

    lock.acquire()

    for triangle in sphere.triangles:
        count += 1
        if triangle.is_hide is True:
            triangle.is_hide = False
            break

    sphere.spin()
    # main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True and count < len(sphere.triangles):
        t = threading.Timer(0.02, show_sphere_schedule, args=[sphere, lock])
        t.start()


# 再描画処理
def display_schedule(main_view, lock):
    if isinstance(main_view, BaseView) is False:
        return

    lock.acquire()

    main_view.set_needs_display()

    lock.release()

    if main_view.on_screen is True:
        t = threading.Timer(0.012, display_schedule, args=[main_view, lock])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '反射する球'
    main_view.background_color = 'lightblue'

    # カメラの位置
    main_view.set_camera_position(0, 0, 200)
    # カメラの注視点
    main_view.set_lookat_position(0, 0, -250)
    # ビュー座標の軸を生成する
    main_view.set_camera_coodinate_vector()

    # 球
    sphere = Sphere(80, is_hide=True)
    sphere.set_center(0, 0, -250)
    main_view.add_sphere(sphere)

    # 二つ目の球
    sphere_2 = Sphere(80, is_hide=True)
    sphere_2.set_center(0, 0, -250)
    sphere_2.face_color = 'yellow'
    main_view.add_sphere(sphere_2)

    # 三つ目の球
    sphere_3 = Sphere(80, is_hide=True)
    sphere_3.set_center(0, 0, -250)
    sphere_3.face_color = 'red'
    main_view.add_sphere(sphere_3)

    # 水面
    surface = Square(-250, -500, 0, -250, 0, 0, 250, 0, 0, 250, -500, 0)
    surface.set_center(0, 0, 0)
    surface.translate(0, 300, 0)
    surface.set_scale(1)
    surface.set_angle_x(90)
    main_view.set_surface(surface)

    # 天井
    ceiling = Square(-250, -500, 0, -250, 0, 0, 250, 0, 0, 250, -500, 0)
    ceiling.set_center(0, 0, 0)
    ceiling.translate(0, -300, 0)
    ceiling.set_scale(1)
    ceiling.set_angle_x(90)
    main_view.set_ceiling(ceiling)

    main_view.present()

    # タイマー処理を設定する
    lock = threading.Lock()

    # 一つ目の球
    delay = 1.0

    t1 = threading.Timer(delay, show_sphere_schedule, args=[sphere, lock])
    t1.start()

    delay += 4.0
    t2 = threading.Timer(delay, fall_sphere_schedule, args=[main_view, sphere, [-5, 3, -1], lock])
    t2.start()

    # 2つ目の球
    delay += 10.0
    t3 = threading.Timer(delay, show_sphere_schedule, args=[sphere_2, lock])
    t3.start()

    # 視点移動　周回
    delay += 0.5
    tv1 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 90 + 360, lock])
    tv1.start()

    delay += 4.0
    t4 = threading.Timer(delay, fall_sphere_schedule, args=[main_view, sphere_2, [1, 1, -5], lock])
    t4.start()

    # 3つ目の球
    delay += 10.0
    t5 = threading.Timer(delay, show_sphere_schedule, args=[sphere_3, lock])
    t5.start()

    # 視点移動　上昇
    delay += 0.5
    tv2 = threading.Timer(delay, change_view_y_schedule, args=[main_view, -200, -4, lock])
    tv2.start()

    delay += 4.0
    t6 = threading.Timer(delay, fall_sphere_schedule, args=[main_view, sphere_3, [1, -5, 1], lock])
    t6.start()

    # 視点移動　下降
    delay += 10.0
    tv3 = threading.Timer(delay, change_view_y_schedule, args=[main_view, 200, 4, lock])
    tv3.start()

    # 視点移動　上昇
    delay += 15.0
    tv4 = threading.Timer(delay, change_view_y_schedule, args=[main_view, 0, -2, lock])
    tv4.start()

    # 視点移動　周回
    delay += 0.5
    tv5 = threading.Timer(delay, change_view_round_schedule, args=[main_view, 90, 90 + 360, lock])
    tv5.start()

    td = threading.Timer(0.01, display_schedule, args=[main_view, lock])
    td.start()


