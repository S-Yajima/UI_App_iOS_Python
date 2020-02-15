import ui
import threading
import math

# 重なり部分を塗り潰すためのView
class OverlapView(ui.View):
    # 円の重なりを描画する矩形
    round_frame = {'x': 0, 'y': 0, 'width': 0, 'height': 0}
    draw_color = 'yellow'

    # 円の重なりを描画する矩形を設定する
    def setRoundFrame(self, x, y, width, height):
        self.round_frame = dict(x=x, y=y, width=width, height=height)

    # 描画
    def draw(self):
        # 重なりの円の描画位置を設定する
        # 設定した描画位置で重なりの円を描画する
        path = ui.Path.oval(
            self.round_frame['x'], self.round_frame['y'], self.round_frame['width'], self.round_frame['height'])
        ui.set_color(self.draw_color)
        path.fill()


# 円を描画するView
# 円の描画はdraw()メソッド内で.ui.Pathクラスにて行う
class MyView(ui.View):
    is_contact = False
    direction_x = 1         # 円が進む方向　1:右、/-1:左
    direction_x_speed = 2   # 円が進む速度
    overlap_self_view = None
    overlap_other_view = None

    # 重なりを描画するViewを生成する
    def prepare_overlap_view(self):
        self.overlap_self_view = OverlapView(0, 0, 0, 0)
        self.add_subview(self.overlap_self_view)

        self.overlap_other_view = OverlapView(0, 0, 0, 0)
        self.add_subview(self.overlap_other_view)

    # 重なりを描画するViewに枠線を設定する
    def set_overlap_border(self):
        if self.overlap_self_view != None:
            self.overlap_self_view.border_color = 'black'
            self.overlap_other_view.border_width = 1

    def upper_right(self):
        return (self.x + self.width)

    def lower_left(self):
        return (self.y + self.height)

    # メインビューの端に到達した際の角度の変更
    def reflect_main(self):
        # メインビューの左右の壁に接触した場合は
        # 左右進行方向を逆に設定する。
        if self.x <= 0:
            self.direction_x = 1

        elif self.upper_right() >= self.superview.width:
            self.direction_x = -1

        # メインビューの下の壁に接触した場合
        if self.lower_left() >= self.superview.height:
            pass

    # 自身の円の重なりを描画するViewの矩形を設定する
    def calc_self_overlap(self, subview, contact_point_x, contact_point_y):
        overlap_self_view_x = 0
        overlap_self_view_y = self.height / 2 - contact_point_y
        overlap_self_view_w = self.width / 2 - contact_point_x
        overlap_self_view_h = contact_point_y * 2

        overlap_self_round_x = 0
        if self.center.x < subview.center.x:
            overlap_self_view_x = self.width / 2 + contact_point_x
            overlap_self_round_x = overlap_self_view_w - self.width

        self.overlap_self_view.frame = (
            overlap_self_view_x, overlap_self_view_y,
            overlap_self_view_w, overlap_self_view_h)
        self.overlap_self_view.setRoundFrame(
            overlap_self_round_x,
            contact_point_y - self.height / 2,
            self.width, self.height)
        self.overlap_self_view.set_needs_display()

    # 相手の円の重なりを描画する
    def calc_other_overlap(self, subview, contact_point_x, contact_point_y, diff_center):
        overlap_other_view_x = self.width / 2 - contact_point_x
        overlap_other_view_y = self.height / 2 - contact_point_y
        overlap_other_view_w = ((self.width + subview.width) / 2 - diff_center) - (self.width / 2 - contact_point_x)
        overlap_other_view_h = contact_point_y * 2

        overlap_other_round_x = ((self.width + subview.width) / 2 - diff_center) - (
                    self.width / 2 - contact_point_x) - subview.width

        if self.center.x < subview.center.x:
            overlap_other_view_x = self.width - (self.x + self.width - subview.x)
            overlap_other_round_x = 0

        self.overlap_other_view.frame = (
            overlap_other_view_x, overlap_other_view_y,
            overlap_other_view_w, overlap_other_view_h)
        self.overlap_other_view.setRoundFrame(
            overlap_other_round_x,
            contact_point_y - self.height / 2,
            subview.width, subview.height)
        self.overlap_other_view.set_needs_display()

    # 重なる部分を検知する
    def calc_overlap_frame(self, subview):
        if id(self) == id(subview):
            return

        # 相手の円と重なっていなければリターン
        diff_center_x = abs(self.center.x - subview.center.x)
        diff_center_y = abs(self.center.y - subview.center.y)
        diff_center = math.sqrt(diff_center_x ** 2 + diff_center_y ** 2)
        if (self.width + subview.width) / 2 <= diff_center:
            # print(diff_center)
            return

        self.is_contact = True

        # 接点と中心を結ぶ線と中心同士の線の角度を求める
        contact_cos = 0
        if diff_center != 0:    # 0割算対応
            # 接点までの角度cosθ=(自身の半径2乗+中心同士の距離2乗-相手の半径2乗)/(2*中心同士の距離*自身の半径)
            contact_cos = (diff_center ** 2 + self.width / 2 - subview.width / 2) / (2 * diff_center * (self.width / 2))
        # 接点までの角度アークcos(ラジアン)を算出する
        contact_acos = math.acos(contact_cos)

        # 接点までの角度アークcos(ラジアン)と半径の長さから接点のx、y座標を求める
        contact_point_y = math.sin(contact_acos) * (self.width / 2)
        contact_point_x = math.cos(contact_acos) * (self.width / 2)

        # 円の重なりを描画する
        self.calc_self_overlap(
            subview, contact_point_x, contact_point_y)
        self.calc_other_overlap(
            subview, contact_point_x, contact_point_y, diff_center)

    def overlap(self):
        for subview in self.superview.subviews:
            if id(self) != id(subview):
                self.calc_overlap_frame(subview)

    # 描画
    def draw(self):
        path = ui.Path.oval(0, 0, self.width, self.height)
        ui.set_color(self.draw_color)
        path.fill()

    # 移動
    def move(self):
        self.x = self.x + (self.direction_x * self.direction_x_speed)

    def cleanup(self):
        if self.is_contact == False:
            self.overlap_self_view.setRoundFrame(0, 0, 0, 0)
            self.overlap_self_view.set_needs_display()
            self.overlap_other_view.setRoundFrame(0, 0, 0, 0)
            self.overlap_other_view.set_needs_display()

        self.is_contact = False


