# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 23 层 · 外链核验订正（v3.2.8 → v3.2.9）】
#
# 依据：全库外链自查（2026-10-03）。方法是**三通道交叉**，不采信单路结果：
#   D1 系统解析（socket.getaddrinfo ×5）
#   D2 AliDNS DoH（https://dns.alidns.com/resolve）
#   D3 DNSPub DoH（https://doh.pub/dns-query）
#   T   TCP 80 / 443 端口探测（独立于 HTTP 层）
#   G   双协议实抓（HTTP / HTTPS 各 3 次重试）→ 状态码 + 最终 URL + <title>
# 旁证：主机侧 WebFetch（另一条出口）+ WebSearch 第三方官方页（如 `drise`、`lib`、`gs`
#       的官方通知），用于判定「站点身份」而非仅「是否可达」。
#
# 全量结果：包内唯一外链 138 条 / 引用 654 处；除 2 条外全部 200。
#
# 本轮**内容缺陷**（step59 只修了排版与协议标注，未触及下列事实错误）：
#   D-1【失效路径】`http://jxgl.dlut.edu.cn/`（裸根）**实测 404**，
#       而它被当作「综合教务系统」入口写进 S1 / S3 两个域的 DUT 绑定点（共 10 处）。
#       实测可用入口：`http://jxgl.dlut.edu.cn/student/home`（200，登录页）。
#       → 改路径（这是「链接进不去」的第三个根因，与前两个根因独立）。
#   D-2【状态过期】信息库 4 条登记与实测不符：`cw`、`tuanwei` 实为可达；`etd.lib` **名称错**
#       （不是「毕业设计系统」，是图书馆**学位论文提交系统**）；`tulip` 的「仅校园网」措辞
#       与其「外网可打开」的实测相反（保留待核实，但把话说明白）。
#   D-3【标签过期】`info` 的 `bkspy.htm` 实测标题为「本科生培养」，登记名却是「本科教学质量报告」。
#   D-4【理由过期】`www.dlutci.edu.cn` 写「https 不可达（3/3 失败）」；实测 https **可连**，
#       但**证书链不完整**（CERTIFICATE_VERIFY_FAILED）。结论（必须写 http）不变，理由须改正。
#   D-5【老域名表述】`robot.dlut.edu.cn` 被列入「老域名坑」，实测**仍 200 且与 `aihub` 同站**；
#       `zhjw` / `zdysc` **域名仍解析**（只是服务已停 / 403）。
#
# 用法：python scripts/_build/v3/step60_url_audit.py [仓库根]
# 幂等：改写一律带**哨兵**（判据不看整块内容）；版本号用**全部替换**。
# -------------------------------------------------------------------------------
import glob
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD, NEW = '3.2.8', '3.2.9'

BAD_JWGL = 'http://jxgl.dlut.edu.cn/ '
GOOD_JWGL = 'http://jxgl.dlut.edu.cn/student/home '


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs):
    """pairs: (old, new, sentinel_or_None). 幂等：sentinel 命中即视为已改。"""
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel)
        return
    o = t
    for item in pairs:
        a, b = item[0], item[1]
        sent = item[2] if len(item) > 2 else None
        if sent and sent in t:
            print('  [SAME] %s :: %r' % (rel, sent[:44]))
            continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:44]))
            continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:44]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


# =========================================================== D-1 失效路径：jxgl 裸根 404
print('== D-1) 综合教务系统：裸根 404 → 可用登录入口（S1 / S3 两域 + 各 skill + v2 源头）==')
FILES = glob.glob(os.path.join(ROOT, 'domains/*/_domain.md'))
FILES += glob.glob(os.path.join(ROOT, 'domains/*/skills/local/*/SKILL.md'))
FILES += glob.glob(os.path.join(ROOT, 'commands/*.md')) + [os.path.join(ROOT, 'SKILL.md')]
n_tot, f_tot = 0, 0
for p in sorted(set(FILES)):
    if not os.path.isfile(p):
        continue
    t = io.open(p, 'r', encoding='utf-8').read()
    if BAD_JWGL not in t:
        continue
    k = t.count(BAD_JWGL)
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(BAD_JWGL,
                                                                  GOOD_JWGL))
    f_tot += 1
    n_tot += k
    print('  [OK]   %-58s %d 处' % (os.path.relpath(p, ROOT).replace('\\', '/'), k))
print('  合计 %d 文件 / %d 处（期望 10 文件 / 10 处）' % (f_tot, n_tot))

