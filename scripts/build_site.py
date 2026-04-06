#!/usr/bin/env python3
"""
视频平台会员优惠监控 - 静态页面生成
读取 deals.json 生成精美的 HTML 展示页面
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from jinja2 import Template

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
DEALS_FILE = DATA_DIR / "deals.json"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 视频会员优惠监控</title>
    <style>
        :root {
            --bg: #0f0f1a;
            --card: #1a1a2e;
            --card-hover: #222240;
            --accent: #e94560;
            --accent2: #0f3460;
            --text: #eee;
            --text-dim: #888;
            --green: #00d68f;
            --gold: #ffd700;
            --border: #2a2a4a;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 2.5rem 1rem;
            text-align: center;
            border-bottom: 2px solid var(--accent);
        }
        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .header h1 span { color: var(--accent); }
        .header .subtitle {
            color: var(--text-dim);
            font-size: 0.95rem;
        }
        .header .update-time {
            margin-top: 0.8rem;
            display: inline-block;
            background: rgba(233,69,96,0.15);
            color: var(--accent);
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 1.5rem 1rem;
        }
        .filter-bar {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
            justify-content: center;
        }
        .filter-btn {
            background: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.5rem 1.2rem;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: var(--accent);
            border-color: var(--accent);
            color: #fff;
        }
        .section-title {
            font-size: 1.3rem;
            margin: 2rem 0 1rem;
            padding-left: 0.8rem;
            border-left: 4px solid var(--accent);
        }
        .deals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1rem;
        }
        .deal-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.2rem;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        .deal-card:hover {
            background: var(--card-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(233,69,96,0.15);
        }
        .deal-card .platform-tag {
            display: inline-block;
            padding: 0.2rem 0.8rem;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.6rem;
        }
        .platform-tencent { background: rgba(0,150,136,0.2); color: #4db6ac; }
        .platform-iqiyi { background: rgba(0,180,0,0.15); color: #66bb6a; }
        .platform-youku { background: rgba(255,87,34,0.15); color: #ff8a65; }
        .platform-mgtv { background: rgba(255,193,7,0.15); color: #ffd54f; }
        .platform-bilibili { background: rgba(0,161,214,0.15); color: #4fc3f7; }
        .deal-card .name {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            line-height: 1.4;
        }
        .price-row {
            display: flex;
            align-items: baseline;
            gap: 0.8rem;
            margin-bottom: 0.5rem;
        }
        .price-current {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--accent);
        }
        .price-original {
            font-size: 0.95rem;
            color: var(--text-dim);
            text-decoration: line-through;
        }
        .discount-badge {
            background: var(--accent);
            color: #fff;
            padding: 0.15rem 0.6rem;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .save-text {
            color: var(--green);
            font-size: 0.85rem;
            margin-bottom: 0.6rem;
        }
        .notes {
            color: var(--text-dim);
            font-size: 0.82rem;
            line-height: 1.5;
            border-top: 1px solid var(--border);
            padding-top: 0.6rem;
            margin-top: 0.6rem;
        }
        .notes::before {
            content: "💡 ";
        }
        .source-tag {
            position: absolute;
            top: 1rem;
            right: 1rem;
            font-size: 0.7rem;
            color: var(--text-dim);
            background: rgba(255,255,255,0.05);
            padding: 0.15rem 0.5rem;
            border-radius: 8px;
        }
        .tips-section {
            margin-top: 2.5rem;
            background: linear-gradient(135deg, rgba(15,52,96,0.3), rgba(26,26,46,0.5));
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
        }
        .tips-section h3 {
            margin-bottom: 0.8rem;
            color: var(--gold);
        }
        .tips-section ul {
            list-style: none;
        }
        .tips-section li {
            padding: 0.4rem 0;
            color: var(--text-dim);
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-dim);
            font-size: 0.8rem;
        }
        .footer a {
            color: var(--accent);
            text-decoration: none;
        }
        .no-price {
            color: var(--gold);
            font-size: 0.9rem;
            font-style: italic;
        }
        .compare-table {
            width: 100%;
            margin-top: 2rem;
            border-collapse: collapse;
            background: var(--card);
            border-radius: 12px;
            overflow: hidden;
        }
        .compare-table th {
            background: var(--accent2);
            padding: 0.8rem;
            text-align: center;
            font-size: 0.85rem;
        }
        .compare-table td {
            padding: 0.7rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
            font-size: 0.85rem;
        }
        .compare-table tr:hover td {
            background: var(--card-hover);
        }
        @media (max-width: 600px) {
            .header h1 { font-size: 1.5rem; }
            .deals-grid { grid-template-columns: 1fr; }
            .compare-table { font-size: 0.75rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 视频会员<span>优惠监控</span></h1>
        <div class="subtitle">帮你找到最便宜的视频会员开通方式</div>
        <div class="update-time">🔄 数据更新: {{ updated_at }}</div>
    </div>

    <div class="container">
        <!-- 平台筛选 -->
        <div class="filter-bar">
            <button class="filter-btn active" onclick="filterPlatform('all')">全部平台</button>
            {% for p in platforms %}
            <button class="filter-btn" onclick="filterPlatform('{{ p }}')">{{ p }}</button>
            {% endfor %}
        </div>

        <!-- 横向对比表 -->
        <h2 class="section-title">📊 年卡价格对比</h2>
        <table class="compare-table">
            <thead>
                <tr>
                    <th>平台</th>
                    <th>年卡原价</th>
                    <th>大促价</th>
                    <th>联合会员</th>
                    <th>最佳方案</th>
                </tr>
            </thead>
            <tbody>
                {% for row in compare_table %}
                <tr>
                    <td><strong>{{ row.platform }}</strong></td>
                    <td>¥{{ row.original }}</td>
                    <td style="color: var(--accent); font-weight:600;">{{ row.sale }}</td>
                    <td>{{ row.bundle }}</td>
                    <td style="color: var(--green); font-weight:600;">{{ row.best }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <!-- 优惠列表 -->
        <h2 class="section-title">🔥 全部优惠信息</h2>
        <div class="deals-grid">
            {% for deal in deals %}
            <div class="deal-card" data-platform="{{ deal.platform }}">
                <span class="source-tag">{{ deal.source }}</span>
                <span class="platform-tag platform-{{ deal.platform_class }}">{{ deal.platform }}</span>
                <div class="name">{{ deal.name }}</div>
                <div class="price-row">
                    {% if deal.current_price %}
                    <span class="price-current">¥{{ deal.current_price }}</span>
                    {% if deal.original_price %}
                    <span class="price-original">¥{{ deal.original_price }}</span>
                    {% endif %}
                    {% if deal.discount %}
                    <span class="discount-badge">{{ deal.discount }}折</span>
                    {% endif %}
                    {% else %}
                    <span class="no-price">⚡ 价格浮动，点击查看详情</span>
                    {% endif %}
                </div>
                {% if deal.save_amount %}
                <div class="save-text">💰 省 ¥{{ deal.save_amount }}</div>
                {% endif %}
                <div class="notes">{{ deal.notes }}</div>
            </div>
            {% endfor %}
        </div>

        <!-- 省钱技巧 -->
        {% if tips %}
        <div class="tips-section">
            <h3>💎 省钱小技巧</h3>
            <ul>
                {% for tip in tips %}
                <li>{{ tip }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>

    <div class="footer">
        <p>数据仅供参考，以各平台实际价格为准</p>
        <p>由 <a href="https://github.com/DoubleYYu">DoubleYYu</a> 的自动化工具生成</p>
    </div>

    <script>
        function filterPlatform(platform) {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.deal-card').forEach(card => {
                if (platform === 'all' || card.dataset.platform === platform) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>"""


