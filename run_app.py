#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-22

from app import create_app
import logging

banner = r'''
  _____  ___ __  _ __ ___  ___ ___(_) ___  _ __
 / _ \ \/ / '_ \| '__/ _ \/ __/ __| |/ _ \| '_ \
|  __/>  <| |_) | | |  __/\__ \__ \ | (_) | | | |
 \___/_/\_\ .__/|_|  \___||___/___/_|\___/|_| |_|
          |_|
'''
print(banner)
print('================================================')
print('             CREATING   FLASK  APP              ')
print('================================================')

app = create_app()

print('==================================================')
print('                FLASK APP CREATED                 ')
print('                  STARTING  NOW                   ')
print('==================================================')

if __name__ == '__main__':
    # handler = logging.FileHandler('flask.log')
    # app.logger.addHandler(handler)
    # print(app.logger.handlers)
    # print(len(app.logger.handlers))
    app.run()
