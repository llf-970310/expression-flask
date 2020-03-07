#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-22

from app import create_app
import logging

print('================================================')
print('====                                        ====')
print('====         CREATING   FLASK  APP          ====')
print('====                                        ====')
print('================================================')

app = create_app()

if __name__ == '__main__':
    # handler = logging.FileHandler('flask.log')
    # app.logger.addHandler(handler)
    # print(app.logger.handlers)
    # print(len(app.logger.handlers))
    print('=====================================================')
    print('====                                             ====')
    print('====             FLASK  APP  CREATED             ====')
    print('====                                             ====')
    print('====           NOW  STARTING  THE  APP           ====')
    print('====                                             ====')
    print('=====================================================')
    app.run()
