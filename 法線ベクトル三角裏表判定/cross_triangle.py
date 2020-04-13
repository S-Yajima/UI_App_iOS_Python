
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
    def shift_queue(self, x, y, z):
        return ((x + self.shift_x), (y + self.shift_y), (z + self.shift_z))

    # 3次元回転行列
    # [x']=[x cosθ  -y sinθ] [x]
    # [y']=[x sinθ  y cosθ] [y]
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

    # A→B→Cが半時計周りに見える面が面になるように
    # 座標を設定すること
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

    def corner_A(self):
        # print('___c_A___')
        x, y, z = self.queue(self.A_x, self.A_y, self.A_z)
        return (x, y, z)

    def corner_B(self):
        # print('___c_B___')
        x, y, z = self.queue(self.B_x, self.B_y, self.B_z)
        return (x, y, z)

    def corner_C(self):
        # print('___c_C___')
        x, y, z = self.queue(self.C_x, self.C_y, self.C_z)
        return (x, y, z)


# 背景と床を描画する
class BaseView(ui.View):
    triangles = []
    numbers = []
    round_angle = 0
    screen_depth = 250  # 視点から投影面までの距離

    def add_triangle(self, triangle):
        self.triangles.append(triangle)

    # 表示中の図形の表裏向きを判別する
    # 下記二つのベクトルを算出し、内積を計算する
    # ・三角形のABとACの外積
    # ・三角形からカメラ焦点のベクトル
    # 入力) 図形３つの頂点ABCのxyz座標
    # 出力) False:裏、True:面
    def is_face(self, a_x, a_y, a_z,
                b_x, b_y, b_z,
                c_x, c_y, c_z):
        is_fase = False  # 表裏を示す値。初期値False裏
        # 三角形の中心から視点焦点へのベクトル
        scr_vector = [
            self.width / 2 - (a_x + b_x + c_x) / 3,
            self.height / 2 - (a_y + b_y + c_y) / 3,
            self.screen_depth - (a_z + b_z + c_z) / 3]
        # 三角形の頂点Aから頂点Bへのベクトル(b - a)
        AB = [b_x - a_x, b_y - a_y, b_z - a_z]
        # 三角形の頂点Aから頂点Cへのベクトル(c - a)
        AC = [c_x - a_x, c_y - a_y, c_z - a_z]
        # ベクトルAB, AC の外積を求める
        cross_AB_AC = [
            AB[1] * AC[2] - AB[2] * AC[1],
            AB[2] * AC[0] - AB[0] * AC[2],
            AB[0] * AC[1] - AB[1] * AC[0]]

        # 視点のベクトルとAB,ACの外積との内積を求める
        inner = scr_vector[0] * cross_AB_AC[0] + \
                scr_vector[1] * cross_AB_AC[1] + \
                scr_vector[2] * cross_AB_AC[2]
        # 内積の値が0より大きいかで表裏を判別する
        if inner > 0.0:
            is_fase = True

        return is_fase

    # スクリーン投影を実行し座標を返す
    def screen_project(self, x, y, z):
        depth = self.screen_depth * -1
        center_width = self.width / 2
        center_height = self.height / 2

        s_x = (depth / (z + depth)) * (x - center_width) + center_width
        s_y = (depth / (z + depth)) * (y - center_height) + center_height

        return (s_x, s_y)

    # 描画
    def draw(self):
        # 三角
        for triangle in self.triangles:
            if triangle.is_hide is True:
                continue

            a_x, a_y, a_z = triangle.corner_A()
            b_x, b_y, b_z = triangle.corner_B()
            c_x, c_y, c_z = triangle.corner_C()
            # 図形が表裏どちらが表示されているか判別する
            # スクリーン投影する前の座標から判別を行う
            is_face = self.is_face(
                a_x, a_y, a_z, b_x, b_y, b_z, c_x, c_y, c_z)

            # 三次元空間から二次元スクリーンへの投影を反映する
            s_a_x, s_a_y = self.screen_project(a_x, a_y, a_z)
            s_b_x, s_b_y = self.screen_project(b_x, b_y, b_z)
            s_c_x, s_c_y = self.screen_project(c_x, c_y, c_z)

            path_t = ui.Path()
            path_t.move_to(s_a_x, s_a_y)
            path_t.line_to(s_b_x, s_b_y)
            path_t.line_to(s_c_x, s_c_y)
            path_t.line_to(s_a_x, s_a_y)

            ui.set_color(triangle.mycolor())

            if is_face is False:
                path_t.stroke()
            else:
                path_t.fill()


