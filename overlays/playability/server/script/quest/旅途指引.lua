-- A discoverable, non-blocking hint. No item, currency or quest-state writes.
addQuestTrigger(SYS_ON_ONLINE, function(playerUID)
    uidRemoteCall(playerUID, [[
        if getLevel() < 7 then
            postString('初来乍到？右键移动，左键攻击或交谈。比奇县万事通（456，393）可查看新手指引与每日任务。')
        end
    ]])
end)
