import ui
import threading
import math


# 背景と床を描画する
class BaseView(ui.View):
    floor_color = 'blue'
    floor_angle = 90  # 床の傾き

    # 床描画の起点、角の座標
    floor_front_left_x = 10.0
    floor_front_left_y = 500.0
    floor_front_right_x = 370.0
    floor_front_right_y = 500.0

    floor_back_left_x = 100.0
    floor_back_left_y = 410.0
    floor_back_right_x = 280.0
    floor_back_right_y = 410.0

    def floor_height(self):
        return (360)

    def floor_width(self):
        return (self.floor_front_right_x - self.floor_front_left_x)

    def floor_front_x(self):
        return (self.floor_front_left_x)

    def floor_front_y(self):
        return (self.floor_front_right_y)

    def floor_back_y(self):
        return (self.floor_back_right_y)

    def set_floor_angle(self, angle):
        self.floor_angle = angle

    def rotate_floor(self):
        floor_height = self.floor_height()

        # 角度から、床の傾きを計算する
        cos_x = math.cos(math.radians(self.floor_angle)) * (floor_height / 4)
        sin_y = math.sin(math.radians(self.floor_angle)) * floor_height

        self.floor_back_left_x = self.floor_front_left_x + cos_x
        self.floor_back_left_y = self.floor_front_left_y - sin_y
        self.floor_back_right_x = self.floor_front_right_x - cos_x
        self.floor_back_right_y = self.floor_front_right_y - sin_y

        self.set_needs_display()

    # 描画
    def draw(self):
        path = ui.Path()
        path.move_to(self.floor_front_left_x, self.floor_front_left_y)
        path.line_to(self.floor_back_left_x, self.floor_back_left_y)
        path.line_to(self.floor_back_right_x, self.floor_back_right_y)
        path.line_to(self.floor_front_right_x, self.floor_front_right_y)

        ui.set_color(self.floor_color)
        path.stroke()
        path.fill()
        pass


