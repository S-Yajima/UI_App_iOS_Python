import ui
import threading
from math import cos
from math import sin
from math import radians
from math import isclose
from math import sqrt
from glyph import *
from figure import *
from dotmap import *


# Glyph Point Type
class TYPE():
    LINE = 'line'
    CURVE = 'curve'
    CONTROL = 'control'


# 文字
class Character(MyFigure):
    # points 座標の配列 [[[x,y,z,'type',flag],[x,y,z],...]]

    def __init__(self, contours):
        # 法線ベクトル取得の為の座標
        self.min_x = 500
        self.min_y = 500
        self.max_x = 500
        self.max_y = 500
        # 基本的なz座標は下記の値とする
        self.default_z = 1

        self.base_points = []
        for contour in contours:
            points = []
            for point in contour:
                work_list = []
                work_list.append(point[0])  # x座標
                work_list.append(point[1])  # y座標
                work_list.append(self.default_z)
                work_list.append(point[2])  # line/curve/control
                work_list.append(True)  # 表示/非表示
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


# 背景と床を描画する
class BaseView(ui.View):
    characters = []  # 文字の配列。一つのみのインスタンスなのでstaticメンバで定義する。

    is_Fill = True  # フォントを塗り潰す/塗り潰さない

    is_enable_title = False
    string_A_D = 'アメリカン・デジタル'
    string_A_D_s = '- オープンソースを利用したイノベーション -'
    string_C_D = 'チャイニーズ・デジタル'
    string_C_D_s = '- 国家主導型イノベーション -'
    string_E_D = 'ヨーロピアン・デジタル'
    string_E_D_s = '- ブランド力によるエンパワーメント -'
    string_T_D = 'サードウェーブ・デジタル'
    string_T_D_s = '- 一足飛びに生まれる新種のイノベーション -'

    surface = None
    screen_depth = 400  # 視点から投影面までの距離

    light_x = 150
    light_y = 150
    light_z = 600

    def add_character(self, character):
        self.characters.append(character)

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

    # glyph座標からフォントのアウトライン描画を行う
    # point   : 座標 x, y, z
    # control : 制御点 x, y, z
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

    # ui.draw_string()
    def draw_string(self):
        color = 'black'
        # uiのメソッドによるフォント描画
        with ui.GState():
            if self.is_enable_title is True:
                ui.set_shadow('gray', 1, 1, 0)
                ui.draw_string(self.string_A_D,
                               rect=(10, 10, 300, 20),
                               font=('HiraMinProN-W6', 20), color=color)
                ui.draw_string(self.string_A_D_s,
                               rect=(10, 30, 300, 10),
                               font=('HiraMinProN-W6', 10), color=color)
                ui.draw_string(self.string_C_D,
                               rect=(350, 10, 300, 20),
                               font=('HiraMinProN-W6', 20), color=color)
                ui.draw_string(self.string_C_D_s,
                               rect=(350, 30, 300, 10),
                               font=('HiraMinProN-W6', 10), color=color)
                ui.draw_string(self.string_T_D,
                               rect=(10, 150, 300, 20),
                               font=('HiraMinProN-W6', 20), color=color)
                ui.draw_string(self.string_T_D_s,
                               rect=(10, 170, 300, 10),
                               font=('HiraMinProN-W6', 10), color=color)
                ui.draw_string(self.string_E_D,
                               rect=(350, 135, 300, 20),
                               font=('HiraMinProN-W6', 20), color=color)
                ui.draw_string(self.string_E_D_s,
                               rect=(350, 155, 300, 10),
                               font=('HiraMinProN-W6', 10), color=color)

            for character in self.characters:
                if character.is_enable_name is True:
                    ui.draw_string(character.name_string, rect=(character.name_x, character.name_y, 300, 15),
                                   font=('HiraMinProN-W6', 15), color=color)

    # 色を表す文字列と内積の値からuiにRGBの値を設定する
    def set_ui_color(self, color, inner):
        if color == 'blue':
            ui.set_color((0.3, 0.3, (inner * -1), 1.0))
        elif color == 'darkblue':
            ui.set_color((0.3, 0.3, (inner * -1) - 0.2, 1.0))
        elif color == 'green':
            ui.set_color((0.3, (inner * -1), 0.3, 1.0))
        elif color == 'red':
            ui.set_color(((inner * -1), 0.0, 0.0, 1.0))
        elif color == 'yellow':
            ui.set_color(((inner * -1), (inner * -1), 0.3, 1.0))
        elif color == 'brown':
            ui.set_color(((inner * -1) - 0.3, (inner * -1) - 0.8, (inner * -1) - 0.8, 1.0))
        elif color == 'silver':
            ui.set_color(((inner * -1) - 0.05, (inner * -1) - 0.05, (inner * -1) - 0.05, 1.0))
        elif color == 'black':
            ui.set_color(((inner * -1) - 0.7, (inner * -1) - 0.7, (inner * -1) - 0.7, 1.0))
        elif color == 'orange':
            ui.set_color(((inner * -1), (inner * -1) - 0.2, 0.2, 1.0))
        else:
            ui.set_color((0.0, 0.0, 0.0, 1.0))

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
        self.draw_string()

        # 文字を描画する
        for character in self.characters:
            # [[x,y,z,type,flag],[],...],[]
            contours = character.glyph(self.height)

            # 法線ベクトルの為の座標を取得
            point_for_vector = character.point_for_vector(self.height)
            # A→B、A→Cのベクトルを算出する
            font_v1 = [
                point_for_vector[1][0] - point_for_vector[0][0],
                point_for_vector[1][1] - point_for_vector[0][1],
                point_for_vector[1][2] - point_for_vector[0][2]]
            font_v2 = [
                point_for_vector[2][0] - point_for_vector[0][0],
                point_for_vector[2][1] - point_for_vector[0][1],
                point_for_vector[2][2] - point_for_vector[0][2]]

            # フォントの外積を算出し法線を取得する
            font_cross_vector = cross_product(font_v1, font_v2)
            # フォントの法線ベクトルを正規化する
            font_normal_vector = normalize(font_cross_vector)

            # フォントから視点焦点へのベクトルを算出する
            scr_vector = [
                self.width / 2 - (point_for_vector[0][0] + point_for_vector[1][0] + point_for_vector[2][0]) / 3,
                self.height / 2 - (point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3,
                self.screen_depth - (point_for_vector[0][2] + point_for_vector[1][2] + point_for_vector[2][2]) / 3]
            # 視点焦点までのベクトルを正規化する
            scr_normal_vector = normalize(scr_vector)
            # 正規化したフォントの法線ベクトルと視点焦点ベクトルとの内積を取得する
            scr_inner = dot_product(font_normal_vector, scr_normal_vector)

            # フォントから光源までのベクトルを算出する
            light_vector = [
                self.light_x - (point_for_vector[0][0] + point_for_vector[1][0] + point_for_vector[2][0]) / 3,
                self.light_y - (point_for_vector[0][1] + point_for_vector[1][1] + point_for_vector[2][1]) / 3,
                self.light_z - (point_for_vector[0][2] + point_for_vector[1][2] + point_for_vector[2][2]) / 3]
            # フォントから光源までのベクトルを正規化する
            light_normal_vector = normalize(light_vector)
            # 正規化したフォントの法線ベクトルと光源ベクトルとの内積を取得する
            light_inner = dot_product(font_normal_vector, light_normal_vector)

            # フォントを描画する
            for points in contours:
                if len(points) < 3:
                    continue

                path = ui.Path()
                # 最初のglyph座標
                p_x, p_y = self.projection(points[0][0], points[0][1], points[0][2])
                path.move_to(p_x, p_y)

                controls = []  # 制御点を格納する
                # 2番目以降のglyph座標
                for i in range(1, len(points)):
                    self.draw_glyph(points[i], controls, path)

                # 最後のglyph座標
                self.draw_glyph(points[0], controls, path)

                # 使用しているフォントの
                if scr_inner < 0.0:
                    self.set_ui_color(
                        character.mycolor(), light_inner)
                else:
                    ui.set_color('black')
                path.fill()


# font をY軸に回転させる
# 一周するまで本関数が繰り返し呼ばれる
# 回転中に文字の「文字列を表示するフラグ」を設定する
def rotate_y_font_schedule(main_view, character):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(character, Character) is False:
        return

    character.rotate_angle_y += 10
    if character.rotate_angle_y >= 360:
        character.set_angle_y(0)

    if character.rotate_angle_y >= 270 and character.rotate_angle_y < 290:
        character.set_enable_name(True)

    main_view.set_needs_display()

    if main_view.on_screen is True and character.rotate_angle_y > 0:
        t = threading.Timer(0.02, rotate_y_font_schedule, args=[main_view, character])
        t.start()


# font x軸に回転させる
# 一周するまで本関数が繰り返し呼ばれる
def rotate_x_font_schedule(main_view, character):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(character, Character) is False:
        return

    character.rotate_angle_x += 10
    if character.rotate_angle_x >= 360:
        character.set_angle_x(0)

    main_view.set_needs_display()

    if main_view.on_screen is True and character.rotate_angle_x > 0:
        t = threading.Timer(0.02, rotate_x_font_schedule, args=[main_view, character])
        t.start()


# font を縮小する
# minimam scale 0.06 で設定する
def scaledown_schedule(main_view, character, scale, min_scale):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(character, Character) is False:
        return

    scale -= 0.01
    character.set_scale(scale)
    main_view.set_needs_display()

    if main_view.on_screen is True and scale > min_scale and not isclose(scale, min_scale, rel_tol=0.01):
        t = threading.Timer(0.02, scaledown_schedule, args=[main_view, character, scale, min_scale])
        t.start()


# 文字を縦一例に並べる
# 縮小しながら縦一例に整列する
def queue_font_schedule(
        main_view, character, from_scale, min_scale,
        from_shift_x, from_shift_y,
        to_shift_x, to_shift_y):
    if isinstance(main_view, BaseView) is False:
        return
    if isinstance(character, Character) is False:
        return

    scale = character.scale
    scale -= 0.001
    character.set_scale(scale)

    # 現在の縮小値でのx、y座標を計算し設定する
    x = (scale - min_scale) * (from_shift_x - to_shift_x) / (from_scale - min_scale) + to_shift_x
    character.shift_x = x
    y = (scale - min_scale) * (from_shift_y - to_shift_y) / (from_scale - min_scale) + to_shift_y
    character.shift_y = y

    main_view.set_needs_display()

    if main_view.on_screen is True and \
            scale > min_scale and \
            not isclose(scale, min_scale, rel_tol=0.001):
        # 目的のscaleになるまで繰り返す
        t = threading.Timer(0.01, queue_font_schedule,
                            args=[main_view, character, from_scale, min_scale, from_shift_x, from_shift_y,
                                  to_shift_x, to_shift_y])
        t.start()


# 地図を倒す
def rotate_map_schedule(map_view, angle):
    if isinstance(map_view, MyMapView) is False:
        return

    angle += 10
    map_view.map.set_angle_x(angle)
    if angle >= 70:
        map_view.superview.is_enable_title = True
        map_view.superview.set_needs_display()

    map_view.set_needs_display()

    if map_view.on_screen is True and 70 > angle:
        t = threading.Timer(0.02, rotate_map_schedule, args=[map_view, angle])
        t.start()


# 地図を横方向と手前／奥方向に動かす
def shift_map_schedule(map_view, to_x, to_z):
    if isinstance(map_view, MyMapView) is False:
        return

    x = map_view.map.shift_x
    y = map_view.map.shift_y
    z = map_view.map.shift_z

    move_length = 50

    if abs(to_x - x) <= move_length:
        x = to_x
    elif x < to_x:
        x += move_length
    elif x > to_x:
        x -= move_length

    if abs(to_z - z) <= move_length:
        z = to_z
    elif z < to_z:
        z += move_length
    elif z > to_z:
        z -= move_length

    map_view.map.set_shift(x, y, z)
    map_view.set_needs_display()

    if map_view.on_screen is True and (x != to_x or z != to_z):
        t = threading.Timer(0.02, shift_map_schedule, args=[map_view, to_x, to_z])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '世界の4つのデジタルイデオロギー'
    main_view.background_color = 'lightblue'

    # 水面
    surface = Surface(-300, 300, 0, 300, 300, 0, 300, 0, 0, -300, 0, 0)
    surface.set_center(0, 0, 0)
    surface.set_shift(330, 330, 0)
    surface.set_scale(1)
    surface.set_angle_x(270)
    main_view.set_surface(surface)

    # map
    map = MyMap(dots())
    map.set_scale(0.6)
    # map.set_scale(1.0)
    map.set_shift(0, 0, 0)
    map.set_angle_x(0)
    map.set_center(0, -370, 0)
    map_view = MyMapView(frame=(50, 100, 554, 267))
    map_view.set_map(map)
    main_view.add_subview(map_view)

    # Font
    start_scale = 0.15
    center_scale = 0.06
    queue_scale = 0.014

    char_A_G = Character(glyph_G())
    char_A_G.set_center(-600, -600, 0)
    char_A_G.set_shift(1500, 3000, 0)
    char_A_G.set_scale(start_scale)
    char_A_G.set_name_string('oogle', 50, 47)
    char_A_G.set_color('red')
    main_view.add_character(char_A_G)

    char_A_Ap = Character(glyph_A())
    char_A_Ap.set_center(-600, -600, 0)
    char_A_Ap.set_shift(2800, 3000, 0)
    char_A_Ap.set_scale(start_scale)
    char_A_Ap.set_name_string('pple', 50, 68)
    char_A_Ap.set_color('silver')
    main_view.add_character(char_A_Ap)

    char_A_F = Character(glyph_F())
    char_A_F.set_center(-600, -600, 0)
    char_A_F.set_shift(4100, 3000, 0)
    char_A_F.set_scale(start_scale)
    char_A_F.set_name_string('acebook', 50, 90)
    char_A_F.set_color('blue')
    main_view.add_character(char_A_F)

    char_A_Am = Character(glyph_A())
    char_A_Am.set_center(-600, -600, 0)
    char_A_Am.set_shift(5200, 3000, 0)
    char_A_Am.set_scale(start_scale)
    char_A_Am.set_name_string('mazon', 50, 110)
    char_A_Am.set_color('orange')
    main_view.add_character(char_A_Am)

    char_A_M = Character(glyph_M())
    char_A_M.set_center(-600, -600, 0)
    char_A_M.set_shift(6500, 3000, 0)
    char_A_M.set_scale(start_scale)
    char_A_M.set_name_string('icrosoft   etc...', 50, 130)
    char_A_M.set_color('blue')
    main_view.add_character(char_A_M)

    america_list = [
        char_A_G, char_A_Ap, char_A_F,
        char_A_Am, char_A_M]

    char_C_B = Character(glyph_B())
    char_C_B.set_center(-600, -600, 0)
    char_C_B.set_shift(3000, 3000, 0)
    char_C_B.set_scale(start_scale)
    char_C_B.set_name_string('aido', 390, 47)
    char_C_B.set_color('red')
    main_view.add_character(char_C_B)

    char_C_Al = Character(glyph_A())
    char_C_Al.set_center(-600, -600, 0)
    char_C_Al.set_shift(4300, 3000, 0)
    char_C_Al.set_scale(start_scale)
    char_C_Al.set_name_string('libaba', 390, 68)
    char_C_Al.set_color('yellow')
    main_view.add_character(char_C_Al)

    char_C_T = Character(glyph_T())
    char_C_T.set_center(-600, -600, 0)
    char_C_T.set_shift(5600, 3000, 0)
    char_C_T.set_scale(start_scale)
    char_C_T.set_name_string('encent', 390, 90)
    char_C_T.set_color('blue')
    main_view.add_character(char_C_T)

    char_C_H = Character(glyph_H())
    char_C_H.set_center(-600, -600, 0)
    char_C_H.set_shift(6900, 3000, 0)
    char_C_H.set_scale(start_scale)
    char_C_H.set_name_string('uawey   etc...', 390, 110)
    char_C_H.set_color('orange')
    main_view.add_character(char_C_H)

    chinese_list = [
        char_C_B, char_C_Al, char_C_T, char_C_H]

    char_E_Le = Character(glyph_L())
    char_E_Le.set_center(-600, -600, 0)
    char_E_Le.set_shift(3000, 3000, 0)
    char_E_Le.set_scale(start_scale)
    char_E_Le.set_name_string('eica', 390, 170)
    char_E_Le.set_color('red')
    main_view.add_character(char_E_Le)

    char_E_Lv = Character(glyph_L())
    char_E_Lv.set_center(-600, -600, 0)
    char_E_Lv.set_shift(4300, 3000, 0)
    char_E_Lv.set_scale(start_scale)
    char_E_Lv.set_name_string('VMH', 390, 190)
    char_E_Lv.set_color('brown')
    main_view.add_character(char_E_Lv)

    char_E_C = Character(glyph_C())
    char_E_C.set_center(-600, -600, 0)
    char_E_C.set_shift(5600, 3000, 0)
    char_E_C.set_scale(start_scale)
    char_E_C.set_name_string('arl Zeiss', 390, 210)
    char_E_C.set_color('darkblue')
    main_view.add_character(char_E_C)

    char_E_Me = Character(glyph_M())
    char_E_Me.set_center(-600, -600, 0)
    char_E_Me.set_shift(6900, 3000, 0)
    char_E_Me.set_scale(start_scale)
    char_E_Me.set_name_string('ercedes-Benz   etc...', 390, 230)
    char_E_Me.set_color('black')
    main_view.add_character(char_E_Me)

    european_list = [
        char_E_Le, char_E_Lv, char_E_C, char_E_Me]

    char_T_T = Character(glyph_T())
    char_T_T.set_center(-600, -600, 0)
    char_T_T.set_shift(4300, 3000, 0)
    char_T_T.set_scale(start_scale)
    char_T_T.set_name_string('ata Motors', 50, 190)
    char_T_T.set_color('blue')
    main_view.add_character(char_T_T)

    char_T_M = Character(glyph_M())
    char_T_M.set_center(-600, -600, 0)
    char_T_M.set_shift(5600, 3000, 0)
    char_T_M.set_scale(start_scale)
    char_T_M.set_name_string('-pesa   etc...', 50, 210)
    char_T_M.set_color('green')
    main_view.add_character(char_T_M)
    thirdwave_list = [char_T_T, char_T_M]

    main_view.present()

    # map を倒す
    delay = 3.0
    t1 = threading.Timer(1.0, rotate_map_schedule, args=[map_view, 0])
    t1.start()

    # アメリカンデジタル
    delay += 4.0
    t2 = threading.Timer(delay, shift_map_schedule, args=[map_view, -250, 350])
    t2.start()

    delay += 4.0
    for character in america_list:
        t = threading.Timer(delay, scaledown_schedule, args=[main_view, character, start_scale, center_scale])
        t.start()
        delay += 0.1

    delay += 1.0
    for character in america_list:
        t = threading.Timer(delay, rotate_x_font_schedule, args=[main_view, character])
        t.start()
        delay += 0.1

    delay += 2.0
    index = 0
    america_to_point_list = [[1000, 20000], [1000, 18500], [1000, 17000], [1000, 15500], [1000, 14000]]
    for character in america_list:
        t = threading.Timer(delay, queue_font_schedule,
                            args=[main_view, character,
                                  center_scale, queue_scale,
                                  character.shift_x, character.shift_y,
                                  america_to_point_list[index][0],
                                  america_to_point_list[index][1]])
        t.start()
        index += 1
        delay += 0.1

    delay += 3.0
    for character in america_list:
        t = threading.Timer(delay, rotate_y_font_schedule, args=[main_view, character])
        t.start()
        delay += 1.0

    # チャイニーズデジタル
    delay += 4.0
    t3 = threading.Timer(delay, shift_map_schedule, args=[map_view, 180, 300])
    t3.start()

    delay += 4.5
    for character in chinese_list:
        t = threading.Timer(delay, scaledown_schedule, args=[main_view, character, start_scale, center_scale])
        t.start()
        delay += 0.1

    delay += 1.0
    for character in chinese_list:
        t = threading.Timer(delay, rotate_x_font_schedule, args=[main_view, character])
        t.start()
        delay += 0.1

    delay += 2.0
    index = 0
    chinese_to_point_list = [
        [25500, 20000], [25500, 18500],
        [25500, 17000], [25500, 15500]]

    for character in chinese_list:
        t = threading.Timer(
            delay, queue_font_schedule,
            args=[main_view, character,
                  center_scale, queue_scale,
                  character.shift_x, character.shift_y,
                  chinese_to_point_list[index][0],
                  chinese_to_point_list[index][1]])
        t.start()
        index += 1
        delay += 0.1

    delay += 3.0
    for character in chinese_list:
        t = threading.Timer(delay, rotate_y_font_schedule, args=[main_view, character])
        t.start()
        delay += 1.0

    # ヨーロピアンデジタル
    delay += 4.0
    t4 = threading.Timer(delay, shift_map_schedule, args=[map_view, 330, 400])
    t4.start()

    delay += 3.0
    for character in european_list:
        t = threading.Timer(delay, scaledown_schedule, args=[main_view, character, start_scale, center_scale])
        t.start()
        delay += 0.1

    delay += 1.0
    for character in european_list:
        t = threading.Timer(delay, rotate_x_font_schedule, args=[main_view, character])
        t.start()
        delay += 0.1

    delay += 2.0
    index = 0
    european_to_point_list = [
        [25500, 11000], [25500, 9500],
        [25500, 8000], [25500, 6500]]

    for character in european_list:
        t = threading.Timer(delay, queue_font_schedule,
                            args=[main_view, character,
                                  center_scale, queue_scale,
                                  character.shift_x, character.shift_y,
                                  european_to_point_list[index][0],
                                  european_to_point_list[index][1]])
        t.start()
        index += 1
        delay += 0.1

    delay += 3.0
    for character in european_list:
        t = threading.Timer(delay, rotate_y_font_schedule, args=[main_view, character])
        t.start()
        delay += 1.0

    # サードウェーブデジタル
    delay += 4.0
    t5 = threading.Timer(delay, shift_map_schedule, args=[map_view, 250, 100])
    t5.start()

    delay += 3.0
    for character in thirdwave_list:
        t = threading.Timer(delay, scaledown_schedule, args=[main_view, character, start_scale, center_scale])
        t.start()
        delay += 0.1

    delay += 1.0
    for character in thirdwave_list:
        t = threading.Timer(delay, rotate_x_font_schedule, args=[main_view, character])
        t.start()
        delay += 0.1

    delay += 2.0
    index = 0
    thirdwave_to_point_list = [
        [1000, 9500], [1000, 8000]]

    for character in thirdwave_list:
        t = threading.Timer(delay, queue_font_schedule,
                            args=[main_view, character,
                                  center_scale, queue_scale,
                                  character.shift_x, character.shift_y,
                                  thirdwave_to_point_list[index][0],
                                  thirdwave_to_point_list[index][1]])
        t.start()
        index += 1
        delay += 0.1

    delay += 3.0
    for character in thirdwave_list:
        t = threading.Timer(delay, rotate_y_font_schedule, args=[main_view, character])
        t.start()
        delay += 1.0

    # 最後に地図を元の位置に戻す
    delay += 4.0
    t6 = threading.Timer(delay, shift_map_schedule, args=[map_view, 0, 0])
    t6.start()