# Timer イベントで呼び出される
def schedule(main_view):
    for sub_view in main_view.subviews:
        sub_view.reflect_main()

    for sub_view in main_view.subviews:
        sub_view.move()

    for sub_view in main_view.subviews:
        sub_view.overlap()

    for sub_view in main_view.subviews:
        sub_view.cleanup()

    main_view.set_needs_display()

    if main_view.on_screen == True:
        t = threading.Timer(0.02, schedule, args=[main_view])
        t.start()
        pass


if __name__ == '__main__':
    # メイン画面の作成
    main_view = ui.View(frame=(0, 0, 375, 667))
    main_view.name = '円の重なり'
    main_view.background_color = 'lightblue'

    sub_view_1 = MyView(frame=(160, 210, 100, 100))
    sub_view_1.direction_x_speed = 2
    sub_view_1.draw_color = 'green'
    sub_view_1.prepare_overlap_view()
    main_view.add_subview(sub_view_1)

    sub_view_2 = MyView(frame=(280, 210, 100, 100))
    sub_view_2.direction_x_speed = 3
    sub_view_2.draw_color = 'pink'
    sub_view_2.prepare_overlap_view()
    main_view.add_subview(sub_view_2)

    sub_view_3 = MyView(frame=(50, 390, 150, 150))
    sub_view_3.direction_x_speed = 4
    sub_view_3.draw_color = 'red'
    sub_view_3.prepare_overlap_view()
    sub_view_3.set_overlap_border()
    main_view.add_subview(sub_view_3)

    sub_view_4 = MyView(frame=(180, 390, 150, 150))
    sub_view_4.direction_x_speed = 3
    sub_view_4.draw_color = 'blue'
    sub_view_4.prepare_overlap_view()
    sub_view_4.set_overlap_border()
    main_view.add_subview(sub_view_4)

    sub_view_5 = MyView(frame=(160, 80, 70, 70))
    sub_view_5.direction_x_speed = 1
    sub_view_5.draw_color = 'orange'
    sub_view_5.prepare_overlap_view()
    main_view.add_subview(sub_view_5)

    sub_view_6 = MyView(frame=(280, 80, 70, 70))
    sub_view_6.direction_x_speed = 3
    sub_view_6.draw_color = 'purple'
    sub_view_6.prepare_overlap_view()
    main_view.add_subview(sub_view_6)

    main_view.present()

    t = threading.Timer(0.02, schedule, args=[main_view])
    t.start()