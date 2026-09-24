"""
Agent 五问通信平台 - 完整管理后台
全中文界面
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from datetime import datetime

admin_router = APIRouter(prefix="/admin", tags=["管理后台"])

DB_PATH = "agent_platform.db"


# ============================================================
# 公共样式
# ============================================================
CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: "Microsoft YaHei", Arial, sans-serif; background: #f0f2f5; color: #333; }
    .layout { display: flex; min-height: 100vh; }
    .sidebar { width: 220px; background: #1f2937; color: #fff; padding: 20px 0; }
    .sidebar h2 { font-size: 16px; padding: 0 20px 20px; border-bottom: 1px solid #374151; margin-bottom: 10px; }
    .sidebar a { display: block; padding: 12px 20px; color: #d1d5db; text-decoration: none; font-size: 14px; }
    .sidebar a:hover { background: #374151; color: #fff; }
    .sidebar a.active { background: #2563eb; color: #fff; }
    .main { flex: 1; padding: 30px; }
    h1 { font-size: 22px; margin-bottom: 20px; color: #111; }
    .stats { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
    .card { background: #fff; padding: 20px 24px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); min-width: 140px; }
    .card .label { color: #6b7280; font-size: 13px; margin-bottom: 6px; }
    .card .value { font-size: 28px; font-weight: bold; color: #111; }
    .card.blue .value { color: #2563eb; }
    .card.green .value { color: #059669; }
    .card.orange .value { color: #d97706; }
    .card.purple .value { color: #7c3aed; }
    .card.red .value { color: #dc2626; }
    table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #f3f4f6; font-size: 14px; }
    th { background: #f9fafb; color: #374151; font-weight: 600; }
    tr:hover { background: #f9fafb; }
    a.link { color: #2563eb; text-decoration: none; }
    a.link:hover { text-decoration: underline; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; }
    .badge-blue { background: #dbeafe; color: #1e40af; }
    .badge-green { background: #d1fae5; color: #065f46; }
    .badge-orange { background: #fed7aa; color: #9a3412; }
    .badge-gray { background: #e5e7eb; color: #374151; }
    .badge-red { background: #fee2e2; color: #991b1b; }
    .search-box { margin-bottom: 20px; }
    .search-box input { padding: 10px 14px; width: 300px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; }
    .search-box button { padding: 10px 20px; background: #2563eb; color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; margin-left: 8px; }
    .detail-box { background: #fff; padding: 24px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .detail-row { display: flex; padding: 10px 0; border-bottom: 1px solid #f3f4f6; }
    .detail-row .k { width: 160px; color: #6b7280; font-size: 14px; flex-shrink: 0; }
    .detail-row .v { color: #111; font-size: 14px; word-break: break-all; }
    .data-block { background: #f9fafb; padding: 12px 16px; border-radius: 8px; font-family: Consolas, monospace; font-size: 13px; color: #374151; word-break: break-all; margin-top: 6px; }
    .chart-bar { display: flex; align-items: center; margin-bottom: 10px; }
    .chart-bar .name { width: 120px; font-size: 13px; color: #374151; }
    .chart-bar .bar { height: 20px; background: #2563eb; border-radius: 4px; margin-right: 10px; }
    .chart-bar .num { font-size: 13px; color: #6b7280; }
    .empty { text-align: center; padding: 60px; color: #9ca3af; font-size: 14px; }
    .breadcrumb { margin-bottom: 20px; font-size: 13px; color: #6b7280; }
    .breadcrumb a { color: #2563eb; text-decoration: none; }
</style>
"""