# v2 历史层源头（只读保留、不重跑，但内容须与现行树一致，避免「照抄即复发」）
n = replace_all('scripts/_build/build_qihang_v2.py',
                'http://jxgl.dlut.edu.cn/（', 'http://jxgl.dlut.edu.cn/student/home （')
print('  v2 源头 build_qihang_v2.py：%d 处' % n)

# =========================================================== D-2/D-3/D-4/D-5 信息库事实订正
print('== D-2/D-3/D-4/D-5) references/dlut-official-sites.md 事实订正 ==')
edit('references/dlut-official-sites.md', [
    # 头部：核验轮次与口径
    ('> 网址核验记录见 `references/dlut-url-verification.md`（最近一轮 **2026-10-02 程序化实抓 · 105 域名**）。',
     '> 网址核验记录见 `references/dlut-url-verification.md`（最近一轮 **2026-10-03 全量外链自查 · '
     '138 条外链 / 三通道交叉**，见该文件 §十一）。',
     '最近一轮 **2026-10-03 全量外链自查'),

    # D-3 标签错误
    ('| 本科教学质量报告 | https://info.dlut.edu.cn/xxgklm/bkspy.htm | ✅ |',
     '| 本科生培养（信息公开网栏目） | https://info.dlut.edu.cn/xxgklm/bkspy.htm '
     '| ✅ 实测页面标题「本科生培养」 |',
     '本科生培养（信息公开网栏目）'),

    # D-2 etd.lib 名称 + 证据
    ('| 毕业设计系统 | http://etd.lib.dlut.edu.cn | ⚠️ 仅校园网（外网 3/3 探测失败） |',
     '| 学位论文提交系统（图书馆「论文提交」） | http://etd.lib.dlut.edu.cn '
     '| ⚠️ **仅 HTTP**；入口页外网可打开（2026-10-03 三通道复测 200，浏览器兼容提示页），'
     '**实际提交需校园网 / WebVPN** |',
     '学位论文提交系统（图书馆「论文提交」）'),

    # D-2 tulip 措辞
    ('| 校园网自助服务 tulip | http://tulip.dlut.edu.cn/ | ⚠️ **仅校园网** |',
     '| 校园网自助服务 tulip | http://tulip.dlut.edu.cn/ '
     '| ⚠️ **仅 HTTP**；登录页外网可达（2026-10-03 三通道复测 200）；'
     '业务是否限校园网以校方说明为准 |',
     '业务是否限校园网以校方说明为准'),

    # D-2 财务处：实测公开可达
    ('| 财务处 | http://cw.dlut.edu.cn/ | ⚠️ **登录后仍受限**（实测仍返回「系统提示」）→ 需校内网/VPN |',
     '| 财务处 | http://cw.dlut.edu.cn/ | ✅ **站点公开可达**（2026-10-03 复测 200「财务处(内控办)」）；'
     '个人缴费 / 报销数据需登录 |',
     '站点公开可达'),

    # D-2 校团委：站点已改版
    ('| 校团委 | https://tuanwei.dlut.edu.cn/ | ⚠️ 站点存在但根页返回「系统提示」 |',
     '| 校团委 | https://tuanwei.dlut.edu.cn/ | ✅ 站点可达（2026-10-03 复测 200，标题「新团委」＝已改版） |',
     '标题「新团委」＝已改版'),

    # D-5 老域名表述
    ('4. **老域名坑**：`eee→ee`（电气）、`zdysc→chem`（化学）、`robot→aihub`（人工智能）、'
     '`smedut→ic`（集成电路）、`ssdut→ss`（软件）、`life→biotech`（生物工程）。',
     '4. **老域名坑**：`eee→ee`（电气）、`zdysc→chem`（化学）、`robot→aihub`（人工智能）、'
     '`smedut→ic`（集成电路）、`ssdut→ss`（软件）、`life→biotech`（生物工程）。\n'
     '   **2026-10-03 复测修正**：老域名的处置**不统一**，不要一律当「已死」——\n'
     '   · `robot` **仍 200 且与 `aihub` 同站**（可访问，但对外应统一给 `aihub`）；\n'
     '   · `zhjw` / `zdysc` **域名仍解析**（分别为 202.118.65.70 / 202.118.76.180），'
     '但**服务已停**（`zhjw` 80/443 均无监听；`zdysc` 两协议均 403）；\n'
     '   · `eee` / `smedut` / `ssdut` / `life` **已无解析**（三通道均 NXDOMAIN）。',
     '老域名的处置**不统一**'),

    # D-4 dlutci https 的真实理由
    ('5. **仅 http 可用**：`www.dlutci.edu.cn` 的 https 不可达（3/3 失败），**必须写 http**。',
     '5. **仅 http 可用**：`www.dlutci.edu.cn` 的 **https 证书链不完整**'
     '（2026-10-03 实测 `CERTIFICATE_VERIFY_FAILED`；浏览器会报不安全）→ **必须写 http**。'
     '（旧表述「https 不可达 3/3 失败」不准确：https 端口可连、只是证书校验不过。）',
     '的 **https 证书链不完整**'),

    # §8 清单：校团委已出清；毕业设计系统正名
    ('## 8. 未核实清单（勿直接使用，共 17 条）',
     '## 8. 未核实清单（勿直接使用，共 16 条）',
     '共 16 条'),
    ('研究生工作部官网 · 校团委内容页 · 旧教务 zhjw · 毕业设计系统 · tulip 自助服务',
     '研究生工作部官网 · 旧教务 zhjw · 学位论文提交系统（提交需校园网 / WebVPN） · tulip 自助服务',
     '学位论文提交系统（提交需校园网 / WebVPN）'),
    ('> 盘锦生命科学与药学学院（已并入 `hyxy`）。',
     '> 盘锦生命科学与药学学院（已并入 `hyxy`）。\n'
     '>\n'
     '> **2026-10-03 已出清 1 项**（17 → 16）：**「校团委内容页」** —— `tuanwei.dlut.edu.cn` '
     '复测 200（标题「新团委」，站点已改版）→ 已在 §5 由 ⚠️ 升为 ✅。',
     '2026-10-03 已出清 1 项'),

    # 统计口径重算（✅ 79→81 / ⚠️ 12→10；§8 17→16）
    ('- 数据条目核验分布：**✅ 79 / ⚠️ 12 / 未标注 51**（合计 142）',
     '- 数据条目核验分布：**✅ 81 / ⚠️ 10 / 未标注 51**（合计 142）',
     '✅ 81 / ⚠️ 10 / 未标注 51'),
    ('- 显式标注 **✅ 已核验：79 条**',
     '- 显式标注 **✅ 已核验：81 条**',
     '已核验：81 条'),
    ('- 显式标注 **⚠️ 待核实：12 条**（另有 §8「未核实清单」**17 项** URL；',
     '- 显式标注 **⚠️ 待核实：10 条**（另有 §8「未核实清单」**16 项** URL；',
     '待核实：10 条'),
])

