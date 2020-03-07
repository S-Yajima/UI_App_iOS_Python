import ui
import threading
from math import cos
from math import sin
from math import radians


class MyFigure():
    color = 'black'
    # 回転角度と中心
    rotate_angle = 0
    center_x = -30
    center_y = -25
    # 拡大縮小率
    scale = 1
    # 平行移動
    shift_x = 150
    shift_y = 200
    # 影
    is_enable_shadow = True
    shadow_color = 'gray'

    def set_scale(self, scale):
        self.scale = scale

    def set_center(self, x, y):
        self.center_x = x
        self.center_y = y

    def set_color(self, color):
        self.color = color

    def set_shift(self, x, y):
        self.shift_x = x
        self.shift_y = y

    def set_rotate_angle(self, rotate_angle):
        self.rotate_angle = rotate_angle

    # 拡大縮小
    def scale_queue(self, x, y):
        return ((x * self.scale), (y * self.scale))

    # 平行移動
    def shift_queue(self, x, y):
        return ((x + self.shift_x), (y + self.shift_y))

    # 2次元回転行列
    # [x']=[x cosθ  -y sinθ] [x]
    # [y']=[x sinθ  y cosθ] [y]
    def rotate_queue(self, x, y):
        x += self.center_x
        y += self.center_y

        angle = self.rotate_angle
        r_x = (x * cos(radians(angle))) + (-1 * y * sin(radians(angle)))
        r_y = (x * sin(radians(angle))) + (y * cos(radians(angle)))

        return (r_x, r_y)

    # 回転、平行移動、拡大縮小を行う
    def queue(self, x, y):
        r_x, r_y = self.rotate_queue(x, y)
        r_x, r_y = self.shift_queue(r_x, r_y)
        r_x, r_y = self.scale_queue(r_x, r_y)
        return (r_x, r_y)

    def mycolor(self):
        return self.color


# 数字。
# 数字を構成するパーツとして複数の四角を保持する。
class MyNumeral(MyFigure):

    def __init__(self):
        self.squares = []

    def square_count(self):
        return (len(self.squares))

    def add_square(self, square):
        self.squares.append(square)

    def corner_A(self, index):
        square = self.squares[index]
        x, y = self.queue(square.A_x, square.A_y)
        return (x, y)

    def corner_B(self, index):
        square = self.squares[index]
        x, y = self.queue(square.B_x, square.B_y)
        return (x, y)

    def corner_C(self, index):
        square = self.squares[index]
        x, y = self.queue(square.C_x, square.C_y)
        return (x, y)

    def corner_D(self, index):
        square = self.squares[index]
        x, y = self.queue(square.D_x, square.D_y)
        return (x, y)


# 三角。針として使用。
class Triangle(MyFigure):

    def __init__(self, A_x, A_y, B_x, B_y, C_x, C_y):
        self.A_x = A_x
        self.A_y = A_y
        self.B_x = B_x
        self.B_y = B_y
        self.C_x = C_x
        self.C_y = C_y

    def corner_A(self):
        x, y = self.queue(self.A_x, self.A_y)
        return (x, y)

    def corner_B(self):
        x, y = self.queue(self.B_x, self.B_y)
        return (x, y)

    def corner_C(self):
        x, y = self.queue(self.C_x, self.C_y)
        return (x, y)


# 四角
class Square(MyFigure):

    def __init__(self, A_x, A_y, B_x, B_y, C_x, C_y, D_x, D_y):
        self.A_x = A_x
        self.A_y = A_y
        self.B_x = B_x
        self.B_y = B_y
        self.C_x = C_x
        self.C_y = C_y
        self.D_x = D_x
        self.D_y = D_y


