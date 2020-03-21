import ui
import threading
from math import cos
from math import sin
from math import radians


# 図形の基本クラスとして定義
class MyFigure():
    color = 'black'
    # 回転角度と中心
    rotate_angle_x = 0
    rotate_angle_y = 0
    rotate_angle_z = 0
    center_x = 0
    center_y = 0
    center_z = 0
    # 拡大縮小率
    scale = 1
    # 平行移動
    shift_x = 0
    shift_y = 0
    shift_z = 0
    #
    is_hide = False

    def set_scale(self, scale):
        self.scale = scale

    def set_center(self, x, y, z):
        self.center_x = x
        self.center_y = y
        self.center_z = z

    def set_color(self, color):
        self.color = color

    def set_shift(self, x, y, z):
        self.shift_x = x
        self.shift_y = y
        self.shift_z = z

    def set_angle_x(self, angle):
        self.rotate_angle_x = angle

    def set_angle_y(self, angle):
        self.rotate_angle_y = angle

    def set_angle_z(self, angle):
        self.rotate_angle_z = angle

    def set_rotate_angle(self, rotate_angle):
        self.rotate_angle_z = rotate_angle

    # 拡大縮小
    def scale_queue(self, x, y, z):
        return ((x * self.scale), (y * self.scale), (z * self.scale))

    # 平行移動
    def shift_queue(self, x, y, z):
        return ((x + self.shift_x), (y + self.shift_y), (z + self.shift_z))

    # 3次元回転行列
    def rotate_queue(self, x, y, z):
        angle_x = self.rotate_angle_x
        angle_y = self.rotate_angle_y
        angle_z = self.rotate_angle_z

        # x+=self.center_x
        y += self.center_y
        z += self.center_z

        # x軸の回転
        r_x_x = x  # ((1 * x) + (0) + (0))
        r_x_y = ((0) + (y * cos(radians(angle_x))) + (-1 * z * sin(radians(angle_x))))
        r_x_z = ((0) + (y * sin(radians(angle_x))) + (z * cos(radians(angle_x))))

        # r_x_x -= self.center_x
        r_x_y -= self.center_y
        r_x_z -= self.center_z

        r_x_x += self.center_x
        # r_x_y += self.center_y
        r_x_z += self.center_z

        # y軸の回転
        r_y_x = ((r_x_x * cos(radians(angle_y))) + (0) + (r_x_z * sin(radians(angle_y))))
        r_y_y = r_x_y  # ((0) + (1 * r_x_y) + (0))
        r_y_z = ((-1 * r_x_x * sin(radians(angle_y))) + (0) + (r_x_z * cos(radians(angle_y))))

        r_y_x -= self.center_x
        # r_y_y -= self.center_y
        r_y_z -= self.center_z

        r_y_x += self.center_x
        r_y_y += self.center_y
        # r_y_z += self.center_z

        # z軸の回転
        r_z_x = ((r_y_x * cos(radians(angle_z))) + (-1 * r_y_y * sin(radians(angle_z))) + (0))
        r_z_y = ((r_y_x * sin(radians(angle_z))) + (r_y_y * cos(radians(angle_z))) + (0))
        r_z_z = r_y_z  # ((0) + (0) + (1 * r_y_z))

        r_z_x -= self.center_x
        r_z_y -= self.center_y
        # r_z_z -= self.center_z

        return (r_z_x, r_z_y, r_z_z)

    # 回転、平行移動、拡大縮小を行う
    def queue(self, x, y, z):
        r_x, r_y, r_z = x, y, z
        r_x, r_y, r_z = self.rotate_queue(r_x, r_y, r_z)
        r_x, r_y, r_z = self.shift_queue(r_x, r_y, r_z)
        r_x, r_y, r_z = self.scale_queue(r_x, r_y, r_z)
        return (r_x, r_y, r_z)

    def mycolor(self):
        return self.color


# 四角
class Square(MyFigure):
    color = '#90b0ff'

    def __init__(self, A_x, A_y, A_z, B_x, B_y, B_z, C_x, C_y, C_z, D_x, D_y, D_z):
        self.A_x = A_x
        self.A_y = A_y
        self.A_z = A_z
        self.B_x = B_x
        self.B_y = B_y
        self.B_z = B_z
        self.C_x = C_x
        self.C_y = C_y
        self.C_z = C_z
        self.D_x = D_x
        self.D_y = D_y
        self.D_z = D_z

    def corner_A(self):
        return (self.queue(self.A_x, self.A_y, self.A_z))

    def corner_B(self):
        return (self.queue(self.B_x, self.B_y, self.B_z))

    def corner_C(self):
        return (self.queue(self.C_x, self.C_y, self.C_z))

    def corner_D(self):
        return (self.queue(self.D_x, self.D_y, self.D_z))