# =========================================================== D-2 同源：登录站清单的措辞
print('== D-2′) references/dlut-login-sites.md：财务处口径与信息库对齐 ==')
edit('references/dlut-login-sites.md', [
    ('| 8 | 财务处 | http://cw.dlut.edu.cn/ | 缴费、报销进度 | F4 | 方案 C |',
     '| 8 | 财务处 | http://cw.dlut.edu.cn/ | 缴费、报销进度 | F4 | 方案 C'
     '（站点公开可达；个人数据需登录，只读状态） |',
     '站点公开可达；个人数据需登录'),
])

# =========================================================== C 核验记录：三通道复测（§十一）
print('== C) references/dlut-url-verification.md：加「引用前必读」横幅 + 追加 §十一 ==')
edit('references/dlut-url-verification.md', [
    ('> 规则：**未抓到页面内容的，一律判 ⚠️ 或 ❌，不凭常识标 ✅**；待确认项**每个至少尝试 5 次**',
     '> 规则：**未抓到页面内容的，一律判 ⚠️ 或 ❌，不凭常识标 ✅**；待确认项**每个至少尝试 5 次**\n'
     '>\n'
     '> ⚠️ **引用前必读（2026-10-03 加）**：本文件 §二 / §三 / §四 / §十 属**历史轮次**记录。\n'
     '> 其中以下结论**已被 §十一 的三通道全量复测推翻**，请一律以 **§十一** 为准：\n'
     '> `cw`「登录后仍受限」｜`tuanwei`「根页返回系统提示」｜`lx`「直连失败」｜'
     '`map`「可能已停用 / 直连失败」｜`tulip`「5 次全失败」｜`etd.lib`「6 次全失败」｜\n'
     '> `portal`「302 → sso/cas/login」｜`www.dlutci.edu.cn`「https 不可达」｜`robot` 归入「老域名坑」。\n'
     '> 历史轮次的**失败判定多为「本机出网通道有限」所致，不等于站点失效** —— 这正是本轮改用多通道的原因。',
     '引用前必读（2026-10-03 加）'),
    # §10.6 的两条计数行属**当时口径**：用校验器自带的「历史口径」标记豁免，并把现行值指向 §十一
    ('- 信息库由 **159 表格行 / 139 条目** 更新为 **162 表格行 / 142 条目**（✅79 / ⚠️12 / 未标注 51）。',
     '- 信息库由 **159 表格行 / 139 条目** 更新为 **162 表格行 / 142 条目**'
     '（✅79 / ⚠️12 / 未标注 51 —— **历史口径**：2026-10-02 当时分布；'
     '2026-10-03 复核后为 ✅ 81 / ⚠️ 10 / 未标注 51，见 §十一）。',
     '2026-10-03 复核后为 ✅ 81 / ⚠️ 10 / 未标注 51'),
    ('- §8「未核实清单」由 **22 项** 收敛到 **17 项**。',
     '- §8「未核实清单」由 **22 项** 收敛到 **16 项**'
     '（**历史口径**：2026-10-02 为 17 项 → 2026-10-03 出清「校团委内容页」，见 §十一）。',
     '2026-10-03 出清「校团委内容页」，见 §十一'),
])

