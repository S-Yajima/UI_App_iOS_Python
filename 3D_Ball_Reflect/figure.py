from math import cos
from math import sin
from math import radians
from math import degrees
from math import sqrt
from enum import IntEnum


# 回転方向の列挙
class Direction(IntEnum):
    X = 1
    Y = (1 << 1)
    Z = (1 << 2)


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
    # 平行移動.　コンストラクターで定義する.
    # position = [0, 0, 0]	#[x, y, z]

    #
    is_hide = False

    def __init__(self):
        self.position = [0, 0, 0]

    def set_scale(self, scale):
        self.scale = scale

    def set_center(self, x, y, z):
        self.center_x = x
        self.center_y = y
        self.center_z = z

    def set_color(self, color):
        self.color = color

    def translate(self, x, y, z):
        self.position[0] = x
        self.position[1] = y
        self.position[2] = z

    def set_angle_x(self, angle):
        self.rotate_angle_x = angle

    def set_angle_y(self, angle):
        self.rotate_angle_y = angle

    def set_angle_z(self, angle):
        self.rotate_angle_z = angle

    # 拡大縮小
    def scale_queue(self, x, y, z):
        return ((x * self.scale), (y * self.scale), (z * self.scale))

    # 平行移動
    def translate_queue(self, x, y, z):
        return (
            (x + self.position[0]),
            (y + self.position[1]),
            (z + self.position[2]))

    # 回転、平行移動、拡大縮小を行う
    def queue(self, x, y, z):
        r_x, r_y, r_z = x, y, z
        r_x, r_y, r_z = self.three_dimensional_rotation(
            r_x, r_y, r_z,
            self.rotate_angle_x, self.rotate_angle_y, self.rotate_angle_z,
            self.center_x, self.center_y, self.center_z)
        r_x, r_y, r_z = self.translate_queue(r_x, r_y, r_z)
        r_x, r_y, r_z = self.scale_queue(r_x, r_y, r_z)
        return (r_x, r_y, r_z)

    # 三次元回転行列
    # three dimensional rotation matrix
    def three_dimensional_rotation(self, x, y, z,
                                   angle_x, angle_y, angle_z,
                                   center_x, center_y, center_z):
        y += center_y
        z += center_z
        # x軸の回転
        r_x_x = x  # ((1 * x) + (0) + (0))
        r_x_y = ((0) + (y * cos(radians(angle_x))) + (-1 * z * sin(radians(angle_x))))
        r_x_z = ((0) + (y * sin(radians(angle_x))) + (z * cos(radians(angle_x))))

        r_x_y -= center_y
        r_x_z -= center_z

        r_x_x += center_x
        r_x_z += center_z

        # y軸の回転
        r_y_x = ((r_x_x * cos(radians(angle_y))) + (0) + (r_x_z * sin(radians(angle_y))))
        r_y_y = r_x_y  # ((0) + (1 * r_x_y) + (0))
        r_y_z = ((-1 * r_x_x * sin(radians(angle_y))) + (0) + (r_x_z * cos(radians(angle_y))))

        r_y_x -= center_x
        r_y_z -= center_z

        r_y_x += center_x
        r_y_y += center_y

        # z軸の回転
        r_z_x = ((r_y_x * cos(radians(angle_z))) + (-1 * r_y_y * sin(radians(angle_z))) + (0))
        r_z_y = ((r_y_x * sin(radians(angle_z))) + (r_y_y * cos(radians(angle_z))) + (0))
        r_z_z = r_y_z  # ((0) + (0) + (1 * r_y_z))

        r_z_x -= center_x
        r_z_y -= center_y

        return (r_z_x, r_z_y, r_z_z)

    def mycolor(self):
        return self.color


# 三角
class Triangle(MyFigure):

    # A→B→Cが半時計周りに見える面が面になるように
    # 座標を設定すること
    def __init__(self, A_x, A_y, A_z, B_x, B_y, B_z, C_x, C_y, C_z):
        super().__init__()
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


# 四角
class Square(MyFigure):
    color = '#90b0ff'

    def __init__(self, A_x, A_y, A_z, B_x, B_y, B_z, C_x, C_y, C_z, D_x, D_y, D_z):
        super().__init__()
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


