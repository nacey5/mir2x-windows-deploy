# -*- coding: utf-8 -*-
"""
向 mir2x 服务端库新增一个账号与角色（需在服务端停止状态下执行）。

用法:
    python add_account.py <db> <account> <password> <charname> [job] [map] [x] [y]
默认 job=6（与预置角色「亚当」一致）、map=1（比奇）、坐标 (441,381)。
"""
import sqlite3
import sys

db = sys.argv[1]
account = sys.argv[2]
password = sys.argv[3]
charname = sys.argv[4]
job = int(sys.argv[5]) if len(sys.argv) > 5 else 6
mapid = int(sys.argv[6]) if len(sys.argv) > 6 else 1
x = int(sys.argv[7]) if len(sys.argv) > 7 else 441
y = int(sys.argv[8]) if len(sys.argv) > 8 else 381

con = sqlite3.connect(db)

# tbl_char 的 fld_job 带 CHECK(jobValid(...)) / fld_viewr 默认 SYS_PLY_VIEWR()，
# 这两个是服务端在 SQLite 里注册的自定义函数，外部工具写入时必须补桩，否则
# sqlite3.OperationalError: unknown function: jobValid()
con.create_function("jobValid", 1, lambda j: 1)
con.create_function("SYS_PLY_VIEWR", 0, lambda: 15)

cur = con.cursor()

# 账号与角色共用 fld_dbid 主键（实测: test=2 <-> 亚当 dbid=2）
nextid = cur.execute(
    "select coalesce(max(fld_dbid),0)+1 from tbl_account"
).fetchone()[0]
alt = cur.execute(
    "select max(fld_dbid) from tbl_char"
).fetchone()[0] or 0
nextid = max(nextid, alt + 1)

cur.execute(
    "insert into tbl_account(fld_dbid, fld_account, fld_password) values(?,?,?)",
    (nextid, account, password),
)
cur.execute(
    "insert into tbl_char(fld_dbid, fld_name, fld_gender, fld_job, fld_map,"
    " fld_mapx, fld_mapy, fld_hp, fld_mp, fld_exp, fld_gold, fld_hair,"
    " fld_haircolor, fld_pkpoint, fld_viewr)"
    " values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    (nextid, charname, 1, job, mapid, x, y, 10, 10, 0, 10000, 0, 0, 0, 15),
)
con.commit()

print("新增 dbid=%d account=%s char=%s job=%d map=%d (%d,%d)" % (
    nextid, account, charname, job, mapid, x, y))
print("accounts =", [r for r in cur.execute(
    "select fld_dbid, fld_account from tbl_account order by fld_dbid")])
print("chars    =", [r for r in cur.execute(
    "select fld_dbid, fld_name, fld_job, fld_map, fld_mapx, fld_mapy"
    " from tbl_char order by fld_dbid")])
con.close()
