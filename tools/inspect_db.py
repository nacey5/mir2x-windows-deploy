# -*- coding: utf-8 -*-
"""读取 mir2x 服务端 SQLite 数据库，验证账号与角色落库情况。"""
import sqlite3
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else r"F:\mir\mir2x\server\mir2x.db3"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

tabs = [r[0] for r in cur.execute("select name from sqlite_master where type='table' order by name")]
print("tables:", tabs)
print()

for t in tabs:
    cols = [c[1] for c in cur.execute('PRAGMA table_info("%s")' % t)]
    n = cur.execute('select count(*) from "%s"' % t).fetchone()[0]
    print("== %s  rows=%d" % (t, n))
    print("   cols:", cols)
    if n:
        rows = cur.execute('select * from "%s" limit 5' % t).fetchall()
        for r in rows:
            print("   ", r)
    print()

con.close()
