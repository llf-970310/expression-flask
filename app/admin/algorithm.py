import numpy as np
from scipy.special import erfinv

from .admin_config import OptimizeConfig


class OptimizeAlgorithm(object):

    @staticmethod
    def get_gaussian_array(mu, sigma, n):
        """
        获得一组符合正态分布的均匀数据
        :param mu: 均值
        :param sigma: 标准差
        :param n: 数据个数
        :return: 符合正态分布的n个均匀的数字
        """
        y_temp = list(map(lambda x: x / (n + 1), range(1, n + 1)))
        y = list(map(lambda x: mu + np.sqrt(2) * erfinv(2 * x - 1) * sigma, y_temp))
        return y

    @staticmethod
    def analysis_score(score_array, full_score):
        """
        获得一组得分的均值，标准差，难度，区分度
        :param score_array: 得分数组
        :param full_score: 满分
        :return: 均值，标准差，难度系数，区分度
        """
        np_score_array = np.sort(np.array(score_array))
        mean = np.mean(np_score_array)
        sigma = np.std(np_score_array)
        difficulty = mean / full_score
        n = 1 if len(score_array) <= 2 else round(len(score_array) * OptimizeConfig.SCORE_GROUP_PERCENT)
        low, high = 0, 0
        for i in range(n):
            low += np_score_array[i]
            high += np_score_array[-i - 1]
        discrimination = (high - low) / (full_score * n)
        return {'mean': mean, 'sigma': sigma, 'difficulty': difficulty, 'discrimination': discrimination}

    def optimize_param(self, x, y, settings):
        pass


class GradientDescent(OptimizeAlgorithm):

    @staticmethod
    def __get_cost_and_grad(x, theta, l, y):
        """
        获得损失函数值和损失函数导数值
        :param x: numpy矩阵，每行为一个样本，每列为对应参数的取值，包括第一列补充的1
        :param theta: numpy行矩阵，每列为一个参数
        :param l: 正则化参数
        :param y: numpy行矩阵，每列为每个样本对应的标签值
        :return: 在当前参数（theta）下，损失函数值和损失函数的导数值
        """
        m = len(x)
        cost = 1 / (2 * m) * np.power(np.dot(x, theta.T) - y.T, 2).sum() + l / (2 * m) * np.power(theta, 2).sum()
        theta_temp = np.mat([0] + theta.tolist()[1:])
        grad = 1 / m * np.dot(x.T, np.dot(x, theta.T) - y.T) + l / m * theta_temp.T
        return cost, grad

    def optimize_param(self, x, y, settings):
        """
        使用梯度下降对参数进行优化
        :param x: 二维数组，每行为一个样本，e.g.[[a1, a2, a3], [b1, b2, b3], ...]
        :param y: 一维数组，每个元素为样本对应的标签值
        :param settings: 配置，包括步长alpha，正则化参数lambda，迭代次数times，theta初始值（一维数组）
        :return: 迭代完成后得到的theta值和迭代过程中每次迭代的损失函数值
        """
        alpha, lam, times, theta = settings['alpha'], settings['lambda'], settings['times'], settings['theta']
        if not theta or len(theta) != len(x[0]) + 1:
            theta = list(map(lambda t: 0, range(len(x[0]) + 1)))
        # 首先将参数转成numpy矩阵
        np_x, np_y, np_theta = np.mat(list(map(lambda arr: [1] + arr, x))), np.mat(y), np.mat(theta)
        history_cost = []  # 存储历史损失函数值
        for i in range(times):
            cost, grad = self.__get_cost_and_grad(np_x, np_theta, lam, np_y)
            np_theta = np_theta - alpha * grad.T
            history_cost.append(cost)
        np_theta = (np.abs(np_theta) + np_theta) / 2
        return np_theta.tolist()[0], history_cost


class NormalEquation(OptimizeAlgorithm):

    def optimize_param(self, x, y, settings=None):
        np_x = np.mat(list(map(lambda arr: [1] + arr, x)))  # 在最前面补1
        np_y = np.mat(y).T
        np_theta = np.dot(np.dot(np.linalg.pinv(np.dot(np_x.T, np_x)), np_x.T), np_y).T
        np_theta = (np.abs(np_theta) + np_theta) / 2
        # cost history 由于不需要迭代所以损失函数历史全为0
        history_cost = list(map(lambda cost: 0, range(100)))
        return np_theta.tolist()[0], history_cost


if __name__ == '__main__':
    a = [[0.13000987, -0.22367519], [-0.50418984, -0.22367519], [0.50247636, -0.22367519], [-0.73572306, -1.53776691],
         [1.25747602, 1.09041654], [-0.01973173, 1.09041654], [-0.58723980, -0.22367519], [-0.72188140, -0.22367519],
         [-0.78102304, -0.22367519], [-0.63757311, -0.22367519], [-0.07635670, 1.09041654], [-0.00085674, -0.22367519],
         [-0.13927334, -0.22367519], [3.11729182, 2.40450826], [-0.92195631, -0.22367519], [0.37664309, 1.09041654],
         [-0.85652301, -1.53776691], [-0.96222296, -0.22367519], [0.76546791, 1.09041654], [1.29648433, 1.09041654],
         [-0.29404827, -0.22367519], [-0.14179001, -1.53776691], [-0.49915651, -0.22367519], [-0.04867338, 1.09041654],
         [2.37739217, -0.22367519], [-1.13335621, -0.22367519], [-0.68287309, -0.22367519], [0.66102629, -0.22367519],
         [0.25080981, -0.22367519], [0.80070123, -0.22367519], [-0.20344831, -1.53776691], [-1.25918949, -2.85185864],
         [0.04947657, 1.09041654], [1.42986760, -0.22367519], [-0.23868163, 1.09041654], [-0.70929808, -0.22367519],
         [-0.95844796, -0.22367519], [0.16524319, 1.09041654], [2.78635031, 1.09041654], [0.20299317, 1.09041654],
         [-0.42365654, -1.53776691], [0.29862646, -0.22367519], [0.71261793, 1.09041654], [-1.00752294, -0.22367519],
         [-1.44542274, -1.53776691], [-0.18708998, 1.09041654], [-1.00374794, -0.22367519]]
    b = [399900, 329900, 369000, 232000, 539900, 299900, 314900, 198999, 212000, 242500, 239999, 347000, 329999, 699900,
         259900, 449900, 299900, 199900, 499998, 599000, 252900, 255000, 242900, 259900, 573900, 249900, 464500, 469000,
         475000, 299900, 349900, 169900, 314900, 579900, 285900, 249900, 229900, 345000, 549000, 287000, 368500, 329900,
         314000, 299000, 179900, 299900, 239500]
    grad = GradientDescent()
    norm = NormalEquation()
    setting = {
        'alpha': 0.01,
        'lambda': 0,
        'times': 10000,
        'theta': None
    }
    th1 = grad.optimize_param(a, b, setting)
    th2 = norm.optimize_param(a, b, setting)
    print(th1)
    print(th2)
