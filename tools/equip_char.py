# -*- coding: utf-8 -*-
"""
给角色配新手装备 / 药品 / 技能（需在服务端停止状态下执行）。

槽位编号来自 common/src/protocoldef.hpp 的 WearLookGridType：
    1 = 衣服(DRESS)   2 = 头盔(HELMET)   3 = 武器(WEAPON)
    4 = 鞋  5 = 项链  6/7 = 手镯  8/9 = 戒指  10 = 火把  11 = 护身符

物品/技能 ID 来自 common/src/itemrecord.inc 与 magicrecord.inc 的数组下标，
可用 tools/parse_item_ids.py 反查。

用法:
    python equip_char.py <db> <dbid>
默认给：乌木剑(826) + 高级布衣男(766) + 金创药中(6)x20 + 魔法药中(10)x20
        + 回城卷(152)x1 + 基本剑术(25)
"""
import sqlite3
import sys

DB = sys.argv[1]
DBID = int(sys.argv[2])

WEAR_DRESS = 1
WEAR_WEAPON = 3

EXTATTR = b"\x01\x00\x01\t\x02"   # 与包内已有物品一致的空扩展属性

con = sqlite3.connect(DB)
con.create_function("jobValid", 1, lambda j: 1)
con.create_function("SYS_PLY_VIEWR", 0, lambda: 15)
cur = con.cursor()

name = cur.execute("select fld_name from tbl_char where fld_dbid=?", (DBID,)).fetchone()
print("target char:", name)

# ---- 1. 装备 ----
wear_rows = [
    (DBID, WEAR_WEAPON, 826, 1, 0, 0, EXTATTR),   # 乌木剑
    (DBID, WEAR_DRESS, 766, 1, 0, 0, EXTATTR),    # 高级布衣（男）
]
for w in wear_rows:
    cur.execute(
        "insert or replace into tbl_wear"
        "(fld_dbid, fld_wear, fld_itemid, fld_count, fld_duration, fld_maxduration, fld_extattrlist)"
        " values(?,?,?,?,?,?,?)", w)
print("wear set:", [(w[1], w[2]) for w in wear_rows])

# ---- 2. 背包药品 ----
base_seq = cur.execute(
    "select coalesce(max(fld_seqid),0) from tbl_inventory where fld_dbid=?", (DBID,)
).fetchone()[0]
inv = [
    (6, 20),    # 金创药（中）
    (10, 20),   # 魔法药（中）
    (152, 1),   # 回城卷
]
seq = base_seq
for itemid, count in inv:
    seq += 1
    cur.execute(
        "insert or replace into tbl_inventory"
        "(fld_dbid, fld_itemid, fld_seqid, fld_count, fld_duration, fld_maxduration, fld_extattrlist)"
        " values(?,?,?,?,0,0,?)", (DBID, itemid, seq, count, EXTATTR))
print("inventory added:", inv)

# ---- 3. 技能 ----
cur.execute(
    "insert or replace into tbl_learnedmagiclist(fld_dbid, fld_magicid, fld_exp) values(?,?,0)",
    (DBID, 25))   # 基本剑术
print("magic learned: 25 基本剑术")

con.commit()

print("\n--- 结果 ---")
print("wear  =", cur.execute(
    "select fld_wear, fld_itemid from tbl_wear where fld_dbid=? order by fld_wear", (DBID,)
).fetchall())
print("inv   =", cur.execute(
    "select fld_itemid, fld_count from tbl_inventory where fld_dbid=? order by fld_seqid", (DBID,)
).fetchall())
print("magic =", cur.execute(
    "select fld_magicid, fld_exp from tbl_learnedmagiclist where fld_dbid=?", (DBID,)
).fetchall())
con.close()
