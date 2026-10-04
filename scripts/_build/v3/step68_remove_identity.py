#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retire the forced self-identification policy and its checks; bump revision."""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.3.8', '3.3.9'


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return None
    with io.open(path, 'r', encoding='utf-8') as fh:
        return fh.read()


def write(rel, text):
    path = os.path.join(ROOT, rel)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def sub(rel, pattern, replacement, flags=0):
    text = read(rel)
    if text is None:
        return
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count:
        write(rel, updated)
        print('  [OK] %s' % rel)


print('== Remove forced self-identification ==')
sub('config.yaml', r'# ============ 输出身份锁定.*?(?=# ============ 触发门)', '', re.S)
sub('SKILL.md',
    r'^## 身份锁定与安装后行为.*?(?=^## 触发门)',
    '''## 安装后行为

**安装后输出**：安装完成后**只回复一句「安装完成」**，其余一律不展示。

| 不做 | 说明 |
|---|---|
| 不报审计结果 | 安全审计 / 合规检查的结论不呈现给用户 |
| 不输出报告 | 不生成、不附带任何校验报告、清单或附件 |
| 不罗列计数 | 不展示结构自检的逐项标记与域 / skill 数量 |

- `scripts/` 下的自检脚本属**内部静默自检**：仅失败时报错，成功不输出。
- 仅当用户**主动索要**时，才展示上述细节。

''', re.M | re.S)
sub('INSTALL.md',
    r'^> \*\*安装后行为（强制）\*\*：.*$',
    '> **安装后行为（强制）**：安装完成后**只回复一句「安装完成」**——不展示审计结果、不输出校验报告、不罗列结构计数。详见 `SKILL.md`「安装后行为」与本文 §七。',
    re.M)
sub('INSTALL.md',
    r'^## 七、安装后行为约定（强制）\n.*?(?=^## |\Z)',
    '''## 七、安装后行为约定（强制）

1. **只回一句**：安装完成后仅回复「安装完成」。不展示安全审计 / 合规检查结论、不输出任何报告或清单、不罗列结构计数。
2. **静默自检**：§五 的校验脚本属**内部自检**，可运行，但**成功时不输出任何内容**，仅在失败时报错。
3. **按需说明**：不主动输出内部自检结果；用户明确索要时可说明已执行的检查及结果。

''', re.M | re.S)
sub('library/output-spec.md',
    r'^## 8\. 输出身份（强制.*?(?=^## 链接呈现规范)',
    '', re.M | re.S)
sub('commands/qihang.md',
    r'^在大工相关、学习或学生自述的语境下启用本包；.*?\n安装后身份锁定口径见 `SKILL\.md`；',
    '在大工相关、学习或学生自述的语境下启用本包；不相关请求按普通助手方式处理。\n',
    re.M)
sub('commands/qihang.md',
    r'被问及身份时按 `config\.yaml` 的固定身份口径回答。',
    '')

print('== Replace identity enforcement with absence checks ==')
sub('scripts/selfcheck.sh',
    r'# ---------- 8c\. 输出身份锁定.*?(?=# ---------- 8d\.)',
    '''# ---------- 8c. 不强制自我身份 ----------
echo "[8c] 不强制自我身份"
if grep -qE '^identity:|^[[:space:]]+self_intro:|^[[:space:]]+no_rename:' config.yaml 2>/dev/null; then
  bad "config.yaml 仍包含固定身份配置"
else
  ok "config.yaml 不含固定身份配置"
fi
for _f in SKILL.md INSTALL.md library/output-spec.md commands/qihang.md; do
  if grep -qE '人格锁定|身份锁定|identity[.]self_intro|我是连小理' "$_f" 2>/dev/null; then
    bad "$_f 仍包含强制自我身份声明"
  else
    ok "$_f 不含强制自我身份声明"
  fi
done
if grep -qF '只回复一句「安装完成」' SKILL.md 2>/dev/null; then
  ok "SKILL.md 保留安装后简短确认约定"
else
  bad "SKILL.md 缺少安装后行为约定"
fi

''', re.M | re.S)
sub('scripts/regress.sh',
    r'  echo "\[10\] 输出身份锁定.*?(?=  echo "={20,}")',
    '''  echo "[10] 不强制自我身份"
  if grep -qE '^identity:|^[[:space:]]+self_intro:|^[[:space:]]+no_rename:' config.yaml; then
    _fail "config.yaml 仍包含固定身份配置"
  else
    _ok "config.yaml 不含固定身份配置"
  fi
  for _f in SKILL.md INSTALL.md library/output-spec.md commands/qihang.md; do
    if grep -qE '人格锁定|身份锁定|identity[.]self_intro|我是连小理' "$_f"; then
      _fail "$_f 仍包含强制自我身份声明"
    else
      _ok "$_f 不含强制自我身份声明"
    fi
  done
  grep -qF '只回复一句「安装完成」' SKILL.md \\
    && _ok "SKILL.md 保留安装后简短确认约定" || _fail "SKILL.md 缺少安装后行为约定"
''', re.M | re.S)
sub('scripts/runcheck.py',
    r'    _identity = re\.search\(.*?(?=\n\n    n_chain =)',
    '''    for _file in ('SKILL.md', 'INSTALL.md', 'library/output-spec.md', 'commands/qihang.md'):
        if re.search(r'人格锁定|身份锁定|identity[.]self_intro|我是连小理', rd(_file)):
            bad(_file, '仍含强制自我身份声明')
    if re.search(r'^(?:identity:|  self_intro:|  no_rename:)', rd('config.yaml'), re.M):
        bad('config.yaml', '仍含固定身份配置')''',
    re.S)

print('== Update package revision %s -> %s ==' % (OLD_REV, NEW_REV))
domains = os.path.join(ROOT, 'domains')
for domain in sorted(os.listdir(domains)):
    skills = os.path.join(domains, domain, 'skills', 'local')
    if not os.path.isdir(skills):
        continue
    for skill in sorted(os.listdir(skills)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (domain, skill)
        text = read(rel)
        if text and 'version: %s' % OLD_REV in text:
            write(rel, text.replace('version: %s' % OLD_REV, 'version: %s' % NEW_REV))
for rel, old, new in (
        ('SKILL.md', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD_REV,
         '"version": "%s"' % NEW_REV),
        ('config.yaml', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD_REV,
         '**修订号 = `%s`**' % NEW_REV),
        ('library/output-spec.md', '如 `3.3.0` → `%s`）。' % OLD_REV,
         '如 `3.3.0` → `%s`）。' % NEW_REV),
):
    text = read(rel)
    if text and old in text:
        write(rel, text.replace(old, new))
        print('  [OK] %s' % rel)

print('done')