# 背景と床を描画する
class BaseView(ui.View):
    triangles = []
    numbers = []
    round_angle = 0

    def add_number(self, number):
        self.numbers.append(number)

    def add_triangle(self, triangle):
        self.triangles.append(triangle)

    def set_needle_angle(self, angle):
        for triangle in self.triangles:
            triangle.set_rotate_angle(angle)

    def set_number_angle(self, angle, index):
        if index < len(self.numbers):
            self.numbers[index].set_rotate_angle(angle)

    def set_round_angle(self, angle):
        self.round_angle = angle

    # 描画
    def draw(self):
        # 数字を描画する
        for number in self.numbers:
            for square_index in range(0, number.square_count()):
                a_x, a_y = number.corner_A(square_index)
                b_x, b_y = number.corner_B(square_index)
                c_x, c_y = number.corner_C(square_index)
                d_x, d_y = number.corner_D(square_index)

                # 影の描画を行う
                if number.is_enable_shadow is True:
                    path_s = ui.Path()
                    path_s.move_to(a_x + 5, a_y + 5)
                    path_s.line_to(b_x + 5, b_y + 5)
                    path_s.line_to(c_x + 5, c_y + 5)
                    path_s.line_to(d_x + 5, d_y + 5)

                    ui.set_color(number.shadow_color)
                    path_s.fill()

                path = ui.Path()
                path.move_to(a_x, a_y)
                path.line_to(b_x, b_y)
                path.line_to(c_x, c_y)
                path.line_to(d_x, d_y)

                ui.set_color(number.mycolor())
                path.fill()

        # 円を描画する
        path_r = ui.Path()
        path_r.move_to(350, 100)
        path_r.add_arc(100, 100, 250, 0, radians(self.round_angle))
        path_r.stroke()

        # 三角
        for triangle in self.triangles:
            a_x, a_y = triangle.corner_A()
            b_x, b_y = triangle.corner_B()
            c_x, c_y = triangle.corner_C()

            # 影の描画を行う
            if triangle.is_enable_shadow is True:
                path_t_s = ui.Path()
                path_t_s.move_to(a_x + 5, a_y + 5)
                path_t_s.line_to(b_x + 5, b_y + 5)
                path_t_s.line_to(c_x + 5, c_y + 5)

                ui.set_color(triangle.shadow_color)
                path_t_s.fill()

            path_t = ui.Path()
            path_t.move_to(a_x, a_y)
            path_t.line_to(b_x, b_y)
            path_t.line_to(c_x, c_y)

            ui.set_color(triangle.mycolor())
            path_t.fill()


# 円を描く
def round_schedule(main_view, round_angle):
    if isinstance(main_view, BaseView) is True:
        main_view.set_round_angle(round_angle)
        main_view.set_needs_display()

        if round_angle < 360:
            round_angle += 3

    if main_view.on_screen is True and round_angle <= 360:
        t = threading.Timer(0.02, round_schedule, args=[main_view, round_angle])
        t.start()


# 数字を縮小
def scale_schedule(main_view, index):
    if isinstance(main_view, BaseView) is True:
        number = main_view.numbers[index]
        scale = number.scale

        if scale > 1.1:
            scale -= 0.1
        else:
            scale = 1.0
            index += 1

        number.set_scale(scale)
        main_view.set_needs_display()

    if main_view.on_screen is True and index < len(main_view.numbers):
        t = threading.Timer(0.02, scale_schedule, args=[main_view, index])
        t.start()

    if main_view.on_screen is True and index >= len(main_view.numbers):
        t = threading.Timer(1.0, needle_scale_schedule, args=[main_view, 0])
        t.start()


# 針を縮小
def needle_scale_schedule(main_view, index):
    if isinstance(main_view, BaseView) is True:
        triangle = main_view.triangles[index]
        scale = triangle.scale

        if scale > 1.1:
            scale -= 0.1
        else:
            scale = 1.0
            index += 1

        triangle.set_scale(scale)
        main_view.set_needs_display()

    if main_view.on_screen is True and index < len(main_view.triangles):
        t = threading.Timer(0.02, needle_scale_schedule, args=[main_view, index])
        t.start()

    if main_view.on_screen is True and index >= len(main_view.triangles):
        t = threading.Timer(1.0, needle_rotate_schedule, args=[main_view, 0, 0])
        t.start()
        t2 = threading.Timer(16.0, number_rotate_schedule, args=[main_view, 0, 0])
        t2.start()


# 数字を回す
def number_rotate_schedule(main_view, angle, index):
    delay = 0.01
    if isinstance(main_view, BaseView) is True:
        if index < len(main_view.numbers):
            angle += 13
            if angle >= 360:
                angle = 0

            main_view.set_number_angle(angle, index)

            if angle == 0:
                index += 1
                delay = 0.5
            if index >= len(main_view.numbers):
                index = 0
                delay = 5.0

    if main_view.on_screen is True:
        t = threading.Timer(delay, number_rotate_schedule, args=[main_view, angle, index])
        t.start()
        pass


# 針を回す
def needle_rotate_schedule(main_view, l_angle, s_angle):
    if isinstance(main_view, BaseView) is True:
        if len(main_view.triangles) > 0:
            l_triangle = main_view.triangles[1]
            l_triangle.set_rotate_angle(l_angle)
            s_triangle = main_view.triangles[0]
            s_triangle.set_rotate_angle(s_angle)
            main_view.set_needs_display()
            l_angle = (l_angle + 1) % 360
            s_angle = (s_angle + (1.0 / 12)) % 360

    if main_view.on_screen is True:
        t = threading.Timer(0.02, needle_rotate_schedule, args=[main_view, l_angle, s_angle])
        t.start()
    pass


