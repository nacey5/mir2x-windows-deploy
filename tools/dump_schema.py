# -*- coding: utf-8 -*-
"""导出 mir2x.db3 中涉及自定义函数 / tbl_char 的 DDL。"""
import sqlite3
import sys

db = sys.argv[1]
con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
cur = con.cursor()

rows = cur.execute(
    "select type, name, sql from sqlite_master "
    "where sql is not null and (sql like '%jobValid%' or name = 'tbl_char')"
).fetchall()

for t, n, s in rows:
    print("=== %s %s" % (t, n))
    print(s)
    print()

print("=== 所有触发器 ===")
for t, n, s in cur.execute(
    "select type, name, sql from sqlite_master where type='trigger'"
).fetchall():
    print("--", n)
    print(s)
    print()

con.close()