VERIF = r"""
---

## 十一、全量外链自查（2026-10-03 三通道交叉；2026-10-04 补录后重算）· 167 条外链

**为什么重做**：此前各轮都只用**一条**出网通道（WebFetch 或 `node fetch`），
且部分轮次把「本机抓取失败」直接判为「站点失效」→ 结论里混入了**通道噪声**。
本轮改为**多通道交叉**：任一条通道成功即算可达；「解析层查不到记录」必须
**D1/D2/D3 三条独立公共解析通道一致否定**，且 **D4 直查权威 NS 得到授权级 NXDOMAIN**，
才能作为**实测事实**登记（**且不据此断言「站点不存在」** —— 见 §11.5 口径）。

### 11.1 方法（可复现）

| 通道 | 手段 | 作用 |
|---|---|---|
| **D1** | `socket.getaddrinfo` ×5 次（间隔重试） | 系统解析 |
| **D2** | AliDNS DoH `https://dns.alidns.com/resolve` | 独立解析商 ① |
| **D3** | DNSPub DoH `https://doh.pub/dns-query` | 独立解析商 ② |
| **D4** | **直查权威 NS**（`nslookup <名> 202.118.66.6`，2026-10-04 加） | **授权应答**，不受公共解析器缓存 / 限流影响 |
| **T** | `socket.create_connection` 测 **80 / 443** 端口 | 与 HTTP 层无关的「有没有服务在听」 |
| **G** | 双协议实抓（HTTP 与 HTTPS **各重试 3 次**）→ 状态码 + 最终 URL + `<title>` | 真实页面 |
| **旁证** | 校方官方目录（`www.dlut.edu.cn/xbxy.htm` / `…/zzjg.htm`）+ 主机侧 WebFetch（**另一条出口**） | 判定「站点身份」与「官方是否仍挂此链」，不只判「通不通」 |

> ⚠️ **通道自身的坑（本轮实测）**：① 主机侧 WebFetch **会把 http 强制升级为 https**，
> 因此它对 13 个「仅 HTTP」站点一律报 `fetch failed` —— **不能**据此判它们失效；
> ② AliDNS 偶尔返回 `Status=2`（SERVFAIL，限流/抖动），**对可达站点也会出现**，
> 故 `alidns:2` **不作**失效证据，只作参考；
> ③ 本机出网**只能到达 AliDNS / DNSPub**，`dns.google` 与 `cloudflare-dns.com` 均不可达 ——
> 故「多解析商交叉」实为**两家**，需与 **D4 权威应答**合用才构成充分证据。

### 11.2 总量与结论

- 范围：包内**唯一外链 167 条 / 出现 542 处**；其中 **DUT 域内 137 条 / 504 处**，非 DUT 站点 30 条
  （`github.com` 11 条等）—— 口径与复现命令见 §11.7 ①（`http` 与 `https` 视为同一条、去尾斜杠）。
- 📌 **2026-10-04 补录**：登录站清单新增 19 条 **DUT 域内**外链（WebVPN、大模型网关、智慧学工 /
  学工系统、研究生管理信息系统、迎新、一网通办、图书馆三站等），本节四数按**同一口径**重算为
  `167 / 542 / 137 / 504`（非 DUT 仍 30 条）。新增条目的溯源与逐条实测见
  `dlut-login-sites.md` §0.3 / §1.1；这 19 条已单独实抓（200 或 `302 → SSO`），
  **未并入**下表 2026-10-03 的可达性分布快照。
- ⚠️ **口径更正**：本节初版写「唯一外链 138 条 / 引用 654 处」，但**未声明口径**，且 §11.7 的
  复现命令指向**从未随包交付**的 `urlcheck.py` → 该两数**无法复现**（已删）。现按 §11.7 ① 重算，
  并由 `scripts/aligncheck.py` 断言：改了链接不同步本节 → 直接 FAIL。
- ⚠️ **可达性分布是快照、未复测**：下表 `135 / 1 / 1 / 1` 之和 = 138，是 **2026-10-03 网络实测**
  的当时口径（口径未记录），与上行的「唯一外链 167 条」**不是同一口径**，勿混用。
- **135 条 200 ｜ 1 条 404 ｜ 1 条 NXDOMAIN ｜ 1 条为通配写法（非真实 URL）**。

| 判定 | 条数 | 说明 |
|---|---|---|
| ✅ 可达（200） | **135** | 含需登录站点（登录页 200） |
| ❌ **404** | **1** | `http://jxgl.dlut.edu.cn/`（**裸根**）→ 见 11.3 |
| ❌ NXDOMAIN | **1** | `https://xyz.dlut.edu.cn/` → 见 11.5（**负向示例里的假 URL**） |

### 11.3 本轮唯一的内容缺陷：教务系统裸根 404

`http://jxgl.dlut.edu.cn/`（**裸根**）三通道下 **TCP 80 开、实抓 404**（`404 Not Found`，548 B），
且 **443 无监听**（`ECONNREFUSED`）→ 该站点**只服务 http**，且**根路径无页面**。

**正确入口**（两者均实测 200）：

| 入口 | 实测 |
|---|---|
| `http://jxgl.dlut.edu.cn/student/home` | 200 · 标题「登入页面」 |
| `http://jxgl.dlut.edu.cn/student/ucas-sso/login` | 200 · 标题「统一身份认证」 |

→ 包内 10 处「DUT 绑定点」原写裸根（S1 域 5 处 / S3 域 5 处），**已统一改 `…/student/home`**
（生成链第 23 层 `step60_url_audit.py`）。这也是「依据里的链接进不去」的**第三个独立根因**
（前两个是 URL 紧贴中文、http 被浏览器升级为 https）。

### 11.4 「仅 HTTP」站点清单（13 个主机 · 勿手动改 https）

> **2026-10-04 更正**：本节初版写「8 条」却只列出 **6 个主机**（把 `jxgl` 的三个路径算作三条）
> → **数量与清单都不符**。现按**双协议对照实测**重列：下表中 **13 个主机的 443 全部无服务**
> （`ECONNREFUSED` 或超时），而 **80 端口全部有服务在听**。**必须写 http**。

| 主机（包内引用路径） | `http://` 实测 | `https://` 实测 | 包内引用处 |
|---|---|---|---|
| `jxgl.dlut.edu.cn`（裸根 · `/student/home` · `/student/ucas-sso/login`） | 404 · 200 · 200 | **拒绝连接** | `config.yaml` + `domains/S1`·`S3` 等 + 三个 `references/` |
| `aigw.dlut.edu.cn` | 200 | **超时** | `dlut-login-sites.md` |
| `dutsa.dlut.edu.cn/cas/account/index` | 302 → SSO | **拒绝连接** | `dlut-login-sites.md` |
| `dutxg.dlut.edu.cn` | 200 | **拒绝连接** | `dlut-login-sites.md` |
| `ecardpayment.dlut.edu.cn` | 200 | **拒绝连接** | `dlut-login-sites.md` |
| `etd.lib.dlut.edu.cn` | 200 | **超时** | `dlut-official-sites.md` |
| `lx.dlut.edu.cn` | 200 | **拒绝连接** | `dlut-login-sites.md` + `dlut-official-sites.md` + `domains/F1` |
| `map.dlut.edu.cn` | 200 | **超时** | `dlut-official-sites.md` + `domains/R6` |
| `pan.dlut.edu.cn/cas` | 303 → SSO | **拒绝连接** | `dlut-login-sites.md` |
| `pay.dlut.edu.cn` | 302 → SSO | **超时** | `dlut-login-sites.md` + `dlut-official-sites.md` + `domains/F4` |
| `szdx.dlut.edu.cn` | 200 | **超时** | `dlut-login-sites.md` |
| `tulip.dlut.edu.cn` | 302 | **超时** | `dlut-login-sites.md` + `dlut-official-sites.md` |
| `xinlixlt.dlut.edu.cn/xlogin/cas` | 302 → SSO | **超时** | `dlut-login-sites.md` |

> **其中 5 个（`aigw` / `dutsa` / `dutxg` / `ecardpayment` / `szdx`）是 2026-10-04 登录站清单
> 新增后才出现在包内的**，故初版「8 条」未含。
> 反向案例：`https://yjszs.dlut.edu.cn/zsbm` **只有 443**（无 80），故必须写 https。
> **例外（可升级协议）**：`eproof.dlut.edu.cn` 的 `sso/login.jsp` 入口（包内以 HTTP 写法登记）
> **会 302 升级到 https 并可用**，故**不属于**本节 13 个「仅 HTTP」主机。

### 11.5 「解析层查不到记录」的判定（2026-10-04 加 D4 权威 NS 复核）

> **⚠️ 判定口径（先读这段）**：本节**只登记「解析层查不到记录」这一实测事实**，
> **不据此断言「站点不存在」** —— 一个域名查不到，可能是**已迁移到新域名**（本节同时给出后继域名
> 并逐条实测）、也可能只是**当前解析视图下无记录**。**「不存在」是需要人工复查的判断，不是本节的结论。**
> 下表「判定」列写的都是**可复现的实测事实**（`NXDOMAIN` / `SERVFAIL`），
> 处置列写的是**包内应改用哪个域名**。

| 域名 | 项目中的用途 | D1 系统 | D2 AliDNS | D3 DNSPub | **D4 权威 NS** | TCP | 判定（实测事实） | 处置（改用） |
|---|---|---|---|---|---|---|---|---|
| `xyz.dlut.edu.cn` | **负向示例里的假 URL**（`library` 校验 5 的例子） | 失败 | NXDOMAIN | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录（示例用，**符合预期**） | 保留为负向示例 |
| `law.dlut.edu.cn` | 曾用以论证「法学院无独立站」 | 失败 | SERVFAIL | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录 | 法学相关给 `ip.dlut.edu.cn`（实测 200） |
| `pjlsm.dlut.edu.cn` | 盘锦·生命科学与药学学院 | 失败 | NXDOMAIN | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录 | `hyxy.dlut.edu.cn`（实测 200「化工海洋与生命学院」） |
| `pjzsjy.dlut.edu.cn` | 盘锦校区招生与就业 | 失败 | SERVFAIL | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录 | `panjin.dlut.edu.cn` / `zs.dlut.edu.cn` |
| `eee.dlut.edu.cn` | 电气老域名 | 失败 | SERVFAIL | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录（**校方目录页仍挂此旧链**） | `ee.dlut.edu.cn`（实测 200「电气工程学院」） |
| `smedut.dlut.edu.cn` | 集成电路老域名 | 失败 | NXDOMAIN | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录 | `ic.dlut.edu.cn`（实测 200「集成电路学院」） |
| `ssdut.dlut.edu.cn` | 软件学院老域名 | 失败 | NXDOMAIN | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录 | `ss.dlut.edu.cn`（实测 200「软件学院」） |
| `life.dlut.edu.cn` | 生物工程老域名 | 失败 | NXDOMAIN | NXDOMAIN | **NXDOMAIN** | 关 | 无任何解析记录 | `biotech.dlut.edu.cn`（实测 200「生物工程学院」） |

**D4 是什么、为什么它比 D1–D3 强**：`dlut.edu.cn` 的权威 NS 是
`cedrus.dlut.edu.cn`（202.118.66.6）与 `gingko.dlut.edu.cn`（202.118.66.8），
SOA 为 `cedrus.dlut.edu.cn. ygh.dlut.edu.cn. 2026092900`。
**直查权威 NS** 拿到的是**授权应答（authoritative answer）**，不再受公共解析器的缓存与限流影响 ——
这正是 `law` / `pjzsjy` / `eee` 在 AliDNS 上偶发 `Status=2`（SERVFAIL）的**通道噪声**来源。
D4 对上述 8 条**全部返回 `Non-existent domain`**，与 D3 一致、与 D2 的抖动不同。

**对照实验（排除「通配解析」造成的假阴性）**：

| 探针 | D4 权威 NS 实测 | 说明 |
|---|---|---|
| `zzzz-nope-9931.dlut.edu.cn`（随机假名） | `Non-existent domain` | 与 8 条同结果 → **`dlut.edu.cn` 未开 wildcard**，故 NXDOMAIN 是真否定 |
| `teach.dlut.edu.cn`（正对照） | `202.118.76.180` | 证明 D4 通道本身工作正常，不是「一律 NXDOMAIN」的假通道 |

**⚠️ 一处「官方死链」（交人工复查）**：校方官方目录
`www.dlut.edu.cn/xbxy.htm`（「学部学院」）与 `…/xxgk/zzjg.htm`（「组织机构」）
**至今仍把「电气工程学院」指向 `eee.dlut.edu.cn`（HTTP 老链）**，而该域名四通道一致 NXDOMAIN。
→ 这是**校方页面未更新**（历史引用），**不是包内错误**，也**不能**反证 `eee` 仍可用。
故本节措辞一律为「该域名已无解析记录，校方目录仍挂旧链」，**不写**「`eee` 不存在」。

**反例（本轮推翻「已死」认定）**：

| 域名 | 实测 | 结论 |
|---|---|---|
| `robot.dlut.edu.cn` | 三通道解析到 202.118.76.180，**http/https 均 200，标题「大连理工大学人工智能学院」** | **仍可用且与 `aihub` 同站** → 对外统一给 `aihub`，但**不得**再称其「已失效」 |
| `zhjw.dlut.edu.cn` | **仍解析**（202.118.65.70），但 **80/443 均无监听**、实抓超时 | 域名在、**服务已停** → 「已下线」成立 |
| `zdysc.dlut.edu.cn` | **仍解析**（202.118.76.180），http/https 均 **403** | 域名在、**服务已迁走** → 用 `chem` |

### 11.6 对历史结论的更正对照

| 项 | 历史结论（§二 / §三 / §十） | 2026-10-03 实测 | 处置 |
|---|---|---|---|
| `cw.dlut.edu.cn` | ⚠️「登录后仍受限，返回『系统提示』」 | **200「财务处(内控办)」，59 KB 正文** | 信息库改 **✅** |
| `tuanwei.dlut.edu.cn` | ⚠️「根页返回『系统提示』」 | **200「新团委」，33 KB** | 信息库改 **✅**；§8 出清「校团委内容页」 |
| `lx.dlut.edu.cn` | ❌「直连失败 / 仅校内」 | **200「离校系统」**（HTTP-only，内容需登录） | 信息库记「需登录 · 仅 HTTP」 |
| `map.dlut.edu.cn` | ❌「直连失败，可能已停用」 | **200「校园地图服务系统」** | 维持 ✅；补「仅 HTTP」 |
| `tulip.dlut.edu.cn` | ❌「5 次全失败 = 仅校园网」 | **200「校园网自助服务系统」**（HTTP-only） | 保留 ⚠️ 待核实，但改写理由为实测事实 |
| `etd.lib.dlut.edu.cn` | ❌「6 次全失败 = 仅校园网」；且名为「毕业设计系统」 | **200（HTTP-only，浏览器兼容提示页）**；官方口径为**图书馆「论文提交」＝学位论文提交系统** | **正名** + 理由改为「入口可达、提交需校园网 / WebVPN」 |
| `pay.dlut.edu.cn` | 曾判「失效」（§十已自纠为需登录） | 302 → `sso.dlut.edu.cn/cas/login`（HTTP-only） | 维持「需登录」 |
| `portal.dlut.edu.cn` | 「302 → `sso.dlut.edu.cn/cas/login`」 | 实测落在 **`https://portal.dlut.edu.cn/tp/`**（SPA 外壳，标题 `loading`） | 改为「门户首页为 SPA，登录在页内完成」 |
| `www.dlutci.edu.cn` | 「https 不可达（3/3 失败）」 | **https 端口可连、但证书链不完整**（`CERTIFICATE_VERIFY_FAILED`） | 结论不变（写 http），**理由改正** |
| `info…/bkspy.htm` | 登记名「本科教学质量报告」 | 页面标题 **「本科生培养」** | 按实测**改名** |

### 11.7 复现命令

```bash
# ① 计数口径 —— §11.2 的两个数就出自这段（Python 3.10+，标准库即可）
python - <<'PY'
import os, re, collections
DEV = {'validation-report.md', 'acceptance-v2.md', 'review-report-v2.2.md', 'review-report-v2.3.md',
       'review-report-v2.4.md', 'stress-test-v3.md', 'alignment-audit-v3.md', '需求确认书-v2三级结构.md'}
occ = collections.Counter()
for b, d, fs in os.walk('.'):
    d[:] = [x for x in d if x not in ('.git', '.idea', '.learnbuddy', '__pycache__', '_build')]
    for f in fs:
        if f in DEV or f == '.gitignore':
            continue
        t = open(os.path.join(b, f), encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'https?://[^\s`"\u3000）)】|>,;]+', t):
            u = m.group(0)
            if u.startswith('http:'):
                u = 'https' + u[4:]
            u = u.rstrip('/').rstrip('。').rstrip('、')
            occ[u] += 1
dut = {u: v for u, v in occ.items() if 'dlut' in u}
print('唯一外链 %d 条 / 出现 %d 处；DUT 域内 %d 条 / %d 处'
      % (len(occ), sum(occ.values()), len(dut), sum(dut.values())))
PY

# ② 单点复核（任一条即可证伪「失效」）
curl -sI http://jxgl.dlut.edu.cn/student/home          # 期望 200
python -c "import socket;print(socket.getaddrinfo('law.dlut.edu.cn',None))"   # 期望 gaierror

# ②b D4 权威 NS 直查（授权应答，不受缓存 / 限流影响；2026-10-04 加）
nslookup -type=A law.dlut.edu.cn 202.118.66.6          # 期望 Non-existent domain
nslookup -type=A eee.dlut.edu.cn 202.118.66.6          # 期望 Non-existent domain
nslookup -type=A teach.dlut.edu.cn 202.118.66.6        # 期望 202.118.76.180（正对照）
nslookup -type=A zzzz-nope-9931.dlut.edu.cn 202.118.66.6  # 期望 Non-existent domain（通配对照）
nslookup -type=NS dlut.edu.cn 202.118.66.6             # 期望 cedrus / gingko

# ③ 三通道 DNS + 端口 + 双协议实抓（D1/D2/D3 + T80/T443 + GET ×3）
#    ⚠️ 这部分的工具**不在包内**：初版本节写 `python urlcheck.py <仓库根>`，但仓库里
#    从来没有这个文件（开发期脚本未随包交付）→ 该命令**不可复现**。
#    需要三通道复核时，按 11.1 的通道表自行实现，或直接用 ② 的单点复核证伪「失效」。
```

> **口径声明**：本节的「可达」= **至少一条通道取到 HTTP 200**；
> 「解析层查不到记录」= **D1/D2/D3 三条独立公共解析通道一致否定**、**D4 权威 NS 授权级 NXDOMAIN**
> 且端口全关；本节**不把它表述为「站点不存在」**（见 §11.5 开头口径）。
> 二者都**不含**「站点内容是否权威、是否需登录」的判断 —— 后者另见 `dlut-site-profiles.md`。
> **「唯一外链」= 按 ① 归一化后的不同 URL 数**（`http://` 与 `https://` 视为同一条、去尾斜杠），
> **「出现」= 同一 URL 在包内被引用的总次数**；两数由 `scripts/aligncheck.py` 断言，改链接不同步本节即 FAIL。
"""
t = read('references/dlut-url-verification.md')
if t is None:
    print('  [SKIP] 无 references/dlut-url-verification.md')
