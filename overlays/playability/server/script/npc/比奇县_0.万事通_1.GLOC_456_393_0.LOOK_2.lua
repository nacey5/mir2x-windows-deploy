-- Entry point for the 201b19d build's previously empty Bichon guide.
-- Existing dailyquest owns progress, reset times and rewards.
local dialog = require('include.dialog')

local function back()
    return {
        dialog.link(SYS_ENTER, '返回指引'),
        dialog.link(SYS_EXIT, '先去试试'),
    }
end

local function activities(uid)
    local level = uidQueryLevel(uid)
    local choices = {}
    if level >= 7 then
        table.insert(choices, dialog.link('guide_daily', '接取 / 查看当前跑腿任务'))
    end
    table.insert(choices, dialog.link('guide_routes', '查看职业任务入口'))
    table.insert(choices, dialog.link(SYS_ENTER, '返回指引'))
    table.insert(choices, dialog.link(SYS_EXIT, '关闭'))
    dialog.post(uid, {
        '今日可做：每日跑腿',
        string.format('需要7级，你当前%d级。每天最多20轮。', level),
        '每轮随机获得金币、经验或补给之一。完成后到目标人物处领取。',
        '目标可能在其他地图。熟悉路线后再接；忘了目标可回来查看。',
        '限时活动尚未开放。先完成职业任务，学会补给与战斗。',
    }, choices)
end

setEventHandler({
    [SYS_ENTER] = function(uid, value)
        dialog.post(uid, {
            '我是比奇万事通。初来乍到，先准备补给，再出城试一场战斗。',
            '以后不知道做什么，都可以回来找我：比奇县（456，393）。',
        }, {
            dialog.link('guide_first', '第一次玩：从哪里开始'),
            dialog.link('guide_controls', '查看操作方法'),
            dialog.link('guide_activities', '今天有什么可做'),
            dialog.link(SYS_EXIT, '我先自己探索'),
        })
    end,

    guide_first = function(uid, value)
        dialog.post(uid, {
            '先完成一轮：准备 → 战斗 → 补给。',
            '第一步：查看背包与装备，确认有能穿戴的武器、衣服和药。',
            '第二步：到城外找落单弱怪，左键攻击。血量下降就撤回安全处。',
            '第三步：拾取掉落，查看经验变化，再回城补药。',
        }, {
            dialog.link('guide_supplies', '去哪里补给'),
            dialog.link('guide_controls', '我还不会操作'),
            dialog.link('guide_routes', '寻找职业任务'),
            dialog.link(SYS_ENTER, '返回指引'),
        })
    end,

    guide_controls = function(uid, value)
        dialog.post(uid, {
            '移动：右键点击可通行的地面。',
            '战斗 / 交谈：左键点击怪物 / 人物。',
            '拾取：左键点击地上物品，或站到物品处按Tab。',
            '补给：物品放入快捷栏后，按1至6使用对应栏位。',
            '遇到危险：右键离开，打断当前追击。',
        }, back())
    end,

    guide_supplies = function(uid, value)
        dialog.post(uid, {
            '比奇城补给点',
            '药店老板（397，363）：购买金创药、魔法药，先看价格。',
            '老张（423，395）：查看武器、出售物品和修理；先看穿戴条件。',
            '总教头（447，444）：询问技能书指导，需要费用。',
            '身上没有合适装备或买不起药时，先回出生地找职业引路人。',
        }, {
            dialog.link('guide_routes', '查看职业引路人'),
            dialog.link(SYS_ENTER, '返回指引'),
            dialog.link(SYS_EXIT, '去找商人'),
        })
    end,

    guide_routes = function(uid, value)
        dialog.post(uid, {
            '选择你的职业，查看初出江湖任务的起点。',
            '到对应人物处交谈接取。这里查看说明不会自动完成任务。',
        }, {
            dialog.link('guide_warrior', '战士：边境城市'),
            dialog.link('guide_wizard', '法师：银杏山谷'),
            dialog.link('guide_taoist', '道士：道馆'),
            dialog.link(SYS_ENTER, '返回指引'),
        })
    end,

    guide_warrior = function(uid, value)
        dialog.post(uid, {
            '战士初出江湖',
            '起点：边境城市，上官小姐（461，257）。',
            '低等级从帮肉店送东西开始；6级起的对话路线不同。',
            '按对话指引继续，接过任务后查看任务面板。',
        }, back())
    end,

    guide_wizard = function(uid, value)
        dialog.post(uid, {
            '法师初出江湖',
            '起点：银杏山谷，南宫小姐（264，201）。',
            '低等级从拜访肉铺开始；6级起的对话路线不同。',
            '按对话指引继续，接过任务后查看任务面板。',
        }, back())
    end,

    guide_taoist = function(uid, value)
        dialog.post(uid, {
            '道士初出江湖',
            '起点：道馆，士官（403，132）。',
            '低等级先按士官的指引办事；6级起的对话路线不同。',
            '按对话指引继续，接过任务后查看任务面板。',
        }, back())
    end,

    guide_activities = activities,

    guide_daily = function(uid, value)
        -- Enforce the gate again: a stale or forged dialog event must not bypass it.
        if uidQueryLevel(uid) < 7 then
            activities(uid)
            return
        end
        require('npc.include.dailyquest').setQuest(uid, nil)
    end,
})
