"""Run with MIR2X_SCRIPT_ROOT pointing to an unmodified 201b19d script directory.

Real upstream dialog rendering is executed in Lua 5.4; engine/player calls are
test doubles. This does not certify native rendering or network gameplay.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from lupa.lua54 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'overlays' / 'playability'
SCRIPTS = OVERLAY / 'server' / 'script'
NPC = next((SCRIPTS / 'npc').glob('*.lua'))
HINT = SCRIPTS / 'quest' / '旅途指引.lua'
spec = importlib.util.spec_from_file_location('checker', ROOT / 'tools' / 'check_playability.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class GuideTests(unittest.TestCase):
    def setUp(self):
        # Fail explicitly instead of silently skipping the most useful checks.
        source = Path(os.environ['MIR2X_SCRIPT_ROOT'])
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.g = self.lua.globals()
        self.g.source_path = source.as_posix()
        self.lua.execute('''
            package.path = source_path .. '/?.lua;' .. package.path
            SYS_ENTER = 'enter'; SYS_EXIT = 'exit'
            SYS_EPUID = 'uid'; SYS_EPQST = 'quest'; SYS_EPDEF = 'default'
            SYS_ON_ONLINE = 1
            level = 1; daily_calls = 0; messages = {}; xml = nil
            function assertType(value, ...)
                for _, expected in ipairs({...}) do
                    if type(value) == expected or
                       (expected == 'integer' and math.type(value) == 'integer') then
                        return value
                    end
                end
                error('unexpected type: ' .. type(value))
            end
            function isArray(value) return type(value) == 'table' end
            function argBooleanFlag(value, name, default)
                if value == nil then return default end
                assert(type(value) == 'boolean'); return value
            end
            function uidQueryLevel(uid) assert(uid == 123); return level end
            function uidPostXML(uid, path, format, value)
                assert(uid == 123); xml = string.format(format, value)
            end
            function setEventHandler(value) handlers = value end
            package.preload['npc.include.dailyquest'] = function()
                return {setQuest = function(uid, args)
                    assert(uid == 123); assert(args == nil)
                    daily_calls = daily_calls + 1
                end}
            end
            function addQuestTrigger(kind, callback)
                assert(kind == SYS_ON_ONLINE); login_callback = callback
            end
            function getLevel() return level end
            function postString(message) table.insert(messages, message) end
            function uidRemoteCall(uid, code)
                assert(uid == 123); return assert(load(code))()
            end
        ''')
        self.lua.execute(NPC.read_text(encoding='utf-8'))

    def render(self, event):
        self.g.handlers[event](123, None)
        return ET.fromstring(self.g.xml)

    def test_every_page_renders_valid_xml_and_all_links_resolve(self):
        for level in (1, 6, 7, 30):
            self.g.level = level
            for event in self.g.handlers:
                if event == 'guide_daily':
                    continue
                with self.subTest(level=level, event=event):
                    page = self.render(event)
                    self.assertEqual(page.tag, 'layout')
                    for link in page.iter('event'):
                        self.assertTrue(link.attrib['id'] == 'exit' or
                                        self.g.handlers[link.attrib['id']] is not None)
                    # Bound copy length for the original narrow NPC dialog.
                    for paragraph in page.findall('par'):
                        self.assertLessEqual(len(''.join(paragraph.itertext())), 58)
        self.assertEqual(self.g.daily_calls, 0)

    def test_below_seven_has_no_accept_link(self):
        for level in (1, 6):
            self.g.level = level
            page = self.render('guide_activities')
            self.assertNotIn('guide_daily', [e.attrib['id'] for e in page.iter('event')])

    def test_direct_or_stale_daily_event_rechecks_level(self):
        self.g.level = 7
        self.render('guide_activities')
        self.g.level = 6
        self.g.handlers['guide_daily'](123, 'forged payload')
        self.assertEqual(self.g.daily_calls, 0)

    def test_seven_and_above_delegate_to_existing_daily_service(self):
        for level in (7, 30):
            self.g.level = level
            page = self.render('guide_activities')
            self.assertIn('guide_daily', [e.attrib['id'] for e in page.iter('event')])
            self.g.handlers['guide_daily'](123, 'ignored payload')
        self.assertEqual(self.g.daily_calls, 2)

    def test_operation_copy_matches_pinned_input_code(self):
        text = ''.join(self.render('guide_controls').itertext())
        self.assertIn('右键点击可通行的地面', text)
        self.assertIn('左键点击怪物', text)
        self.assertIn('Tab', text)

    def test_login_hint_is_low_level_only_and_has_no_persistent_writes(self):
        self.lua.execute(HINT.read_text(encoding='utf-8'))
        self.g.login_callback(123)
        self.assertEqual(len(self.g.messages), 1)
        self.assertIn('456，393', self.g.messages[1])
        self.g.level = 7
        self.g.login_callback(123)
        self.assertEqual(len(self.g.messages), 1)


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        test_output = ROOT / '.test-output'
        test_output.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_output)
        # Verify the resolved cleanup target remains inside the test workspace.
        assert Path(self.temp.name).resolve().is_relative_to(test_output.resolve())
        self.addCleanup(self.temp.cleanup)
        self.server = Path(self.temp.name) / 'server'
        self.scripts = self.server / 'script'
        source = Path(os.environ['MIR2X_SCRIPT_ROOT'])
        self.manifest = json.loads((OVERLAY / 'baseline.json').read_text(encoding='utf-8'))
        for relative in self.manifest['dependencies']:
            dest = self.scripts / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, dest)
        for relative in self.manifest['replace_empty']:
            dest = self.scripts / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.touch()

    def test_original_and_already_patched_layouts_are_accepted_without_changes(self):
        self.assertEqual(checker.check(self.server), [])
        for patch in SCRIPTS.rglob('*.lua'):
            dest = self.scripts / patch.relative_to(SCRIPTS)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(patch, dest)
        before = {p: p.read_bytes() for p in self.scripts.rglob('*.lua')}
        self.assertEqual(checker.check(self.server), [])
        self.assertEqual(before, {p: p.read_bytes() for p in self.scripts.rglob('*.lua')})

    def test_custom_npc_is_not_treated_as_safe_to_replace(self):
        target = self.scripts / self.manifest['replace_empty'][0]
        target.write_text('-- existing customization', encoding='utf-8')
        self.assertTrue(any('customized NPC' in p for p in checker.check(self.server)))

    def test_changed_and_missing_dependencies_fail(self):
        deps = list(self.manifest['dependencies'])
        (self.scripts / deps[0]).write_text('-- drift', encoding='utf-8')
        (self.scripts / deps[1]).unlink()
        problems = checker.check(self.server)
        self.assertTrue(any('Changed dependency' in p for p in problems))
        self.assertTrue(any('Missing dependency' in p for p in problems))

    def test_conflicting_quest_filename_fails(self):
        target = self.scripts / 'quest' / HINT.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('-- existing quest', encoding='utf-8')
        self.assertTrue(any('name already used' in p for p in checker.check(self.server)))


if __name__ == '__main__':
    unittest.main()
