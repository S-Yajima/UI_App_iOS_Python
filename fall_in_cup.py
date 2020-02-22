import ui
import threading
import math

class BaseView(ui.View):
    cup_width = 200
    cup_height = 360
    cup_gap = 40
    cup_color = 'blue'

    def cup_y(self):
        return (self.height - self.cup_height)

    def cup_x(self):
        return (self.width - self.cup_width - self.cup_gap)

    # cupの右端のx軸を返す
    def cup_x_width(self):
        return (self.width - self.cup_gap)

    # cupの描画を行う
    def draw(self):
        path = ui.Path.rect(
            self.width - self.cup_width - self.cup_gap,
            self.height - self.cup_height,
            self.cup_width, self.cup_height)
        ui.set_color(self.cup_color)
        path.fill()


# 円を描画するView
# 落下、放物線上を動作する
# 円の描画はdraw()メソッド内で.ui.Pathクラスにて行う
class BallView(ui.View):
    draw_color = 'yellow'
    direction_x = 1  # 1: 右 / -1: 左
    direction_x_speed = 2  # 左右に動く速度
    direction_x_decel = 0.01  # 転がる際の速度減速
    falling_speed = 0  # 落下速度
    acceleration = 0.2  # 落下加速速度
    restitution = 0.03  # 反発係数
    is_suspend = False  # 停止済か否かを示す。

    def upper_right(self):
        return (self.x + self.width)

    def lower_left(self):
        return (self.y + self.height)

    # 他の円と接触しているか判別する
    def is_contact_with_subview(self, subview):
        is_contact = False

        diff_x = subview.center.x - self.center.x
        diff_y = subview.center.y - self.center.y
        diff_center = math.sqrt(abs(diff_x) ** 2 + abs(diff_y) ** 2)
        # 接触している場合
        if (self.width + subview.width) / 2 >= diff_center:
            is_contact = True

        return is_contact

    # 円同士の接触と反射を処理する
    def reflect_subview(self):
        # 停止中の場合は終了
        if self.is_suspend == True:
            return

        for subview in self.superview.subviews:
            if id(self) == id(subview):
                continue

            # 他の円と接触しているか判別する
            if self.is_contact_with_subview(subview) == False:
                continue

            # 更に他の円と接触していないか判別する
            for other_view in self.superview.subviews:
                if id(self) == id(other_view) or id(subview) == id(other_view):
                    continue

                # 2つの円と接触している場合、落下速度と左右移動速度を無くし停止フラグを立てる
                if self.is_contact_with_subview(other_view) == True:
                    self.direction_x_speed = 0
                    self.falling_speed = 0
                    self.is_suspend = True
                    return

                    # 最初に接触した円との左右の位置関係から、左右の進行方向を決定する
            if self.center.x < subview.center.x:
                # 進行方向が変更される場合は反発係数で速度を減速する
                if self.direction_x == 1:
                    self.direction_x_speed -= self.restitution
                self.direction_x = -1
            else:
                if self.direction_x == -1:
                    self.direction_x_speed -= self.restitution
                self.direction_x = 1

            # 移動速度が一定以上遅くなったら停止する
            if self.direction_x_speed < 0.05:
                self.direction_x_speed = 0

            # 円に接触した事により落下速度を無くす
            self.falling_speed = 0

    # cupとの接触と反射を処理する
    def reflect_cup(self):
        # 二つの円と接触して停止している場合は処理を抜ける
        if self.is_suspend == True:
            return

        # 円の位置がcupの中の場合
        if self.lower_left() > self.superview.cup_y() and self.center.x > self.superview.cup_x():

            # cupの左右の壁に接触したら反射し反発係数で減速する
            if self.x <= self.superview.cup_x():
                self.direction_x = 1
                self.direction_x_speed -= self.restitution
                self.x = self.superview.cup_x()
            elif self.upper_right() >= self.superview.cup_x_width():
                self.direction_x = -1
                self.direction_x_speed -= self.restitution
                self.x = self.superview.cup_x_width() - self.width

            # コップの底に接触した場合
            if self.lower_left() >= self.superview.height:
                # 落下速度を無くす
                self.falling_speed = 0
                # 転がる速度を減速させる
                self.direction_x_speed -= self.direction_x_decel

                if self.direction_x_speed < 0.1:
                    self.direction_x_speed = 0

                # めり込みを補正する。
                self.y = self.superview.height - self.height

    # メインビューの端に到達した際の角度の変更
    def reflect_main(self):

        if self.is_suspend == True:
            return

        # メインビューの左右の壁に接触した場合は
        # 左右進行方向を逆に設定する
        if self.x <= 0:
            self.direction_x = 1
            self.direction_x_speed -= self.restitution
            self.x = 0
        elif self.upper_right() >= self.superview.width:
            self.direction_x = -1
            self.direction_x_speed -= self.restitution
            self.x = self.superview.width - self.width

        # メインビューの下の壁に接触した場合
        if self.lower_left() >= self.superview.height:
            # 床を転がる状態
            self.falling_speed = 0
            # 転がる速度を減速させる
            self.direction_x_speed -= self.direction_x_decel

            if self.direction_x_speed < 0.1:
                self.direction_x_speed = 0

            # めり込みを補正する。
            self.y = self.superview.height - self.height

    # 円を描画する
    def draw(self):
        path = ui.Path.oval(0, 0, self.width, self.height)
        ui.set_color(self.draw_color)
        path.fill()

    # 移動
    def move(self):
        self.x += (self.direction_x * self.direction_x_speed)
        self.y += self.falling_speed

        if self.is_suspend == False:
            self.falling_speed += self.acceleration


# Timer イベントで呼び出される
def schedule(main_view, count):
    colors = ['yellow', 'red', 'green', 'pink', 'orange']

    # 円を新たに生成して落とす
    interval = 140  # 円を落とす時間間隔
    round_number = 17  # 円の個数
    if count % interval == 0 and count <= (round_number * interval):
        sub_view = BallView(frame=(90, 60, 75, 75))
        color_index = ((int(count / interval) - 1) % len(colors))
        sub_view.draw_color = colors[color_index]
        main_view.add_subview(sub_view)

    # 円同士の接触と反射
    for sub_view in main_view.subviews:
        sub_view.reflect_subview()
    # cupとの接触と反射
    for sub_view in main_view.subviews:
        sub_view.reflect_cup()
    # main viewとの接触と反射
    for sub_view in main_view.subviews:
        sub_view.reflect_main()
    # 円を実際に動かす
    for sub_view in main_view.subviews:
        sub_view.move()

    main_view.set_needs_display()
    # タイマー処理を再設定する
    if main_view.on_screen == True:
        count = count + 1
        t = threading.Timer(0.02, schedule, args=[main_view, count])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = BaseView(frame=(0, 0, 375, 667))
    main_view.name = 'コップに円を投げ入れ積み上げ'
    main_view.background_color = 'lightblue'

    main_view.present()

    t = threading.Timer(0.02, schedule, args=[main_view, 1])
    t.start()
