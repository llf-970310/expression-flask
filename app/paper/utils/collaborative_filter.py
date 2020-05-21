#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-21

import math
from app.models.user import UserModel


class CollaborativeFilter(object):

    def __init__(self):
        self.reverse_table = {}
        self.weight_matrix = {}
        self.user_like_counts = {}
        self.similarity_matrix = {}

    def create_reverse_table(self):
        users = UserModel.Objects({'questions_liked': {'$ne': '{}'}})
        for u in users:
            questions = u.questions_liked
            for q in questions:
                if q not in self.reverse_table:
                    self.reverse_table[q] = set()
                self.reverse_table[q].add(u)

    def create_weight_matrix(self):
        for question, users in self.reverse_table.items():
            for u1 in users:
                for u2 in users:
                    if u1 == u2:
                        continue
                    self.weight_matrix.setdefault(u1, {})
                    self.weight_matrix[u1].setdefault(u2, 0)
                    self.weight_matrix[u1][u2] += 1

    def calc_similarity_matrix(self):
        for u1, v1 in self.weight_matrix.items():
            for u2, cnt in v1.items():
                m = self.user_like_counts[u1]
                n = self.user_like_counts[u2]
                sim = cnt / math.sqrt(m * n)
                self.similarity_matrix[u1][u2] = sim

    def save_similar_users(self):
        # TODO: save the result to user.users_similar
        pass