PLATFORM_CLASS = {
    "腾讯视频": "tencent",
    "爱奇艺": "iqiyi",
    "优酷": "youku",
    "芒果TV": "mgtv",
    "B站": "bilibili",
}

COMPARE_DATA = [
    {"platform": "腾讯视频", "original": "253", "sale": "~128 (618/双11)", "bundle": "移动套餐9.9/月", "best": "大促年卡"},
    {"platform": "爱奇艺",   "original": "248", "sale": "~148 (618/双11)", "bundle": "京东PLUS联合148", "best": "京东联合年卡"},
    {"platform": "优酷",     "original": "228", "sale": "~99 (大促)",      "bundle": "88VIP含年卡=88元", "best": "淘宝88VIP ¥88"},
    {"platform": "芒果TV",   "original": "208", "sale": "~128 (大促)",    "bundle": "-", "best": "大促年卡"},
    {"platform": "B站",      "original": "168", "sale": "148 (自动续费)",  "bundle": "-", "best": "年度大会员148"},
]


def main():
    # 读取数据
    if not DEALS_FILE.exists():
        print("❌ 未找到 deals.json，请先运行 fetch_deals.py")
        return

    with open(DEALS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    deals = data.get("deals", [])
    tips = data.get("tips", [])
    updated_at = data.get("updated_at", "")

    # 格式化时间
    if updated_at:
        try:
            dt = datetime.fromisoformat(updated_at)
            updated_at = dt.strftime("%Y-%m-%d %H:%M CST")
        except Exception:
            pass

    # 添加平台 CSS class
    for deal in deals:
        deal["platform_class"] = PLATFORM_CLASS.get(deal["platform"], "")

    # 按折扣排序
    deals.sort(key=lambda d: d.get("discount") or 999)

    # 平台列表
    platforms = list(dict.fromkeys(d["platform"] for d in deals))

    # 渲染
    template = Template(HTML_TEMPLATE)
    html = template.render(
        deals=deals,
        platforms=platforms,
        tips=tips,
        updated_at=updated_at,
        compare_table=COMPARE_DATA,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 页面已生成: {output_file}")


if __name__ == "__main__":
    main()