# 球
class Sphere(MyFigure):
    face_color = 'blue'
    back_color = 'white'
    # 球の中心.コンストラクターにて定義する
    # center = [0, 0, 0]
    # 球の半径
    radius = 0

    # 落下加速
    acceleration_vector = [0, 0.5, 0]
    # 進行ベクトル
    # proceed_vector = [0, 0, 0]
    # Y軸を軸にスピンする回転角度
    spin_angle = 0

    def __init__(self, radius, center_x=0, center_y=0, center_z=0, is_hide=False):

        self.radius = radius
        self.center = [center_x, center_y, center_z]

        # Triangles
        self.triangles = []
        # 進行ベクトルを初期設定する
        self.proceed_vector = [0, 0, 0]

        step = 20
        # 円図形の頂点を算出する
        # 0度と360度は座標が重複するがループで三角形を生成する便宜上あえて座標を配列に加える
        rounds = []
        for colmn in range(0, 361, step):
            points = []
            for angle in range(0, 181, step):
                x = radius * cos(radians(int(angle) + 270))
                y = radius * sin(radians(int(angle) + 270))
                z = 0

                r_x, r_y, r_z = self.three_dimensional_rotation(
                    x, y, z,
                    0, colmn, 0,
                    0, 0, 0)
                points.append([r_x, r_y, r_z])

            rounds.append(points)

        # 三角形を生成する
        # 最後のインデックスは計算用
        for r_index in range(0, len(rounds) - 1):
            round = rounds[r_index]
            next_round = rounds[r_index + 1]

            point_A = round[0]
            point_B = round[1]
            point_C = next_round[1]
            triangle = Triangle(
                point_A[0], point_A[1], point_A[2],
                point_B[0], point_B[1], point_B[2],
                point_C[0], point_C[1], point_C[2])
            triangle.is_hide = is_hide
            self.triangles.append(triangle)

            for p_index in range(1, len(round) - 1):
                point_A = round[p_index]
                point_B = round[p_index + 1]
                point_C = next_round[p_index]

                triangle = Triangle(
                    point_A[0], point_A[1], point_A[2],
                    point_B[0], point_B[1], point_B[2],
                    point_C[0], point_C[1], point_C[2])
                triangle.is_hide = is_hide
                self.triangles.append(triangle)

        self.set_center(center_x, center_y, center_z)

    # 球の中心座標を設定する
    # 初期設定、減り込み対応などに使用する
    def set_center(self, x, y, z):
        self.center[0] = x
        self.center[1] = y
        self.center[2] = z


        for triangle in self.triangles:
            triangle.position[0] = x
            triangle.position[1] = y
            triangle.position[2] = z


    # 進行ベクトルを設定する
    def set_proceed_vector(self, x, y, z):
        self.proceed_vector[0] = x
        self.proceed_vector[1] = y
        self.proceed_vector[2] = z


    # 進行ベクトルによる球の移動
    def proceed(self):
        self.set_center(
            self.center[0] + self.proceed_vector[0],
            self.center[1] + self.proceed_vector[1],
            self.center[2] + self.proceed_vector[2])


    # 加速ベクトルの値を進行ベクトルに加算して加速させる
    def accel(self):
        self.proceed_vector[0] += self.acceleration_vector[0]
        self.proceed_vector[1] += self.acceleration_vector[1]
        self.proceed_vector[2] += self.acceleration_vector[2]


    # 球をスピンする
    def spin(self):
        self.spin_angle += 2
        for triangle in self.triangles:
            triangle.rotate_angle_y = self.spin_angle


# 二つのベクトルの内積を求める
# ベクトルの長さで正規化されたベクトル同士の内積は
# 2つのベクトル同士のなす角cosθと同値になる
# v1 [x, y, z]
# v2 [x, y, z]
def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + \
           v1[2] * v2[2]


# 二つのベクトルの外積を計算して返す
# v1 [x, y, z]
# v2 [x, y, z]
def cross_product(v1, v2):
    return [v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]]


# ベクトルの長さから正規化を行い返す
# vector [x, y, z]
def normalize(vector):
    # ベクトルの長さを算出
    length = sqrt(
        vector[0] ** 2 + \
        vector[1] ** 2 + \
        vector[2] ** 2)

    # 法線ベクトルの正規化を実行し返す
    return [vector[0] / length,
            vector[1] / length,
            vector[2] / length]

