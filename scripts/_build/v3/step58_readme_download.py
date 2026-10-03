# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 21 层 · README 下载区（v3.2.6 → v3.2.7）】
# 用途：在 README 顶部加「下载与快速开始」区，给出 **release 分支**（纯净交付树）的
#       一键下载地址与安装位置 —— 让拿到仓库的人立刻知道该下哪个分支。
# 用法：python scripts/_build/v3/step58_readme_download.py [仓库根]
# 幂等：插入带**哨兵**（`## 0. 下载与快速开始`），重复执行判 SAME。
# -------------------------------------------------------------------------------
import os, io, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD, NEW = '3.2.6', '3.2.7'

BLOCK = """## 0. 下载与快速开始

| 方式 | 一步到位 |
|---|---|
| **下载交付包（推荐）** | [`release` 分支 ZIP](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/release.zip) |
| 在线浏览 | [github.com/xiaojun10086/qihang-pack/tree/release](https://github.com/xiaojun10086/qihang-pack/tree/release) |
| 命令行安装 | `git clone -b release https://github.com/xiaojun10086/qihang-pack.git` |

> **`release` 分支 = 纯净交付树**（173 个文件）：只含运行所需内容 —— 无构建脚本、无内部过程文档、无本机路径。
> 下载后把目录放到 `~/.learnbuddy/skills/qihang`（用户级）或当前工作区 `.learnbuddy/skills/qihang`（项目级）即可使用，
> **无需安装任何依赖**（私密站只读为可选功能，见 `INSTALL.md` §六）。
> 开发树（含生成器链与过程文档）在 [`main` 分支](https://github.com/xiaojun10086/qihang-pack)。

---

"""


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


print('== README 下载区 ==')
t = read('README.md')
if t is None:
    print('  [SKIP] 无 README.md')
elif '## 0. 下载与快速开始' in t:
    print('  [SAME] 哨兵已存在')
elif '## 1. 三级结构' in t:
    write('README.md', t.replace('## 1. 三级结构', BLOCK + '## 1. 三级结构', 1))
    print('  [OK]   已插入「下载与快速开始」区')
else:
    print('  [MISS] 未找到锚点 ## 1. 三级结构')

print('== 修订号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        if replace_all('domains/%s/skills/local/%s/SKILL.md' % (d, s),
                       'version: %s' % OLD, 'version: %s' % NEW):
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD, 'version: %s' % NEW),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD, '"version": "%s"' % NEW),
        ('config.yaml', 'version: %s' % OLD, 'version: %s' % NEW),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD, '**修订号 = `%s`**' % NEW),
        ('library/output-spec.md', '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % OLD,
         '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s :: %r ×%d' % ('OK' if k else '--', rel, a[:40], k))

print('done')