# 三角形を移動する
def move_schedule(main_view, triangle, goal_x, goal_y):
    if isinstance(main_view, BaseView) is False:
        return

    if isinstance(triangle, Triangle) is False:
        return

    x = triangle.shift_x
    if abs(goal_x - x) < 2:
        x = goal_x
    elif goal_x > x:
        x += 2
    elif goal_x < x:
        x -= 2

    y = triangle.shift_y
    if abs(goal_y - y) < 2:
        y = goal_y
    elif goal_y > y:
        y += 2
    elif goal_y < y:
        y -= 2

    triangle.set_shift(x, y, triangle.shift_z)
    main_view.set_needs_display()

    if main_view.on_screen is True and (triangle.shift_x != goal_x or triangle.shift_y != goal_y):
        t1 = threading.Timer(0.02, move_schedule, args=[main_view, triangle, goal_x, goal_y])
        t1.start()


# 三角を回転して表示
def schedule(main_view, angle, indexes, direction, finish_angle):
    if isinstance(main_view, BaseView) is False:
        return

    for index in indexes:
        if len(main_view.triangles) > index:
            # x, y, z軸回転
            triangle = main_view.triangles[index]
            triangle.is_hide = False

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
    main_view.name = '法線ベクトルで三角裏表判別'
    main_view.background_color = 'lightblue'

    # 三角形を複数生成
    color = ['green', 'yellow', 'blue', 'orange']

    for i in range(6):
        for j in range(12):
            triangle = Triangle(0, -25, 1, -25, 25, 1, 25, 25, 1)
            triangle.set_shift(50 * (j + 1), 50 * (i + 1), 0)
            triangle.set_center(0, 0, 0)
            triangle.set_color(color[i % len(color)])
            main_view.add_triangle(triangle)

    main_view.present()

    delay = 1.0
    direction = int(Direction.X | Direction.Y)
    for i in range(len(main_view.triangles)):
        t1 = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t1.start()
        delay += 0.3

    delay = 11.0
    direction = Direction.X
    for i in range(len(main_view.triangles)):
        t2 = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t2.start()
        delay += 0.3

    delay = 21.0
    direction = Direction.Y
    for i in range(len(main_view.triangles)):
        t3 = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t3.start()
        delay += 0.3

    delay = 23.0
    direction = Direction.Z
    for i in range(len(main_view.triangles) - 1, -1, -1):
        t4 = threading.Timer(delay, schedule, args=[main_view, 0, [i], direction, 360])
        t4.start()
        delay += 0.3

    delay = 50.0
    direction = Direction.Y

    indexes_1 = [
        12, 24, 36, 48,
        23, 35, 47, 59]
    t5 = threading.Timer(delay, schedule, args=[main_view, 0, indexes_1, direction, 270])
    t5.start()

    direction_2 = Direction.X
    indexes_2 = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
        60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
    t6 = threading.Timer(delay, schedule, args=[main_view, 0, indexes_2, direction_2, 270])
    t6.start()

    delay = 53.0
    indexes_3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    for i in indexes_3:
        if len(main_view.triangles) > i:
            triangle = main_view.triangles[i]
            t7 = threading.Timer(delay, move_schedule, args=[main_view, triangle, triangle.shift_x, 300])
            t7.start()

    indexes_4 = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
    for i in indexes_4:
        if len(main_view.triangles) > i:
            triangle = main_view.triangles[i]
            t8 = threading.Timer(delay, move_schedule, args=[main_view, triangle, triangle.shift_x, 50])
            t8.start()

    delay = 58.0
    indexes_5 = [12, 24, 36, 48]
    for i in indexes_5:
        if len(main_view.triangles) > i:
            triangle = main_view.triangles[i]
            t7 = threading.Timer(delay, move_schedule, args=[main_view, triangle, 600, triangle.shift_y])
            t7.start()

    indexes_6 = [23, 35, 47, 59]
    for i in indexes_6:
        if len(main_view.triangles) > i:
            triangle = main_view.triangles[i]
            t8 = threading.Timer(delay, move_schedule, args=[main_view, triangle, 50, triangle.shift_y])
            t8.start()