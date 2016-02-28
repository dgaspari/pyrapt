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
    print('looking for filename that starts with: ', name)
    # file_location = 'scratch/marilyn02/'
    file_location = 'scratch/jonathan01_2sec_samples/'
    for a_file in os.listdir(file_location):
        if a_file.startswith(name + '0') and a_file.endswith('.wav'):
            print('found file: ', file_location + a_file)
            return file_location + a_file


def get_plot(filename):
    if filename is not None:
        print('getting plot for: ' + filename)
        results = pyrapt.rapt(filename, doubling_cost=30.0,
                              max_hypotheses_per_frame=35)
        return results
    else:
        print('no filename passed in, unable to load plot')
        return None


def insert_to_db(filename, plot, simplified, mandarin, pinyin):
    print('inserting into DB')
    dbpath = '../../../web/tonetrainer/database/tonetrainer.db'
    speaker_id = 1
    # get binary foramtted blob to insert into DB:
    with open(filename, 'rb') as wavfile:
        a_blob = wavfile.read()
        blob_binary = sqlite3.Binary(a_blob)
        insert_call = '''INSERT INTO Examples (SpeakerId, MandarinWord,
                      SimplifiedWord, PinyinWord, PitchJson,
                      WavFile) VALUES(?, ?, ?, ?, ?, ?);'''
        conn = sqlite3.connect(dbpath)
        with conn:
            curs = conn.cursor()
            curs.execute(insert_call, [speaker_id, mandarin, simplified, pinyin,
                         json.dumps(plot), blob_binary])

example_list = [
    ('新', '新', 'xin', 'xīn'),
    ('酸', '酸', 'suan', 'suān'),
    ('忙', '忙', 'mang', 'máng'),
    ('油', '油', 'you', 'yóu'),
    ('好', '好', 'hao', 'hǎo'),
    ('早', '早', 'zao', 'zǎo'),
    ('快', '快', 'kuai', 'kuài'),
    ('大', '大', 'da', 'dà'),
    ('傷心', '伤心', 'shangxin', 'shāngxīn'),
    ('好聽', '好听', 'haoting', 'hǎotīng'),
    ('突然', '突然', 'turan', 'tūrán'),
    ('狡猾', '狡猾', 'jiaohua', 'jiǎohuá'),
    ('辛苦', '辛苦', 'xinku', 'xīnkǔ'),
    ('保守', '保守', 'baoshou', 'bǎoshǒu'),
    ('安靜', '安静', 'anjing', 'ānjìng'),
    ('好看', '好看', 'haokan', 'hǎokàn'),
    ('暖和', '暖和', 'nuanhuo', 'nuǎnhuo'),
    ('舒服', '舒服', 'shufu', 'shūfu'),
    ('年輕', '年轻', 'nianqing', 'niánqīng'),
    ('流行', '流行', 'liuxing', 'liúxíng'),
    ('熱情', '热情', 'reqing', 'rèqíng'),
    ('無聊', '无聊', 'wuliao', 'wúliáo'),
    ('特別', '特别', 'tebie', 'tèbié'),
    ('電腦', '电脑', 'diannao', 'diànnǎo'),
    ('合適', '合适', 'heshi', 'héshì'),
    ('重要', '重要', 'zhongyao', 'zhòngyào'),
    ('便宜', '便宜', 'pianyi', 'piànyí'),
    ('漂亮', '漂亮', 'piaoliang', 'piàoliang')  # ,
    # ('美國人', '美国人', 'meiguoren', 'měiguórén'),
    # ('三明治', '三明治', 'sanmingzhi', 'sānmíngzhì'),
    # ('做飯', '做饭', 'zuofan', 'zuòfàn'),
    # ('牛肉', '牛肉', 'niurou', 'niúròu'),
    # ('小貓', '小猫', 'xiaomao', 'xiǎomāo')
    ]
for ex in example_list:
    # goal here is to find the right file, generate plot, convert to json str,
    # AND THEN: save to the local sqlite DB
    wavfile = get_file(ex[2])
    plot = get_plot(wavfile)
    if plot is not None:
        insert_to_db(wavfile, plot, ex[0], ex[1], ex[3])