# 円を描画するView
# 進行方向の角度と速度、色を保持する
# 円の描画はdraw()メソッド内で.ui.Pathクラスにて行う
class BallView(ui.View):
    draw_color = 'yellow'
    angle = 0           # 円が動く角度
    speed = 1           # 円が動く速度
    falling_speed = 0
    is_on_floor = False

    ball_x = 0          # 円の実際のx, y位置座標
    ball_y = 0
    ball_diameter = 60  # 円の実際の直径

    movement_x = 1.0    # 角度から算出するspeed 1 ごとにx軸に動く量
    movement_y = 0.0    # 角度から算出するspeed 1 ごとにy軸に動く量

    # 円の中心のx座標を返す
    def center_x(self):
        return (self.ball_x + (self.ball_diameter / 2))

    # 円の中心のy座標を返す
    def center_y(self):
        return (self.ball_y + (self.ball_diameter / 2))

    def set_point_diameter(self, x, y, diameter):
        self.ball_x = x
        self.ball_y = y
        self.ball_diameter = diameter
        pass

    # 移動速度と角度,色を設定する
    def set_speed_angle_color(self, speed, angle, draw_color):
        self.speed = speed
        self.angle = angle
        self.draw_color = draw_color
        self.calc_movement()

    def upper_right(self):
        return (self.ball_x + self.ball_diameter)

    def lower_left(self):
        return (self.ball_y + self.ball_diameter)

    # 角度と速度から、x軸y軸に動く長さを計算する
    # x軸= cos 角度
    # y軸= sin 角度
    def calc_movement(self):
        if self.angle == 0:
            self.movement_x = 1.0
            self.movement_y = 0.0
        elif self.angle == 90:
            self.movement_x = 0.0
            self.movement_y = 1.0
        elif self.angle == 180:
            self.movement_x = -1.0
            self.movement_y = 0.0
        elif self.angle == 270:
            self.movement_x = 0.0
            self.movement_y = -1.0
        else:
            self.movement_x = math.cos(math.radians(self.angle))
            self.movement_y = math.sin(math.radians(self.angle))

    # 接触した壁の角度から、反射角度を計算して設定する
    def angle_with_wallangle(self, wallangle):
        new_angle = (self.angle + ((wallangle - self.angle) * 2)) % 360
        # print(new_angle)
        return new_angle

    # 中心同士の角度を計算して返す
    def center_angle(self, diff_x, diff_y):
        # 中心同士のx軸とy軸の位置の差分からatan()で角度を算出する
        center_angle = 90
        if diff_x != 0:  # ゼロ割り算を防ぐ
            center_angle = int(math.degrees(math.atan(diff_y / diff_x)))

        # 接触した円の位置関係から360°角度に変更する
        if diff_x < 0 and diff_y > 0:
            center_angle = (90 - abs(center_angle)) + 90
        elif diff_x < 0 and diff_y < 0:
            center_angle = abs(center_angle) + 180
        elif diff_x > 0 and diff_y < 0:
            center_angle = 360 + center_angle

        return center_angle

    # 円同士の接触と反射を処理する
    def reflect_subview(self):
        for subview in self.superview.subviews:
            if id(self) != id(subview) and subview.is_on_floor == True:
                # 中心同士の距離を算出する
                diff_x = subview.center_x() - self.center_x()
                diff_y = subview.center_y() - self.center_y()
                diff_center = math.sqrt(abs(diff_x) ** 2 + abs(diff_y) ** 2)
                # 接触している場合
                if (self.ball_diameter + subview.ball_diameter) / 2 >= diff_center:
                    # 中心同士を結んだ線の角度
                    theta_center = self.center_angle(diff_x, diff_y)
                    diff_wall_angle = 90

                    # 進行方向の後方から接触されたかを判別
                    if abs(180 - abs(((self.angle + 180) % 360) - theta_center)) > 90:
                        self.angle = (self.angle + (((theta_center + 180) % 360) - self.angle) / 2) % 360
                    # 進行方向の前方から接触した場合
                    else:
                        self.angle = self.angle_with_wallangle((theta_center + 90) % 360)
                    self.calc_movement()

    # メインビューの端に到達した際の角度の変更
    def reflect_main(self):
        # メインビューの左右の壁に接触した場合は
        # 90°の壁に接触した前提で反射角度を計算し設定する
        if self.ball_x <= 0 or self.upper_right() >= self.superview.floor_width():
            self.angle = self.angle_with_wallangle(90)

        # メインビューの上下の壁に接触した場合は
        # 0°の壁に接触した前提で反射角度を計算し設定する
        if self.ball_y <= 0 or self.lower_left() >= self.superview.floor_height():
            self.angle = self.angle_with_wallangle(0)

        self.calc_movement()

    # 描画
    def draw(self):
        path = ui.Path.oval(0, 0, self.width, self.height)
        ui.set_color(self.draw_color)
        path.fill()

    # 表示上の半径を返す
    def change_diameter(self):
        # Todo 直径の最大値最小値などは定義しなおす
        max_diameter = self.ball_diameter
        min_diameter = 30
        min_y = 0 - min_diameter
        floor_width = self.superview.floor_width()

        return (((max_diameter - min_diameter) / floor_width) * (self.ball_y - min_y) + min_diameter)

    # 表示上の円のy座標を算出する
    def change_floor_y(self):
        floor_height = self.superview.floor_height()
        floor_front_y = self.superview.floor_front_y()
        floor_back_y = self.superview.floor_back_y()

        # 円の中心の座標を、表示上の円の底に設定する
        # (床の上下y軸の差分/床の実際の縦の辺の長さ) *
        # (円の位置y+円の半径)+床の最奥のy座標-円の表示直径
        return ((floor_front_y - floor_back_y) / floor_height) * (
                    self.ball_y + self.ball_diameter / 2) + floor_back_y - self.height

        pass

    # 表示上の円のx座標を算出する
    def change_floor_x(self):
        floor_width = self.superview.floor_width()
        floor_front_right_x = self.superview.floor_front_right_x
        floor_front_left_x = self.superview.floor_front_left_x
        floor_back_right_x = self.superview.floor_back_right_x
        floor_back_left_x = self.superview.floor_back_left_x
        floor_front_y = self.superview.floor_front_y()
        floor_back_y = self.superview.floor_back_y()

        # (180/360)+(360/360-180/360)/90 で表示上の
        # y軸の変化毎のx軸の比率の割合を算出し、
        # 円の表示上の位置からx軸の割合を算出する
        ratio = ((floor_back_right_x - floor_back_left_x) / floor_width) + (((floor_front_right_x - floor_front_left_x) / \
                floor_width - (floor_back_right_x - floor_back_left_x) / floor_width) / (floor_front_y - floor_back_y)) * \
                (self.y + self.height - floor_back_y)
        # 画面の左端と床の左端の隙間を算出する
        gap = (floor_front_y - floor_back_y) - (floor_front_right_x - floor_back_right_x) * (
                    (self.y + self.height - floor_back_y) / (floor_front_y - floor_back_y))
        # 床の上でのx軸を算出する
        return floor_front_left_x + gap + (self.ball_x * ratio) - (self.width / 2)

    # 床の上を移動
    def move_on_floor(self):
        self.ball_x = self.ball_x + (self.movement_x * self.speed)
        self.ball_y = self.ball_y + (self.movement_y * self.speed)

        # 円の表示サイズ変更
        self.width = self.change_diameter()
        self.height = self.width

        # 円のx,y座標を変換する
        self.y = self.change_floor_y()
        self.x = self.change_floor_x()

    # 円を落とし床に着地させる
    def fall(self):
        self.y = self.y + self.falling_speed
        self.falling_speed += 0.1

        floor_view = self.superview
        if isinstance(floor_view, BaseView) == False:
            return

        if self.y + self.ball_diameter >= floor_view.floor_front_y():
            self.falling_speed = 0
            self.ball_y = floor_view.floor_height() - self.ball_diameter
            # self.ball_x = self.x - floor_view.floor_front_x()
            self.ball_x = self.x
            self.is_on_floor = True
        pass

