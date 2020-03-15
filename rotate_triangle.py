import ui
import threading
from math import cos
from math import sin
from math import radians
from enum import IntEnum


# 回転方向
class Direction(IntEnum):
    X = 1
    Y = (1 << 1)
    Z = (1 << 2)

# 図形の基本クラス
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
    # 表示/非表示
    is_hide = True

    is_enable_shadow = True
    shadow_color = 'gray'

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
    # [x']=[x a]
    # [y']=[y b]
    # [z']=[z c]
    def shift_queue(self, x, y, z):
        return ((x + self.shift_x), (y + self.shift_y), (z + self.shift_z))

    # 3次元回転行列
    # xθ
    # [x']=[1    0      0   ] [x]
    # [y']=[0  cosθ  -sinθ] [y]
    # [z']=[0  sinθ  cosθ ] [z]
    # yθ
    # [x']=[cosθ  0  sinθ] [x]
    # [y']=[0      1     0 ] [y]
    # [z']=[-sinθ 0  cosθ] [z]
    # zθ
    # [x']=[cosθ  -sinθ  0] [y]
    # [y']=[sinθ  cosθ   0] [z]
    # [z']=[ 0      0      1] [x]
    def rotate_queue(self, x, y, z):
        # x+=self.center_x
        y += self.center_y
        z += self.center_z

        angle_x = self.rotate_angle_x
        angle_y = self.rotate_angle_y
        angle_z = self.rotate_angle_z

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


# 三角
class Triangle(MyFigure):

    def __init__(self, A_x, A_y, A_z, B_x, B_y, B_z, C_x, C_y, C_z):
        self.A_x = A_x
        self.A_y = A_y
        self.A_z = A_z
        self.B_x = B_x
        self.B_y = B_y
        self.B_z = B_z
        self.C_x = C_x
        self.C_y = C_y
        self.C_z = C_z
        self.is_front = True

    def corner_A(self):
        # print('___c_A___')
        x, y, z = self.queue(self.A_x, self.A_y, self.A_z)
        # return (x, y)
        return (x, y, z)

    def corner_B(self):
        # print('___c_B___')
        x, y, z = self.queue(self.B_x, self.B_y, self.B_z)
        # return (x, y)
        return (x, y, z)

    def corner_C(self):
        # print('___c_C___')
        x, y, z = self.queue(self.C_x, self.C_y, self.C_z)
        # return (x, y)
        return (x, y, z)


# 背景と床を描画する
class BaseView(ui.View):
    triangles = []
    numbers = []
    round_angle = 0
    screen_depth = 300  # 視点から投影面までの距離

    def add_triangle(self, triangle):
        self.triangles.append(triangle)

    # 描画
    def draw(self):
        # 三角
        for triangle in self.triangles:
            if triangle.is_hide is True:
                continue

            a_x, a_y, a_z = triangle.corner_A()
            b_x, b_y, b_z = triangle.corner_B()
            c_x, c_y, c_z = triangle.corner_C()

            # 三次元空間から二次元スクリーンへの投影を反映する
            # Todo: 三次元空間の起点座標(0,0,0)と
            #             二次元の起点座標(0,0)との差分を反映する
            # Todo: 実行する場所、実装箇所を考える
            '''
            depth = self.screen_depth * -1
            if (a_z / depth) != 0:
                a_x = (depth / (a_z + depth)) * a_x
                a_y = (depth / (a_z + depth)) * a_y
            if (b_z / depth) != 0:
                b_x = (depth / (b_z + depth)) * b_x
                b_y = (depth / (b_z + depth)) * b_y
            if (c_z / depth) != 0:
                c_x = (depth / (c_z + depth)) * c_x
                c_y = (depth / (c_z + depth)) * c_y
            '''

            path_t = ui.Path()
            path_t.move_to(a_x, a_y)
            path_t.line_to(b_x, b_y)
            path_t.line_to(c_x, c_y)
            path_t.line_to(a_x, a_y)

            ui.set_color(triangle.mycolor())
            # 裏の場合は三角を塗りつぶす
            if triangle.is_front is True:
                path_t.stroke()
            else:
                path_t.fill()