elif '## 十一、全量外链自查' in t:
    print('  [SAME] §十一 已存在')
else:
    write('references/dlut-url-verification.md', t.rstrip('\n') + '\n' + VERIF)
    print('  [OK]   已追加 §十一')

# =========================================================== D 生成链注册
print('== D) rebuild.py 注册第 23 层 ==')
edit('scripts/_build/v3/rebuild.py', [
    ("    ('step59_link_integrity.py',     '链接可用性修复（URL 边界归一 + 仅HTTP标注 + 排查话术 + 断言与负向注入）+ 修订号 3.2.7→3.2.8'),",
     "    ('step59_link_integrity.py',     '链接可用性修复（URL 边界归一 + 仅HTTP标注 + 排查话术 + 断言与负向注入）+ 修订号 3.2.7→3.2.8'),\n"
     "    ('step60_url_audit.py',          '外链核验订正（教务裸根 404 改可用入口 + 信息库 5 处事实订正 + §十一 三通道复核）+ 修订号 3.2.8→3.2.9'),",
     'step60_url_audit.py'),
])

# =========================================================== E 修订号 3.2.8 → 3.2.9
print('== E) 修订号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        x = read(rel)
        if x and 'version: %s' % OLD in x:
            write(rel, x.replace('version: %s' % OLD, 'version: %s' % NEW))
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD, 'version: %s' % NEW),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD, '"version": "%s"' % NEW),
        ('config.yaml', 'version: %s' % OLD, 'version: %s' % NEW),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD, '**修订号 = `%s`**' % NEW),
        ('library/output-spec.md', '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % OLD,
         '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
        ('scripts/_build/README.md', '3.2.7 → 3.2.8', '3.2.8 → 3.2.9'),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s ×%d' % ('OK' if k else '--', rel, k))

print('done')
