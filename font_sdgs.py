import ui
import threading
from math import cos
from math import sin
from math import radians


# Glyph Point Type
class TYPE():
    LINE = 'line'
    CURVE = 'curve'
    CONTROL = 'control'


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
class Surface(MyFigure):
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


# 文字
class Character(MyFigure):
    # points 座標の配列 [[[x,y,z,'type',flag],[x,y,z],...]]

    def __init__(self, contours):
        self.base_points = []
        for contour in contours:
            points = []
            for point in contour:
                work_list = []
                work_list.append(point[0])
                work_list.append(point[1])
                work_list.append(1)
                work_list.append(point[2])
                work_list.append(False)
                points.append(work_list)

            self.base_points.append(points)

    # 文字の描画のための3D座標を返す
    def glyph(self, screen_height):
        r_points = []

        for contours in self.base_points:
            points = []
            for point in contours:
                x, y, z = self.queue(point[0], point[1], point[2])

                # y軸が上下逆転しているので吸収する
                y = screen_height - y

                points.append([x, y, z, point[3], point[4]])
            r_points.append(points)

        return r_points


# 背景と床を描画する
class BaseView(ui.View):
    characters = []  # 文字の配列。一つのみのインスタンスなのでstaticメンバで定義する。

    is_Fill = False  # フォントを塗り潰す/塗り潰さない
    string_S = 'ustainable'
    string_D = 'evelopment'
    string_G = 'oal'

    surface = None
    screen_depth = 400  # 視点から投影面までの距離

    def add_character(self, character):
        self.characters.append(character)

    def set_surface(self, surface):
        self.surface = surface

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

    # glyph座標からフォントのアウトライン描画を行う
    # point  : 座標 x, y, z
    # control: 制御点 x, y, z
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
    # points : 座標[[x,y,z,type,flag],[x,y,z,type,flag],...
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

        # uiのメソッドによるフォント描画
        with ui.GState():
            ui.set_shadow('gray', 10, 10, 0)
            ui.draw_string(self.string_S, rect=(130, 130, 300, 40),
                            font=('HiraMinProN-W6', 30), color='black')
            ui.draw_string(self.string_D, rect=(130, 290, 300, 40),
                            font=('HiraMinProN-W6', 30), color='black')
            ui.draw_string(self.string_G, rect=(130, 450, 300, 40),
                            font=('HiraMinProN-W6', 30), color='black')

        # 文字を描画する
        for character in self.characters:
            # [[x,y,z,type,flag],[],...],[]
            contours = character.glyph(self.height)

            # フォントを描画する
            for points in contours:
                if len(points) < 1:
                    continue

                # 座標点、制御点を描画する
                # line,curve 黒塗り
                # control 白抜き
                if self.is_Fill is False:
                    self.draw_glyph_points(points)

                path = ui.Path()
                # 最初のglyph座標
                if points[0][4] is True:
                    p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
                    path.move_to(p_x, p_y)
                else:
                    continue

                controls = []  # 制御点を格納する
                # 2番目以降のglyph座標
                for i in range(1, len(points)):
                    if points[i][4] is True:
                        self.draw_glyph(points[i], controls, path)

                # 最後のglyph座標
                self.draw_glyph(points[0], controls, path)

                ui.set_color('black')
                if self.is_Fill is True:
                    path.fill()
                else:
                    path.stroke()


# 文字を移動させる
def move_font_schedule(main_view, index):
    if isinstance(main_view, BaseView) is False:
        return

    goal_x = [0, 0, 0, 3800]
    goal_y = [5000, 3000, 1000, 1600]
    if len(goal_y) <= index:
        return

    is_complete = False

    character = main_view.characters[index]
    character.shift_x -= 50

    if character.shift_x - goal_x[index] < 10 or character.shift_x < goal_x[index]:
        character.shift_x = goal_x[index]
        character.shift_y += 50

        if goal_y[index] - character.shift_y < 10 or character.shift_y > goal_y[index]:
            character.shift_y = goal_y[index]
            is_complete = True
            # index += 1

    main_view.set_needs_display()

    if main_view.on_screen is True and len(goal_y) > index and is_complete is False:
        t = threading.Timer(0.02, move_font_schedule, args=[main_view, index])
        t.start()


# font を回転させる
def rotate_font_schedule(main_view, index):
    if isinstance(main_view, BaseView) is False:
        return

    if len(main_view.characters) <= index:
        return

    character = main_view.characters[index]
    character.rotate_angle_x += 10
    if character.rotate_angle_x >= 360:
        character.rotate_angle_x = 0
        index += 1

    main_view.set_needs_display()

    if main_view.on_screen is True and len(main_view.characters) > index:
        t = threading.Timer(0.02, rotate_font_schedule, args=[main_view, index])
        t.start()
    elif main_view.on_screen is True and len(main_view.characters) <= index:
        for i in range(len(main_view.characters)):
            t2 = threading.Timer(2.0 + (i * 0.8), move_font_schedule, args=[main_view, i])
            t2.start()


# fontを塗り潰すフラグを設定する
def fill_font_schedule(main_view):
    if isinstance(main_view, BaseView) is False:
        return

    main_view.is_Fill = True
    main_view.set_needs_display()

    if main_view.on_screen is True:
        t = threading.Timer(2.0, rotate_font_schedule, args=[main_view, 0])
        t.start()


