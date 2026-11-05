# -*- coding: utf-8 -*-
"""
解析 mir2x 的 itemrecord.inc / magicrecord.inc，建立 名称 <-> ID 映射。

mir2x 的物品/技能 ID 就是数组下标（DBCOM_ITEMID 返回 offset），
数组第 0 项是空占位，所以第一个具名项 ID=1。
"""
import re
import sys


def parse_inc(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    # 顶层项形如 {   .name = u8"xxx", ... }，嵌套结构里不会再出现 .name
    names = re.findall(r'\.name\s*=\s*u8"([^"]*)"', text)
    return names


def main():
    item_inc = r"F:\mir\logs\itemrecord.inc"
    magic_inc = r"F:\mir\logs\magicrecord.inc"

    items = parse_inc(item_inc)
    magics = parse_inc(magic_inc)

    print("items parsed =", len(items))
    print("magics parsed =", len(magics))
    print()

    # 数组下标从 0 开始，每项对应 ID
    item_id = {name: i for i, name in enumerate(items)}
    magic_id = {name: i for i, name in enumerate(magics)}

    print("=== 角色身上已有的 itemid 反查 ===")
    for iid in [4, 6, 10, 766, 826, 1203, 1232, 1239]:
        name = items[iid] if iid < len(items) else "<越界>"
        print("  itemid=%-5d -> %s" % (iid, name))
    print()

    print("=== 新手常用物品 ID ===")
    for want in [
        "金创药（小）", "金创药（中）", "金创药（大）", "金创药（特）",
        "魔法药（小）", "魔法药（中）", "魔法药（大）", "魔法药（特）",
        "回城卷", "随机传送卷",
        "破山剑", "旋风流星刀", "破魂",
        "布衣（男）", "布衣（女）", "轻型盔甲（男）",
    ]:
        print("  %-14s -> %s" % (want, item_id.get(want, "未找到")))
    print()

    print("=== 战士技能 ID ===")
    for want in ["基本剑术", "攻杀剑术", "刺杀剑术", "半月弯刀", "野蛮冲撞", "烈火剑法"]:
        print("  %-8s -> %s" % (want, magic_id.get(want, "未找到")))
    print()

    print("=== 所有含'剑术'的技能 ===")
    for i, n in enumerate(magics):
        if "剑术" in n or "剑法" in n:
            print("  [%d] %s" % (i, n))


if __name__ == "__main__":
    main()