# 花びら
class Petal(MyFigure):
    petal_color_A = 'pink'
    petal_color_B = '#ff9bb8'

    def __init__(self, A_x, A_y, A_z, B_x, B_y, B_z, C_x, C_y, C_z, D_x, D_y, D_z, E_x, E_y, E_z, F_x, F_y, F_z):
        self.A_x = A_x
        self.A_y = A_y
        self.A_z = A_z
        self.B_x = B_x
        self.B_y = B_y
        self.B_z = B_z
        self.C_x = C_x
        self.C_y = C_y
        self.C_z = C_z
        self.D_x = D_x
        self.D_y = D_y
        self.D_z = D_z
        self.E_x = E_x
        self.E_y = E_y
        self.E_z = E_z
        self.F_x = F_x
        self.F_y = F_y
        self.F_z = F_z
        self.is_front = False

    def corner_A(self):
        return (self.queue(self.A_x, self.A_y, self.A_z))

    def corner_B(self):
        return (self.queue(self.B_x, self.B_y, self.B_z))

    def corner_C(self):
        return (self.queue(self.C_x, self.C_y, self.C_z))

    def corner_D(self):
        return (self.queue(self.D_x, self.D_y, self.D_z))

    def corner_E(self):
        return (self.queue(self.E_x, self.E_y, self.E_z))

    def corner_F(self):
        return (self.queue(self.F_x, self.F_y, self.F_z))


class Wave(MyFigure):
    color = 'blue'

    def __init__(self, x, y, z):
        self.shift_x = x
        self.shift_y = y
        self.shift_z = z
        self.radius_length = 0

    def set_radius_length(self, radius_length):
        self.radius_length = radius_length

    # 配列で、半径に対応したx、y, z 座標を返す
    def points(self):
        radius = self.radius_length
        points = []

        for angle in range(0, 360, 10):
            x = cos(radians(angle)) * radius
            y = sin(radians(angle)) * radius
            z = self.center_z  # Todo:検討
            r_x, r_y, r_z = self.queue(x, y, z)
            points.append([r_x, r_y, r_z])

        return points


# 背景と床を描画する
class BaseView(ui.View):
    petals = []  # 花びらの配列。一つのみのインスタンスなのでstaticメンバで定義する。
    waves = []  # 波の配列
    surface = None
    screen_depth = 400  # 視点から投影面までの距離

    def add_petal(self, petal):
        self.petals.append(petal)

    def set_surface(self, surface):
        self.surface = surface

    def add_wave(self, wave):
        self.waves.append(wave)

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

        # 円(波)を描画する
        for wave in self.waves:
            if wave.is_hide is True:
                continue

            wave_points = wave.points()

            if len(wave_points) < 1:
                continue
            if len(wave_points[0]) < 3:
                continue

            path_w = ui.Path()
            s_x, s_y = self.projection(
                wave_points[0][0],
                wave_points[0][1],
                wave_points[0][2])
            path_w.move_to(s_x, s_y)

            for i in range(1, len(wave_points)):
                x, y = self.projection(wave_points[i][0],
                                       wave_points[i][1],
                                       wave_points[i][2])
                path_w.line_to(x, y)
            path_w.line_to(s_x, s_y)
            ui.set_color(wave.mycolor())
            path_w.stroke()

        # 桜
        for petal in self.petals:
            if petal.is_hide is True:
                continue

            a_x, a_y, a_z = petal.corner_A()
            b_x, b_y, b_z = petal.corner_B()
            c_x, c_y, c_z = petal.corner_C()
            d_x, d_y, d_z = petal.corner_D()
            e_x, e_y, e_z = petal.corner_E()
            f_x, f_y, f_z = petal.corner_F()

            # 三次元空間から二次元スクリーンへの投影を反映する
            a_x, a_y = self.projection(a_x, a_y, a_z)
            b_x, b_y = self.projection(b_x, b_y, b_z)
            c_x, c_y = self.projection(c_x, c_y, c_z)
            d_x, d_y = self.projection(d_x, d_y, d_z)
            e_x, e_y = self.projection(e_x, e_y, e_z)
            f_x, f_y = self.projection(f_x, f_y, f_z)

            path_1 = ui.Path()
            path_1.move_to(a_x, a_y)
            path_1.line_to(b_x, b_y)
            path_1.line_to(c_x, c_y)
            path_1.line_to(d_x, d_y)
            path_1.line_to(a_x, a_y)

            ui.set_color(petal.petal_color_A)
            path_1.fill()

            path_2 = ui.Path()
            path_2.move_to(a_x, a_y)
            path_2.line_to(e_x, e_y)
            path_2.line_to(f_x, f_y)
            path_2.line_to(d_x, d_y)

            ui.set_color(petal.petal_color_B)
            path_2.fill()