# 座標点、制御点を描画する
# flag がFalseの座標点を一つTrueに変更して抜け出す
# index Characterのindex
def draw_point_schedule(main_view, index):
    if isinstance(main_view, BaseView) is False:
        return

    if len(main_view.characters) <= index:
        return

    # 対象の文字の座標点を一つTrueに変更する
    character = main_view.characters[index]
    for contours in character.base_points:
        for points in contours:
            if points[4] is False:
                points[4] = True

                main_view.set_needs_display()

                t = threading.Timer(0.2, draw_point_schedule, args=[main_view, index])
                t.start()
                return

    # 全ての座標のフラグがTrueであった場合この行に到達する
    index += 1

    if main_view.on_screen is True and len(main_view.characters) > index:
        t2 = threading.Timer(3.0, draw_point_schedule, args=[main_view, index])
        t2.start()
    # 全ての文字の座標がTrueの場合
    elif main_view.on_screen is True and len(main_view.characters) <= index:
        # 文字を塗り潰す処理を準備する
        t3 = threading.Timer(3.0, fill_font_schedule, args=[main_view])
        t3.start()


def glyph_S():
    return ([[
            [869, 387, 'curve'], [869, 309, 'control'], [809, 244, 'control'], [669, 244, 'curve'],
            [502, 244, 'control'], [402, 301, 'control'], [402, 472, 'curve'], [66, 472, 'line'],
            [66, 127, 'control'], [373, -20, 'control'], [669, -20, 'curve'], [993, -20, 'control'],
            [1204, 127, 'control'], [1204, 389, 'curve'], [1204, 634, 'control'], [1030, 772, 'control'],
            [718, 870, 'curve'], [545, 924, 'control'], [444, 977, 'control'], [444, 1064, 'curve'],
            [444, 1144, 'control'], [515, 1211, 'control'], [656, 1211, 'curve'], [800, 1211, 'control'],
            [870, 1134, 'control'], [870, 1024, 'curve'], [1204, 1024, 'line'], [1204, 1299, 'control'],
            [983, 1476, 'control'], [663, 1476, 'curve'], [343, 1476, 'control'], [110, 1317, 'control'],
            [110, 1067, 'curve'], [110, 805, 'control'], [344, 685, 'control'], [603, 600, 'curve'],
            [827, 527, 'control'], [869, 478, 'control']
        ]])


def glyph_D():
    return ([[
            [581, 0, 'line'], [973, 0, 'control'], [1251, 285, 'control'], [1251, 697, 'curve'],
            [1251, 758, 'line'], [1251, 1170, 'control'], [973, 1456, 'control'], [579, 1456, 'curve'],
            [255, 1456, 'line'], [255, 1185, 'line'], [579, 1185, 'line'], [794, 1185, 'control'],
            [910, 1039, 'control'], [910, 760, 'curve'], [910, 697, 'line'], [910, 416, 'control'],
            [793, 270, 'control'], [581, 270, 'curve'], [263, 270, 'line'], [261, 0, 'line'],
    ], [
            [452, 1456, 'line'], [117, 1456, 'line'], [117, 0, 'line'], [452, 0, 'line']
    ]])


def glyph_G():
    return ([[
            [1296, 778, 'line'], [708, 778, 'line'], [708, 537, 'line'], [961, 537, 'line'],
            [961, 311, 'line'], [931, 284, 'control'], [868, 250, 'control'], [746, 250, 'curve'],
            [529, 250, 'control'], [426, 396, 'control'], [426, 687, 'curve'], [426, 770, 'line'],
            [426, 1063, 'control'], [535, 1207, 'control'], [715, 1207, 'curve'], [883, 1207, 'control'],
            [951, 1125, 'control'], [972, 981, 'curve'], [1295, 981, 'line'], [1265, 1272, 'control'],
            [1098, 1477, 'control'], [704, 1477, 'curve'], [340, 1477, 'control'], [86, 1221, 'control'],
            [86, 768, 'curve'], [86, 687, 'line'], [86, 234, 'control'], [340, -20, 'control'],
            [724, -20, 'curve'], [1040, -20, 'control'], [1223, 98, 'control'], [1296, 180, 'curve']
        ]])


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '持続可能な開発目標'
    main_view.background_color = 'lightblue'

    # Font
    character_S = Character(glyph_S())
    character_S.set_center(0, -600, 0)
    character_S.set_shift(0, 1000, 0)
    character_S.set_scale(0.08)
    main_view.add_character(character_S)

    character_D = Character(glyph_D())
    character_D.set_center(0, -600, 0)
    character_D.set_shift(1200, 1000, 0)
    character_D.set_scale(0.08)
    main_view.add_character(character_D)

    character_G = Character(glyph_G())
    character_G.set_center(0, -600, 0)
    character_G.set_shift(2500, 1000, 0)
    character_G.set_scale(0.08)
    main_view.add_character(character_G)

    character_S_s = Character(glyph_S())
    character_S_s.set_center(0, -600, 0)
    character_S_s.set_shift(6200, 1600, 0)
    character_S_s.set_scale(0.05)
    main_view.add_character(character_S_s)

    # 水面
    surface = Surface(-250, 300, 0, 250, 300, 0, 250, 0, 0, -250, 0, 0)
    surface.set_center(0, 0, 0)
    surface.set_shift(190, 540, 0)
    surface.set_scale(1)
    surface.set_angle_x(270)
    main_view.set_surface(surface)

    main_view.present()

    t = threading.Timer(1.0, draw_point_schedule, args=[main_view, 0])
    t.start()