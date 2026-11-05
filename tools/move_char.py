# -*- coding: utf-8 -*-
"""
把指定角色传送到指定地图坐标（需在服务端停止状态下执行）。

UPDATE 会重新校验 tbl_char 的 CHECK 约束，因此仍需补齐 jobValid / SYS_PLY_VIEWR 桩函数。

用法:
    python move_char.py <db> <dbid> <map> <x> <y>
"""
import sqlite3
import sys

db, dbid, mapid, x, y = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])

con = sqlite3.connect(db)
con.create_function("jobValid", 1, lambda j: 1)
con.create_function("SYS_PLY_VIEWR", 0, lambda: 15)
cur = con.cursor()

before = cur.execute(
    "select fld_name, fld_map, fld_mapx, fld_mapy, fld_hp from tbl_char where fld_dbid=?",
    (dbid,),
).fetchone()
cur.execute(
    "update tbl_char set fld_map=?, fld_mapx=?, fld_mapy=? where fld_dbid=?",
    (mapid, x, y, dbid),
)
con.commit()
after = cur.execute(
    "select fld_name, fld_map, fld_mapx, fld_mapy, fld_hp from tbl_char where fld_dbid=?",
    (dbid,),
).fetchone()
print("before:", before)
print("after :", after)
con.close()