# 円の動作や接触、角度の計算を行う
# Timer イベントで繰り返し呼び出される
def schedule(main_view):
    for sub_view in main_view.subviews:
        if sub_view.is_on_floor == True:
            sub_view.reflect_subview()
            sub_view.reflect_main()

    for sub_view in main_view.subviews:
        if sub_view.is_on_floor == True:
            sub_view.move_on_floor()

    sorted_views = sorted(main_view.subviews, key=lambda subview: subview.width)

    for sub_view in sorted_views:
        sub_view.bring_to_front()
        # sub_view.send_to_back()

    main_view.set_needs_display()

    if main_view.on_screen == True:
        t = threading.Timer(0.01, schedule, args=[main_view])
        t.start()


# 床を奥に倒す挙動を描画する.
# Timerにより繰り返し実行される.
# angle 床を倒す角度. 実行ごとにデクリメントする
def floor_set_schedule(floor_view, angle):
    floor_view.set_floor_angle(angle)
    floor_view.rotate_floor()

    if floor_view.on_screen == True and angle > 18:
        angle -= 2
        t = threading.Timer(0.01, floor_set_schedule, args=[floor_view, angle])
        t.start()
    pass

# 床を回転する挙動を描画する.
# Timerにより繰り返し実行される.
def floor_spin_schedule(floor_view, angle, spin_count):
    floor_view.set_floor_angle(angle)
    floor_view.rotate_floor()

    if floor_view.on_screen == True:
        next_angle = angle - 10

        if next_angle <= 0:
            next_angle = 360

        if angle == 90:
            spin_count += 1

        if spin_count < 3:
            t = threading.Timer(0.01, floor_spin_schedule, args=[floor_view, next_angle, spin_count])
            t.start()
    pass


# 円を床に落下させる.
# Timerにより繰り返し実行される.
def fall_schedule(floor_view, subview):
    if isinstance(subview, BallView):
        subview.fall()

    if floor_view.on_screen == True and subview.is_on_floor == False:
        t = threading.Timer(0.01, fall_schedule, args=[floor_view, subview])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = '奥行きのある床で円を転がす'
    main_view.background_color = 'lightblue'
    main_view.set_floor_angle(90)
    main_view.rotate_floor()

    sub_view_1 = BallView(frame=(20, 80, 60, 60))
    sub_view_1.set_point_diameter(10, 90, 60)
    sub_view_1.set_speed_angle_color(3, 20, 'green')
    main_view.add_subview(sub_view_1)

    sub_view_2 = BallView(frame=(90, 80, 60, 60))
    sub_view_2.set_point_diameter(100, 100, 60)
    sub_view_2.set_speed_angle_color(3, 20, 'yellow')
    main_view.add_subview(sub_view_2)

    sub_view_3 = BallView(frame=(160, 80, 60, 60))
    sub_view_3.set_point_diameter(200, 110, 60)
    sub_view_3.set_speed_angle_color(3, 20, 'red')
    main_view.add_subview(sub_view_3)

    sub_view_4 = BallView(frame=(230, 80, 60, 60))
    sub_view_4.set_point_diameter(200, 220, 60)
    sub_view_4.set_speed_angle_color(3, 20, 'orange')
    main_view.add_subview(sub_view_4)

    sub_view_5 = BallView(frame=(300, 80, 60, 60))
    sub_view_5.set_point_diameter(200, 300, 60)
    sub_view_5.set_speed_angle_color(3, 20, 'pink')
    main_view.add_subview(sub_view_5)

    main_view.present()

    t1 = threading.Timer(1.0, floor_spin_schedule, args=[main_view, 90, 0])
    t1.start()

    t2 = threading.Timer(4.0, floor_set_schedule, args=[main_view, 90])
    t2.start()

    t3 = threading.Timer(7.0, schedule, args=[main_view])
    t3.start()

    delay = 8.0
    for subview in main_view.subviews:
        t4 = threading.Timer(delay, fall_schedule, args=[main_view, subview])
        t4.start()
        delay += 11.0