# 花びらを回す
def schedule(main_view):
    if isinstance(main_view, BaseView) is False:
        return

    for petal in main_view.petals:
        angle = petal.rotate_angle_y
        petal.set_angle_y(angle + 5)

    main_view.set_needs_display()

    if main_view.on_screen is True:
        t1 = threading.Timer(0.02, schedule, args=[main_view])
        t1.start()


# 花びらを落とす
def fall_schedule(main_view):
    if isinstance(main_view, BaseView) is False:
        return

    surface = main_view.surface
    s_x, surface_y, s_z = surface.corner_A()

    for petal in main_view.petals:
        # 位置を下げ落とす
        petal.shift_y += 0.18
        petal.shift_x -= 0.08
        # 花びらの3d座標を取得する
        petal_A_x, petal_A_y, petal_A_z = petal.corner_A()
        petal_F_x, petal_F_y, petal_F_z = petal.corner_F()

        petal_x, petal_y, petal_z = petal_A_x, petal_A_y, petal_A_z
        if petal_y < petal_F_y:
            petal_x, petal_y, petal_z = petal_F_x, petal_F_y, petal_F_z

        # 水面と花びらの接触を判別する
        # TODO: 判別方法を模索する余地あり
        if petal_y >= surface_y and petal.is_hide is False:
            # 花びらの表示を消す
            petal.is_hide = True
            # 花びらの落下位置を投影した座標を取得
            petal_x, petal_y = main_view.projection(petal_x, petal_y, petal_z)

            wave = Wave(petal_x, petal_y, 0)
            wave.set_angle_x(270)
            main_view.add_wave(wave)

            t = threading.Timer(0.1, wave_schedule, args=[main_view, wave, 0])
            t.start()

    main_view.set_needs_display()

    if main_view.on_screen is True:
        t1 = threading.Timer(0.02, fall_schedule, args=[main_view])
        t1.start()


# 波を広げる
def wave_schedule(main_view, wave, length):
    if isinstance(main_view, BaseView) is False:
        return

    wave.set_radius_length(length)
    if wave.radius_length >= 70:
        wave.is_hide = True
        wave.set_radius_length(0)

    main_view.set_needs_display()
    length += 1

    if main_view.on_screen is True and length <= 70:
        t1 = threading.Timer(0.02, wave_schedule, args=[main_view, wave, length])
        t1.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = 'サクラの花びら'
    # main_view.background_color = 'black'
    main_view.background_color = 'lightblue'

    # 水面
    surface = Square(-250, 300, 0, 250, 300, 0, 250, 0, 0, -250, 0, 0)
    surface.set_center(0, 0, 0)
    surface.set_shift(190, 540, 0)
    surface.set_angle_x(270)
    main_view.set_surface(surface)

    # 花びらの折り目の深さ
    depth_s = 7
    depth_l = 10
    petal_settings = [  # x, y, angle_z, angle_y
        [210, 150, 10, 30],
        [160, 180, 350, 10],
        [240, 200, 10, 60],
        [290, 250, 350, 30],
        [400, 150, 350, 50],
        [300, 30, 10, 0],
        [260, 0, 350, 60],
        [230, 60, 10, 90],
        [270, 80, 350, 170],
        [360, 130, 10, 140],
        [220, 360, 10, 290],
        [110, 380, 350, 40],
        [170, 330, 10, 130],
    ]

    for i in range(0, len(petal_settings)):
        #
        petal = Petal(0, -15, depth_s,
                      20, 0, 1, 10, 50, 1,
                      0, 45, depth_l,
                      -20, 0, 1, -10, 50, 1)
        #
        petal.set_shift(
            petal_settings[i][0],
            petal_settings[i][1], -150)
        petal.set_angle_z(petal_settings[i][2])
        petal.set_angle_y(petal_settings[i][3])
        main_view.add_petal(petal)

    main_view.present()

    delay = 1.0
    t1 = threading.Timer(delay, schedule, args=[main_view])
    t1.start()

    t2 = threading.Timer(delay, fall_schedule, args=[main_view])
    t2.start()