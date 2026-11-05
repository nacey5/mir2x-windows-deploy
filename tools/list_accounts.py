# -*- coding: utf-8 -*-
"""列出 mir2x 服务端所有账号与角色，并做关联。"""
import sqlite3
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else r"F:\mir\mir2x\server\mir2x.db3"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

print("### tbl_account")
for r in cur.execute("select fld_dbid, fld_account, fld_password from tbl_account order by fld_dbid"):
    print("  dbid=%-3s account=%-8s password=%s" % r)

print("\n### tbl_char")
print("  %-5s %-8s %-4s %-4s %-5s %-6s %-6s %-5s %-5s %-8s %-8s" % (
    "dbid", "name", "sex", "job", "map", "x", "y", "hp", "mp", "exp", "gold"))
for r in cur.execute(
    "select fld_dbid, fld_name, fld_gender, fld_job, fld_map, fld_mapx, fld_mapy,"
    " fld_hp, fld_mp, fld_exp, fld_gold from tbl_char order by fld_dbid"
):
    print("  %-5s %-8s %-4s %-4s %-5s %-6s %-6s %-5s %-5s %-8s %-8s" % r)

print("\n### 账号 -> 角色")
for r in cur.execute(
    "select a.fld_dbid, a.fld_account, c.fld_name, c.fld_map, c.fld_mapx, c.fld_mapy"
    " from tbl_account a left join tbl_char c on a.fld_dbid = c.fld_dbid order by a.fld_dbid"
):
    print("  %-5s %-8s -> %-8s map=%s (%s,%s)" % r)

print("\n### 最近聊天消息（欢迎语）")
for r in cur.execute(
    "select fld_id, fld_timestamp, fld_to, fld_message from tbl_chatmessage order by fld_id desc limit 3"
):
    mid, ts, to, msg = r
    try:
        text = msg.decode("utf-8", "replace")
        if "<layout>" in text:
            text = text[text.index("<layout>"):]
    except Exception:
        text = repr(msg)
    print("  id=%s ts=%s to=%s msg=%s" % (mid, ts, to, text[:80]))

con.close()
