# -*- coding: utf-8 -*-
# Time       : 2019/3/18 11:42
# Author     : tangdaye
# Description: admin config


class AccountsConfig:
    INVITATION_CODE_LEN = 16


class PaginationConfig:
    DEFAULT_PAGE = 1
    DEFAULT_SIZE = 50


class OptimizeConfig:
    COST_POINT = 50
    EMPTY_SCORE_DATA = {
        'key': [],
        'detail': [],
        'total': [],
        'keyStatistic': {"mean": 0, "sigma": 0, "difficulty": 0,
                         "discrimination": 0},
        'detailStatistic': {"mean": 0, "sigma": 0, "difficulty": 0, "discrimination": 0},
        'totalStatistic': {"mean": 0, "sigma": 0, "difficulty": 0, "discrimination": 0},

    }
    SCORE_GROUP_PERCENT = 0.27


class ScoreConfig:
    DEFAULT_USER_EMAIL = 'default@site.com'
    DEFAULT_NUM_FORMAT = '0.2f'
