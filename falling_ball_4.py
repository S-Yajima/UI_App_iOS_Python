
import ui
import threading
import math


# 円を描画するView
# 落下、バウンド、放物線上を動作する
# 円の描画はdraw()メソッド内で.ui.Pathクラスにて行う
class MyView(ui.View):
    draw_color = 'yellow'
    direction_x = 1  # 1 : 右、/ -1 : 左
    direction_x_speed = 2
    falling_speed = 0
    acceleration = 0.2

    def upper_right(self):
        return (self.x + self.width)

    def lower_left(self):
        return (self.y + self.height)

    # メインビューの端に到達した際の角度の変更
    def reflect_main(self):
        # メインビューの左右の壁に接触した場合は
        # 90°の壁に接触した前提で反射角度を計算し設定する
        if self.x <= 0:
            self.direction_x = 1

        elif self.upper_right() >= self.superview.width:
            self.direction_x = -1

        # メインビューの下の壁に接触した場合
        if self.lower_left() >= self.superview.height:
            self.falling_speed = (self.falling_speed * -1) + self.acceleration
            # めり込みを補正する。
            self.y = self.superview.height - self.height
            # print(self.falling_speed)

    # 描画
    def draw(self):
        path = ui.Path.oval(0, 0, self.width, self.height)
        ui.set_color(self.draw_color)
        path.fill()

    # 移動
    def move(self):
        self.x = self.x + (self.direction_x * self.direction_x_speed)
        self.y = self.y + self.falling_speed

        self.falling_speed = self.falling_speed + self.acceleration

        # print(self.falling_speed)


# Timer イベントで呼び出される
def schedule(main_view):
    for sub_view in main_view.subviews:
        sub_view.reflect_main()

    for sub_view in main_view.subviews:
        sub_view.move()

    main_view.set_needs_display()

    if main_view.on_screen == True:
        t = threading.Timer(0.02, schedule, args=[main_view])
        t.start()


if __name__ == '__main__':
    # メイン画面の作成
    main_view = ui.View(frame=(0, 0, 375, 667))
    main_view.name = '落下とバウンド'
    main_view.background_color = 'lightblue'

    sub_view_1 = MyView(frame=(10, 100, 120, 120))
    sub_view_1.direction_x_speed = 1
    sub_view_1.acceleration = 0.2
    sub_view_1.draw_color = 'yellow'
    main_view.add_subview(sub_view_1)

    sub_view_2 = MyView(frame=(180, 220, 90, 90))
    sub_view_2.direction_x_speed = 3
    sub_view_2.acceleration = 0.4
    sub_view_2.draw_color = 'blue'
    main_view.add_subview(sub_view_2)

    sub_view_3 = MyView(frame=(280, 330, 60, 60))
    sub_view_3.direction_x_speed = 2
    sub_view_3.acceleration = 0.3
    sub_view_3.draw_color = 'red'
    main_view.add_subview(sub_view_3)

    sub_view_4 = MyView(frame=(100, 400, 50, 50))
    sub_view_4.direction_x_speed = 2
    sub_view_4.acceleration = 0.5
    sub_view_4.draw_color = 'green'
    main_view.add_subview(sub_view_4)

    main_view.present()

    t = threading.Timer(0.02, schedule, args=[main_view])
    t.start()