# 数字のパーツを落とす
def parts_parts_schedule(squares, fall_speed):
    for i in range(0, len(squares)):
        square = squares[i]
        if isinstance(square, Square) is True:
            square.A_y += fall_speed
            square.B_y += fall_speed
            square.C_y += fall_speed
            square.D_y += fall_speed
            fall_speed += 0.4

    if main_view.on_screen is True and fall_speed < 60.0:
        t = threading.Timer(0.02, parts_parts_schedule, args=[squares, fall_speed])
        t.start()
    pass


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '時計のような何か'
    main_view.background_color = 'lightblue'

    # 短針
    triangle_1 = Triangle(0, 140, 10, 0, 20, 140)
    triangle_1.set_shift(100, 100)
    triangle_1.set_center(-10, -130)
    triangle_1.set_scale(4.5)
    main_view.add_triangle(triangle_1)

    # 長針
    triangle_2 = Triangle(0, 240, 10, 0, 20, 240)
    triangle_2.set_shift(100, 100)
    triangle_2.set_center(-10, -230)
    triangle_2.set_scale(4.5)
    main_view.add_triangle(triangle_2)

    # Ⅱ
    number_2 = MyNumeral()
    number_2.set_shift(280, 0)
    square_2_0 = Square(0, 0, 10, 0, 10, 50, 0, 50)
    number_2.add_square(square_2_0)
    square_2_1 = Square(15, 0, 25, 0, 25, 50, 15, 50)
    number_2.add_square(square_2_1)
    number_2.set_center(-12.5, -25)
    number_2.set_scale(4.0)
    main_view.add_number(number_2)

    # Ⅲ
    number_3 = MyNumeral()
    number_3.set_shift(315, 100)
    square_3_0 = Square(0, 0, 10, 0, 10, 50, 0, 50)
    number_3.add_square(square_3_0)
    square_3_1 = Square(15, 0, 25, 0, 25, 50, 15, 50)
    number_3.add_square(square_3_1)
    square_3_2 = Square(30, 0, 40, 0, 40, 50, 30, 50)
    number_3.add_square(square_3_2)
    number_3.set_center(-20, -25)
    number_3.set_scale(4.0)
    main_view.add_number(number_3)

    # Ⅳ
    number_4 = MyNumeral()
    number_4.set_shift(280, 200)
    square_4_0 = Square(0, 0, 10, 0, 10, 50, 0, 50)
    number_4.add_square(square_4_0)
    number_4.add_square(Square(15, 0, 25, 0, 35, 50, 25, 50))
    number_4.add_square(Square(45, 0, 55, 0, 45, 50, 35, 50))
    number_4.set_center(-25, -25)
    number_4.set_scale(4.0)
    main_view.add_number(number_4)

    # Ⅴ
    number_5 = MyNumeral()
    number_5.set_shift(210, 285)
    square_5_0 = Square(0, 0, 10, 0, 20, 50, 10, 50)
    number_5.add_square(square_5_0)
    square_5_1 = Square(30, 0, 40, 0, 30, 50, 20, 50)
    number_5.add_square(square_5_1)
    number_5.set_center(-20, -25)
    number_5.set_scale(4.0)
    main_view.add_number(number_5)

    # Ⅵ
    number_6 = MyNumeral()
    number_6.set_shift(100, 310)
    square_6_0 = Square(0, 0, 10, 0, 20, 50, 10, 50)
    number_6.add_square(square_6_0)
    square_6_1 = Square(30, 0, 40, 0, 30, 50, 20, 50)
    number_6.add_square(square_6_1)
    square_6_2 = Square(45, 0, 55, 0, 55, 50, 45, 50)
    number_6.add_square(square_6_2)
    number_6.set_center(-22.5, -25)
    number_6.set_scale(4.0)
    main_view.add_number(number_6)

    # Ⅶ
    number_7 = MyNumeral()
    number_7.set_shift(-20, 285)
    square_7_0 = Square(0, 0, 10, 0, 20, 50, 10, 50)
    number_7.add_square(square_7_0)
    square_7_1 = Square(30, 0, 40, 0, 30, 50, 20, 50)
    number_7.add_square(square_7_1)
    square_7_2 = Square(45, 0, 55, 0, 55, 50, 45, 50)
    number_7.add_square(square_7_2)
    square_7_3 = Square(60, 0, 70, 0, 70, 50, 60, 50)
    number_7.add_square(square_7_3)
    number_7.set_center(-35, -25)
    number_7.set_scale(4.0)
    main_view.add_number(number_7)

    main_view.present()

    t1 = threading.Timer(0.02, round_schedule, args=[main_view, 0])
    t1.start()

    t2 = threading.Timer(6.0, scale_schedule, args=[main_view, 0])
    t2.start()

    t3 = threading.Timer(60.0, parts_parts_schedule, args=[[square_4_0], 0])
    t3.start()

    t4 = threading.Timer(90.0, parts_parts_schedule, args=[[square_6_1], 0])
    t4.start()

    t5 = threading.Timer(90.5, parts_parts_schedule, args=[[square_6_2], 0])
    t5.start()

    squares = [square_2_0, square_2_1,
               square_3_0, square_3_1, square_3_2,
               square_5_0, square_5_1,
               square_7_0, square_7_1, square_7_2, square_7_3, ]
    t6 = threading.Timer(105.0, parts_parts_schedule, args=[squares, 0])
    t6.start()