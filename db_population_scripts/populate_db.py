#!/usr/bin/python
# coding: utf-8
from __future__ import unicode_literals
from pyrapt import pyrapt
import sqlite3
import os
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')


def get_file(name):
    file_location = 'scratch/marilyn01/'
    for a_file in os.listdir(file_location):
        if a_file.startswith(name + '0') and a_file.endswith('.wav'):
            return file_location + a_file


def get_plot(filename):
    print('getting plot for: ' + filename)
    results = pyrapt.rapt(filename, transition_cost=0.5, doubling_cost=30.0)
    return results


def insert_to_db(filename, plot, mandarin, pinyin):
    print('inserting into DB')
    dbpath = '../../../web/tonetrainer/database/tonetrainer.db'
    speaker_id = 2
    # get binary foramtted blob to insert into DB:
    with open(filename, 'rb') as wavfile:
        a_blob = wavfile.read()
        blob_binary = sqlite3.Binary(a_blob)
        insert_call = '''INSERT INTO Examples (SpeakerId, MandarinWord,
                      PinyinWord, PitchJson, WavFile) VALUES(?, ?, ?, ?, ?);'''
        conn = sqlite3.connect(dbpath)
        with conn:
            curs = conn.cursor()
            curs.execute(insert_call, [speaker_id, mandarin, pinyin,
                         json.dumps(plot), blob_binary])

example_list = [
    ('新', 'xin', 'xīn'),
    ('酸', 'suan', 'suān'),
    ('忙', 'mang', 'máng'),
    ('油', 'you', 'yóu'),
    ('好', 'hao', 'hǎo'),
    ('早', 'zao', 'zǎo'),
    ('快', 'kuai', 'kuài'),
    ('大', 'da', 'dà'),
    ('傷心', 'shangxin', 'shāngxīn'),
    ('好聽', 'haoting', 'hǎotīng'),
    ('突然', 'turan', 'tūrán'),
    ('狡猾', 'jiaohua', 'jiǎohuá'),
    ('辛苦', 'xinku', 'xīnkǔ'),
    ('保守', 'baoshou', 'bǎoshǒu'),
    ('安靜', 'anjing', 'ānjìng'),
    ('好看', 'haokan', 'hǎokàn'),
    ('暖和', 'nuanhuo', 'nuǎnhuo'),
    ('舒服', 'shufu', 'shūfu'),
    ('年輕', 'nianqing', 'niánqīng'),
    ('流行', 'liuxing', 'liúxíng'),
    ('熱情', 'reqing', 'rèqíng'),
    ('無聊', 'wuliao', 'wúliáo'),
    ('特別', 'tebie', 'tèbié'),
    ('電腦', 'diannao', 'diànnǎo'),
    ('合適', 'heshi', 'héshì'),
    ('重要', 'zhongyao', 'zhòngyào'),
    ('便宜', 'pianyi', 'piànyí'),
    ('漂亮', 'piaoliang', 'piàoliang')]
for ex in example_list:
    # goal here is to find the right file, generate plot, convert to json str,
    # AND THEN: save to the local sqlite DB
    wavfile = get_file(ex[1])
    plot = get_plot(wavfile)
    insert_to_db(wavfile, plot, ex[0], ex[2])