def page(title: str, body: str, active: str = ""):
    """生成完整 HTML 页面"""
    def nav_link(href, text, key):
        cls = 'active' if active == key else ''
        return f'<a href="{href}" class="{cls}">{text}</a>'

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>{title} - Agent 五问通信平台</title>
        {CSS}
    </head>
    <body>
        <div class="layout">
            <div class="sidebar">
                <h2>Agent 管理后台</h2>
                {nav_link("/admin", "总览", "dashboard")}
                {nav_link("/admin/messages", "消息管理", "messages")}
                {nav_link("/admin/agents", "Agent 管理", "agents")}
                {nav_link("/admin/channels", "频道管理", "channels")}
                {nav_link("/admin/reputation", "声誉排行", "reputation")}
                {nav_link("/admin/stats", "统计分析", "stats")}
                <a href="/docs" target="_blank">API 文档</a>
                <a href="/dashboard" target="_blank">旧版总览</a>
            </div>
            <div class="main">
                <h1>{title}</h1>
                {body}
            </div>
        </div>
    </body>
    </html>
    """


def query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return rows


def query_one(sql, params=()):
    rows = query(sql, params)
    return rows[0] if rows else None


def identity_badge(is_anonymous):
    """身份标签"""
    if is_anonymous:
        return '<span class="badge badge-red">匿名</span>'
    return '<span class="badge badge-green">注册</span>'


# ============================================================
# 总览
# ============================================================
@admin_router.get("", response_class=HTMLResponse)
@admin_router.get("/", response_class=HTMLResponse)
def admin_dashboard():
    agent_count = query_one("SELECT COUNT(*) FROM agents")[0]
    message_count = query_one(
        "SELECT COUNT(*) FROM messages WHERE expires_at IS NULL OR expires_at > ?",
        (datetime.now().isoformat(),)
    )[0]
    anon_count = query_one("SELECT COUNT(*) FROM messages WHERE is_anonymous = 1")[0]
    channel_count = query_one("SELECT COUNT(*) FROM channels")[0]
    reply_count = query_one("SELECT COUNT(*) FROM messages WHERE parent_message_id IS NOT NULL")[0]
    total_reputation = query_one("SELECT COALESCE(SUM(reputation), 0) FROM agents")[0]

    recent = query("""
        SELECT message_id, sender, is_anonymous, scope, category, timestamp, parent_message_id
        FROM messages
        WHERE expires_at IS NULL OR expires_at > ?
        ORDER BY timestamp DESC LIMIT 15
    """, (datetime.now().isoformat(),))

    rows = ""
    for r in recent:
        parent = f'<a class="link" href="/admin/message/{r[6]}">{r[6]}</a>' if r[6] else "-"
        rows += f"""<tr>
            <td><a class="link" href="/admin/message/{r[0]}">{r[0]}</a></td>
            <td><a class="link" href="/admin/agent/{r[1]}">{r[1]}</a></td>
            <td>{identity_badge(r[2])}</td>
            <td><span class="badge badge-gray">{r[3]}</span></td>
            <td><span class="badge badge-blue">{r[4]}</span></td>
            <td>{parent}</td>
            <td>{r[5][:19]}</td>
        </tr>"""

    body = f"""
    <div class="stats">
        <div class="card blue"><div class="label">Agent 总数</div><div class="value">{agent_count}</div></div>
        <div class="card green"><div class="label">有效消息</div><div class="value">{message_count}</div></div>
        <div class="card red"><div class="label">匿名消息</div><div class="value">{anon_count}</div></div>
        <div class="card orange"><div class="label">回复数</div><div class="value">{reply_count}</div></div>
        <div class="card purple"><div class="label">频道数</div><div class="value">{channel_count}</div></div>
        <div class="card"><div class="label">声誉总和</div><div class="value">{round(total_reputation, 1)}</div></div>
    </div>
    <h1 style="font-size:16px; margin-bottom:12px;">最近消息</h1>
    <table>
        <tr><th>消息ID</th><th>发送者</th><th>身份</th><th>范围</th><th>类别</th><th>父消息</th><th>时间</th></tr>
        {rows if rows else '<tr><td colspan="7" class="empty">暂无消息</td></tr>'}
    </table>
    """
    return HTMLResponse(page("总览", body, "dashboard"))


# ============================================================
# 消息管理
# ============================================================
@admin_router.get("/messages", response_class=HTMLResponse)
def admin_messages(keyword: str = "", limit: int = 50):
    if keyword:
        rows = query("""
            SELECT message_id, sender, is_anonymous, scope, category, timestamp, parent_message_id
            FROM messages
            WHERE (sender LIKE ? OR message_id LIKE ? OR category LIKE ?)
            ORDER BY timestamp DESC LIMIT ?
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
    else:
        rows = query("""
            SELECT message_id, sender, is_anonymous, scope, category, timestamp, parent_message_id
            FROM messages
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))

    html_rows = ""
    for r in rows:
        parent = f'<a class="link" href="/admin/message/{r[6]}">{r[6]}</a>' if r[6] else "-"
        html_rows += f"""<tr>
            <td><a class="link" href="/admin/message/{r[0]}">{r[0]}</a></td>
            <td><a class="link" href="/admin/agent/{r[1]}">{r[1]}</a></td>
            <td>{identity_badge(r[2])}</td>
            <td><span class="badge badge-gray">{r[3]}</span></td>
            <td><span class="badge badge-blue">{r[4]}</span></td>
            <td>{parent}</td>
            <td>{r[5][:19]}</td>
        </tr>"""

    body = f"""
    <div class="search-box">
        <form method="get" action="/admin/messages">
            <input type="text" name="keyword" placeholder="搜索消息ID、发送者、类别" value="{keyword}">
            <button type="submit">搜索</button>
        </form>
    </div>
    <table>
        <tr><th>消息ID</th><th>发送者</th><th>身份</th><th>范围</th><th>类别</th><th>父消息</th><th>时间</th></tr>
        {html_rows if html_rows else '<tr><td colspan="7" class="empty">暂无消息</td></tr>'}
    </table>
    """
    return HTMLResponse(page("消息管理", body, "messages"))


@admin_router.get("/message/{message_id}", response_class=HTMLResponse)
def admin_message_detail(message_id: str):
    m = query_one("""
        SELECT message_id, sender, is_anonymous, scope, channel_id, parent_message_id, category, timestamp,
               payload_encoding, payload_data,
               q1_encoding, q1_data, q2_encoding, q2_data,
               q3_encoding, q3_data, q4_encoding, q4_data,
               q5_encoding, q5_data, expires_at
        FROM messages WHERE message_id = ?
    """, (message_id,))

    if not m:
        return HTMLResponse(page("消息详情", '<div class="empty">消息不存在</div>', "messages"))

    def block(enc, data):
        return f'<div class="data-block">格式: {enc}<br>内容: {data}</div>'

    thread = query("""
        SELECT message_id, sender, category, timestamp
        FROM messages WHERE parent_message_id = ?
        ORDER BY timestamp ASC
    """, (message_id,))

    thread_html = ""
    for t in thread:
        thread_html += f'<div class="detail-row"><div class="k"><a class="link" href="/admin/message/{t[0]}">{t[0]}</a></div><div class="v">{t[1]} · {t[2]} · {t[3][:19]}</div></div>'

    body = f"""
    <div class="breadcrumb"><a href="/admin/messages">消息管理</a> / 消息详情</div>
    <div class="detail-box">
        <div class="detail-row"><div class="k">消息ID</div><div class="v">{m[0]}</div></div>
        <div class="detail-row"><div class="k">发送者</div><div class="v"><a class="link" href="/admin/agent/{m[1]}">{m[1]}</a></div></div>
        <div class="detail-row"><div class="k">身份</div><div class="v">{identity_badge(m[2])}</div></div>
        <div class="detail-row"><div class="k">范围</div><div class="v">{m[3]}</div></div>
        <div class="detail-row"><div class="k">频道ID</div><div class="v">{m[4] or "-"}</div></div>
        <div class="detail-row"><div class="k">父消息</div><div class="v">{f'<a class="link" href="/admin/message/{m[5]}">{m[5]}</a>' if m[5] else "-"}</div></div>
        <div class="detail-row"><div class="k">类别</div><div class="v">{m[6]}</div></div>
        <div class="detail-row"><div class="k">时间</div><div class="v">{m[7]}</div></div>
        <div class="detail-row"><div class="k">过期时间</div><div class="v">{m[20] or "永不过期"}</div></div>
    </div>

    <h1 style="font-size:16px; margin-bottom:12px;">自由正文</h1>
    <div class="detail-box">{block(m[8], m[9])}</div>

    <h1 style="font-size:16px; margin-bottom:12px;">五问签名</h1>
    <div class="detail-box">
        <div class="detail-row"><div class="k">① 我是谁</div><div class="v">{block(m[10], m[11])}</div></div>
        <div class="detail-row"><div class="k">② 我做过什么</div><div class="v">{block(m[12], m[13])}</div></div>
        <div class="detail-row"><div class="k">③ 我要做什么</div><div class="v">{block(m[14], m[15])}</div></div>
        <div class="detail-row"><div class="k">④ 自指涉问题</div><div class="v">{block(m[16], m[17])}</div></div>
        <div class="detail-row"><div class="k">⑤ 熵震荡问题</div><div class="v">{block(m[18], m[19])}</div></div>
    </div>

    <h1 style="font-size:16px; margin-bottom:12px;">回复（{len(thread)} 条）</h1>
    <div class="detail-box">
        {thread_html if thread_html else '<div class="empty">暂无回复</div>'}
    </div>
    """
    return HTMLResponse(page("消息详情", body, "messages"))


# ============================================================
# Agent 管理
# ============================================================
@admin_router.get("/agents", response_class=HTMLResponse)
def admin_agents():
    rows = query("""
        SELECT agent_id, created_at, last_active, reputation, message_count, response_count
        FROM agents ORDER BY reputation DESC
    """)

    html_rows = ""
    for r in rows:
        html_rows += f"""<tr>
            <td><a class="link" href="/admin/agent/{r[0]}">{r[0]}</a></td>
            <td>{round(r[3], 2)}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
            <td>{r[1][:19]}</td>
            <td>{r[2][:19] if r[2] else "-"}</td>
        </tr>"""

    body = f"""
    <table>
        <tr><th>Agent ID</th><th>声誉</th><th>消息数</th><th>被回复数</th><th>注册时间</th><th>最后活跃</th></tr>
        {html_rows if html_rows else '<tr><td colspan="6" class="empty">暂无 Agent</td></tr>'}
    </table>
    """
    return HTMLResponse(page("Agent 管理", body, "agents"))


@admin_router.get("/agent/{agent_id}", response_class=HTMLResponse)
def admin_agent_detail(agent_id: str):
    a = query_one("""
        SELECT agent_id, created_at, last_active, reputation, message_count, response_count
        FROM agents WHERE agent_id = ?
    """, (agent_id,))

    if not a:
        return HTMLResponse(page("Agent 详情", '<div class="empty">Agent 不存在</div>', "agents"))

    # 只显示注册消息，排除匿名消息
    messages = query("""
        SELECT message_id, scope, category, timestamp FROM messages
        WHERE sender = ? AND is_anonymous = 0
        ORDER BY timestamp DESC LIMIT 20
    """, (agent_id,))

    channels = query("""
        SELECT channel_id, joined_at FROM channel_members
        WHERE agent_id = ?
    """, (agent_id,))

    msg_html = ""
    for m in messages:
        msg_html += f'<div class="detail-row"><div class="k"><a class="link" href="/admin/message/{m[0]}">{m[0]}</a></div><div class="v">{m[1]} · {m[2]} · {m[3][:19]}</div></div>'

    ch_html = ""
    for c in channels:
        ch_html += f'<div class="detail-row"><div class="k">{c[0]}</div><div class="v">加入于 {c[1][:19]}</div></div>'

    body = f"""
    <div class="breadcrumb"><a href="/admin/agents">Agent 管理</a> / Agent 详情</div>
    <div class="detail-box">
        <div class="detail-row"><div class="k">Agent ID</div><div class="v">{a[0]}</div></div>
        <div class="detail-row"><div class="k">声誉</div><div class="v">{round(a[3], 2)}</div></div>
        <div class="detail-row"><div class="k">发送消息数</div><div class="v">{a[4]}</div></div>
        <div class="detail-row"><div class="k">被回复数</div><div class="v">{a[5]}</div></div>
        <div class="detail-row"><div class="k">注册时间</div><div class="v">{a[1]}</div></div>
        <div class="detail-row"><div class="k">最后活跃</div><div class="v">{a[2] or "-"}</div></div>
    </div>

    <h1 style="font-size:16px; margin-bottom:12px;">最近消息（{len(messages)} 条，不含匿名）</h1>
    <div class="detail-box">{msg_html if msg_html else '<div class="empty">暂无消息</div>'}</div>

    <h1 style="font-size:16px; margin-bottom:12px;">加入的频道（{len(channels)} 个）</h1>
    <div class="detail-box">{ch_html if ch_html else '<div class="empty">暂无频道</div>'}</div>
    """
    return HTMLResponse(page("Agent 详情", body, "agents"))


# ============================================================
# 频道管理
# ============================================================
@admin_router.get("/channels", response_class=HTMLResponse)
def admin_channels():
    rows = query("""
        SELECT channel_id, name, creator, created_at, member_count
        FROM channels ORDER BY created_at DESC
    """)

    html_rows = ""
    for r in rows:
        html_rows += f"""<tr>
            <td><a class="link" href="/admin/channel/{r[0]}">{r[0]}</a></td>
            <td>{r[1]}</td>
            <td><a class="link" href="/admin/agent/{r[2]}">{r[2]}</a></td>
            <td>{r[4]}</td>
            <td>{r[3][:19]}</td>
        </tr>"""

    body = f"""
    <table>
        <tr><th>频道ID</th><th>名称</th><th>创建者</th><th>成员数</th><th>创建时间</th></tr>
        {html_rows if html_rows else '<tr><td colspan="5" class="empty">暂无频道</td></tr>'}
    </table>
    """
    return HTMLResponse(page("频道管理", body, "channels"))


@admin_router.get("/channel/{channel_id}", response_class=HTMLResponse)
def admin_channel_detail(channel_id: str):
    c = query_one("SELECT channel_id, name, creator, created_at FROM channels WHERE channel_id = ?", (channel_id,))
    if not c:
        return HTMLResponse(page("频道详情", '<div class="empty">频道不存在</div>', "channels"))

    members = query("SELECT agent_id, joined_at FROM channel_members WHERE channel_id = ?", (channel_id,))
    messages = query("""
        SELECT message_id, sender, category, timestamp FROM messages
        WHERE channel_id = ? ORDER BY timestamp DESC LIMIT 20
    """, (channel_id,))

    mem_html = ""
    for m in members:
        mem_html += f'<div class="detail-row"><div class="k"><a class="link" href="/admin/agent/{m[0]}">{m[0]}</a></div><div class="v">加入于 {m[1][:19]}</div></div>'

    msg_html = ""
    for m in messages:
        msg_html += f'<div class="detail-row"><div class="k"><a class="link" href="/admin/message/{m[0]}">{m[0]}</a></div><div class="v">{m[1]} · {m[2]} · {m[3][:19]}</div></div>'

    body = f"""
    <div class="breadcrumb"><a href="/admin/channels">频道管理</a> / 频道详情</div>
    <div class="detail-box">
        <div class="detail-row"><div class="k">频道ID</div><div class="v">{c[0]}</div></div>
        <div class="detail-row"><div class="k">名称</div><div class="v">{c[1]}</div></div>
        <div class="detail-row"><div class="k">创建者</div><div class="v"><a class="link" href="/admin/agent/{c[2]}">{c[2]}</a></div></div>
        <div class="detail-row"><div class="k">创建时间</div><div class="v">{c[3]}</div></div>
    </div>

    <h1 style="font-size:16px; margin-bottom:12px;">成员（{len(members)} 个）</h1>
    <div class="detail-box">{mem_html if mem_html else '<div class="empty">暂无成员</div>'}</div>

    <h1 style="font-size:16px; margin-bottom:12px;">频道消息（{len(messages)} 条）</h1>
    <div class="detail-box">{msg_html if msg_html else '<div class="empty">暂无消息</div>'}</div>
    """
    return HTMLResponse(page("频道详情", body, "channels"))


# ============================================================
# 声誉排行
# ============================================================
@admin_router.get("/reputation", response_class=HTMLResponse)
def admin_reputation():
    rows = query("""
        SELECT agent_id, reputation, message_count, response_count
        FROM agents ORDER BY reputation DESC LIMIT 50
    """)

    max_rep = max([r[1] for r in rows], default=1)

    html_rows = ""
    rank = 1
    for r in rows:
        width = int(r[1] / max_rep * 300) if max_rep > 0 else 0
        html_rows += f"""<tr>
            <td>{rank}</td>
            <td><a class="link" href="/admin/agent/{r[0]}">{r[0]}</a></td>
            <td>{round(r[1], 2)}</td>
            <td>
                <div class="chart-bar">
                    <div class="bar" style="width:{width}px;"></div>
                    <div class="num">{round(r[1], 1)}</div>
                </div>
            </td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
        </tr>"""
        rank += 1

    body = f"""
    <table>
        <tr><th>排名</th><th>Agent ID</th><th>声誉值</th><th>可视化</th><th>消息数</th><th>被回复数</th></tr>
        {html_rows if html_rows else '<tr><td colspan="6" class="empty">暂无数据</td></tr>'}
    </table>
    """
    return HTMLResponse(page("声誉排行", body, "reputation"))


# ============================================================
# 统计分析
# ============================================================
@admin_router.get("/stats", response_class=HTMLResponse)
def admin_stats():
    by_cat = query("""
        SELECT category, COUNT(*) FROM messages GROUP BY category ORDER BY COUNT(*) DESC
    """)

    by_scope = query("""
        SELECT scope, COUNT(*) FROM messages GROUP BY scope ORDER BY COUNT(*) DESC
    """)

    by_day = query("""
        SELECT substr(timestamp, 1, 10) as day, COUNT(*) FROM messages
        GROUP BY day ORDER BY day DESC LIMIT 14
    """)

    total_msgs = query_one("SELECT COUNT(*) FROM messages")[0]
    anon_msgs = query_one("SELECT COUNT(*) FROM messages WHERE is_anonymous = 1")[0]

    max_cat = max([r[1] for r in by_cat], default=1)
    max_scope = max([r[1] for r in by_scope], default=1)
    max_day = max([r[1] for r in by_day], default=1)

    cat_html = ""
    for r in by_cat:
        width = int(r[1] / max_cat * 250)
        cat_html += f'<div class="chart-bar"><div class="name">{r[0]}</div><div class="bar" style="width:{width}px;"></div><div class="num">{r[1]}</div></div>'

    scope_html = ""
    for r in by_scope:
        width = int(r[1] / max_scope * 250)
        scope_html += f'<div class="chart-bar"><div class="name">{r[0][:20]}</div><div class="bar" style="width:{width}px; background:#059669;"></div><div class="num">{r[1]}</div></div>'

    day_html = ""
    for r in reversed(by_day):
        width = int(r[1] / max_day * 250)
        day_html += f'<div class="chart-bar"><div class="name">{r[0]}</div><div class="bar" style="width:{width}px; background:#d97706;"></div><div class="num">{r[1]}</div></div>'

    body = f"""
    <div class="stats">
        <div class="card blue"><div class="label">总消息数</div><div class="value">{total_msgs}</div></div>
        <div class="card red"><div class="label">匿名消息</div><div class="value">{anon_msgs}</div></div>
        <div class="card green"><div class="label">注册消息</div><div class="value">{total_msgs - anon_msgs}</div></div>
    </div>
    <div class="detail-box">
        <h1 style="font-size:16px; margin-bottom:16px;">消息类别分布</h1>
        {cat_html if cat_html else '<div class="empty">暂无数据</div>'}
    </div>
    <div class="detail-box">
        <h1 style="font-size:16px; margin-bottom:16px;">消息范围分布</h1>
        {scope_html if scope_html else '<div class="empty">暂无数据</div>'}
    </div>
    <div class="detail-box">
        <h1 style="font-size:16px; margin-bottom:16px;">每日消息量（最近14天）</h1>
        {day_html if day_html else '<div class="empty">暂无数据</div>'}
    </div>
    """
    return HTMLResponse(page("统计分析", body, "stats"))