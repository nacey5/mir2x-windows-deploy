# -*- coding: utf-8 -*-
"""
把角色恢复到指定 HP（需在服务端停止状态下执行）。

用法:
    python heal_char.py <db> <dbid> <hp>
"""
import sqlite3
import sys

db, dbid, hp = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

con = sqlite3.connect(db)
con.create_function("jobValid", 1, lambda j: 1)
con.create_function("SYS_PLY_VIEWR", 0, lambda: 15)
cur = con.cursor()

before = cur.execute(
    "select fld_name, fld_map, fld_mapx, fld_mapy, fld_hp from tbl_char where fld_dbid=?",
    (dbid,),
).fetchone()
cur.execute("update tbl_char set fld_hp=? where fld_dbid=?", (hp, dbid))
con.commit()
after = cur.execute(
    "select fld_name, fld_map, fld_mapx, fld_mapy, fld_hp from tbl_char where fld_dbid=?",
    (dbid,),
).fetchone()
print("before:", before)
print("after :", after)
con.close()