# 三角を表示、回転
def schedule(main_view, angle, indexes, direction, finish_angle):
    if isinstance(main_view, BaseView) is False:
        return

    for index in indexes:
        if len(main_view.triangles) > index:
            # x, y, z軸回転
            triangle = main_view.triangles[index]
            triangle.is_hide = False

            if int(direction & Direction.X) > 0 or int(direction & Direction.Y) > 0:
                if 90 < angle and angle < 270:
                    triangle.is_front = False
                else:
                    triangle.is_front = True

            if int(direction & Direction.X) > 0:
                triangle.set_angle_x(angle)
            if int(direction & Direction.Y) > 0:
                triangle.set_angle_y(angle)
            if int(direction & Direction.Z) > 0:
                triangle.set_angle_z(angle)

    main_view.set_needs_display()
    angle = (angle + 5)  # % 360

    if main_view.on_screen is True and angle <= finish_angle:
        t1 = threading.Timer(0.02, schedule, args=[main_view, angle, indexes, direction, finish_angle])
        t1.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '三角三次元回転'
    main_view.background_color = 'lightblue'

    # 三角形の生成と配置
    x_gap = [0, -25]
    color = ['green', 'yellow', 'blue', 'orange']

    for i in range(8):
        for j in range(7):
            triangle = Triangle(-25, 25, 1, 0, -25, 1, 25, 25, 1)
            triangle.set_shift(x_gap[i % len(x_gap)] + 50 * (j + 1), 50 * (i + 1), 0)
            triangle.set_center(0, 0, 0)
            triangle.set_color(color[i % len(color)])
            main_view.add_triangle(triangle)

    main_view.present()

    # 三角形の動作をタイマーで設定
    delay = 1.0
    direction = int(Direction.X | Direction.Y)
    for i in range(len(main_view.triangles)):
        t = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t.start()
        delay += 0.3

    delay = 11.0
    direction = Direction.X
    for i in range(len(main_view.triangles)):
        t = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t.start()
        delay += 0.3

    delay = 21.0
    direction = Direction.Y
    for i in range(len(main_view.triangles)):
        t = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t.start()
        delay += 0.3

    delay = 23.0
    direction = Direction.Z
    for i in range(len(main_view.triangles) - 1, -1, -1):
        t = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t.start()
        delay += 0.3

    delay = 43.0
    direction_1 = Direction.Y
    direction_2 = Direction.X
    for i in range(8):
        indexes_1 = []
        indexes_2 = []

        for j in range(7):
            indexes_1.append((i * 7) + j)
            indexes_2.append(((7 - i) * 7) + j)

        t1 = threading.Timer(delay, schedule, args=[main_view, 0, indexes_1, direction_1, 360])
        t1.start()
        t2 = threading.Timer(delay, schedule, args=[main_view, 0, indexes_2, direction_2, 360])
        t2.start()
        delay += 1

    delay = 55
    direction = Direction.Y
    indexes_3 = [52, 44, 45, 37, 38, 39, 29, 30, 31, 32, 22, 23, 24, 25, 26, 15, 16, 17, 18, 9, 10, 11, 2, 3]

    for i in range(2):
        t = threading.Timer(delay, schedule, args=[main_view, 0, indexes_3, direction, 360])
        t.start()
        delay += 2.6

    delay = 61
    direction = Direction.Y
    indexes_4 = [1, 8, 9, 5, 12, 13, 14, 16, 18, 20, 23, 29, 27, 33, 25, 31, 38, 44, 45, 46, 51, 54]

    for i in range(2):
        t = threading.Timer(delay, schedule, args=[main_view, 0, indexes_4, direction, 360])
        t.start()
        delay += 2.6

    delay = 67
    direction = Direction.X
    indexes_5 = [52, 44, 45, 37, 38, 39, 29, 30, 31, 32, 22, 23, 24, 25, 26, 14, 15, 16, 17, 18, 19, 7, 8, 9, 11, 12,
                 13, 0, 1, 4, 5]

    finish_angle = 360
    for i in range(2):
        t = threading.Timer(delay, schedule, args=[main_view, 0, indexes_5, direction, finish_angle])
        t.start()
        finish_angle -= 180
        delay += 2.6