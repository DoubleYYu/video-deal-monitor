#!/usr/bin/env python3
"""
视频平台会员优惠监控 - 抓取脚本
自动从各平台和聚合渠道抓取最新会员优惠信息
"""

import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# 配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "deals.json"
HISTORY_FILE = DATA_DIR / "price_history.json"

CST = timezone(timedelta(hours=8))


def fetch_with_retry(url, retries=3, delay=2):
    """带重试的请求"""
    for i in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i == retries - 1:
                print(f"  ⚠️  请求失败: {url} - {e}")
                return None
            time.sleep(delay)
    return None


# ─── 平台优惠抓取函数 ───────────────────────────────────────────

def get_tencent_deals():
    """腾讯视频会员优惠"""
    deals = []
    # 官方活动页
    deals.append({
        "platform": "腾讯视频",
        "name": "腾讯视频VIP月卡",
        "original_price": 30.0,
        "current_price": None,  # 动态获取
        "url": "https://film.qq.com/vip/my/",
        "source": "官方",
        "category": "月卡",
        "notes": "微信支付经常有立减活动",
    })
    deals.append({
        "platform": "腾讯视频",
        "name": "腾讯视频VIP年卡",
        "original_price": 253.0,
        "current_price": None,
        "url": "https://film.qq.com/vip/my/",
        "source": "官方",
        "category": "年卡",
        "notes": "双11/618期间年卡常有5折",
    })
    # 运营商合作
    deals.append({
        "platform": "腾讯视频",
        "name": "移动任我看套餐",
        "original_price": None,
        "current_price": 9.9,
        "url": "https://www.10086.cn/",
        "source": "中国移动",
        "category": "联合会员",
        "notes": "移动用户专享，含定向流量+视频会员",
    })
    return deals


def get_iqiyi_deals():
    """爱奇艺会员优惠"""
    deals = []
    deals.append({
        "platform": "爱奇艺",
        "name": "爱奇艺黄金会员月卡",
        "original_price": 30.0,
        "current_price": None,
        "url": "https://vip.iqiyi/",
        "source": "官方",
        "category": "月卡",
        "notes": "关注官方APP弹窗优惠",
    })
    deals.append({
        "platform": "爱奇艺",
        "name": "爱奇艺黄金会员年卡",
        "original_price": 248.0,
        "current_price": None,
        "url": "https://vip.iqiyi/",
        "source": "官方",
        "category": "年卡",
        "notes": "618/双11通常148-168元",
    })
    deals.append({
        "platform": "爱奇艺",
        "name": "京东PLUS+爱奇艺联合年卡",
        "original_price": 299.0,
        "current_price": 148.0,
        "url": "https://plus.jd.com/",
        "source": "京东",
        "category": "联合会员",
        "notes": "性价比极高，适合京东用户",
    })
    return deals


def get_youku_deals():
    """优酷会员优惠"""
    deals = []
    deals.append({
        "platform": "优酷",
        "name": "优酷酷喵会员月卡",
        "original_price": 30.0,
        "current_price": None,
        "url": "https://vip.youku.com/",
        "source": "官方",
        "category": "月卡",
        "notes": "88VIP用户优酷免费",
    })
    deals.append({
        "platform": "优酷",
        "name": "优酷VIP年卡",
        "original_price": 228.0,
        "current_price": None,
        "url": "https://vip.youku.com/",
        "source": "官方",
        "category": "年卡",
        "notes": "淘宝88VIP含优酷年卡=88元",
    })
    deals.append({
        "platform": "优酷",
        "name": "淘宝88VIP（含优酷年卡）",
        "original_price": 888.0,
        "current_price": 88.0,
        "url": "https://88vip.taobao.com/",
        "source": "淘宝",
        "category": "联合会员",
        "notes": "淘气值≥1000专享，含优酷+网易云+饿了么等",
    })
    return deals


def get_mgtv_deals():
    """芒果TV会员优惠"""
    deals = []
    deals.append({
        "platform": "芒果TV",
        "name": "芒果TV会员月卡",
        "original_price": 25.0,
        "current_price": None,
        "url": "https://www.mgtv.com/vip/",
        "source": "官方",
        "category": "月卡",
        "notes": "湖南移动用户有时有专属优惠",
    })
    deals.append({
        "platform": "芒果TV",
        "name": "芒果TV会员年卡",
        "original_price": 208.0,
        "current_price": None,
        "url": "https://www.mgtv.com/vip/",
        "source": "官方",
        "category": "年卡",
        "notes": "大促期间常有128-148元年卡",
    })
    return deals


def get_bilibili_deals():
    """B站大会员优惠"""
    deals = []
    deals.append({
        "platform": "B站",
        "name": "B站大会员月卡",
        "original_price": 25.0,
        "current_price": None,
        "url": "https://www.bilibili.com/vip",
        "source": "官方",
        "category": "月卡",
        "notes": "年度大会员性价比更高",
    })
    deals.append({
        "platform": "B站",
        "name": "B站年度大会员",
        "original_price": 168.0,
        "current_price": 148.0,
        "url": "https://www.bilibili.com/vip",
        "source": "官方",
        "category": "年卡",
        "notes": "年度大会员自动续费优惠价",
    })
    return deals


def fetch_deal_prices_from_aggregator():
    """
    尝试从优惠聚合站点获取实时价格数据
    使用什么值得买等公开信息源
    """
    price_map = {}
    
    # 尝试抓取什么值得买的视频会员优惠
    try:
        url = "https://search.smzdm.com/?c=faxian&s=%E8%A7%86%E9%A2%91%E4%BC%9A%E5%91%98&order=score"
        resp = fetch_with_retry(url)
        if resp:
            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select(".feed-row-wide")[:10]
            for item in items:
                title_el = item.select_one(".feed-block-title a")
                price_el = item.select_one(".z-highlight")
                if title_el and price_el:
                    title = title_el.get_text(strip=True)
                    price_text = price_el.get_text(strip=True)
                    price_match = re.search(r"[\d.]+", price_text)
                    if price_match:
                        price = float(price_match.group())
                        # 尝试匹配平台
                        for platform in ["腾讯", "爱奇艺", "优酷", "芒果", "B站", "bilibili"]:
                            if platform in title:
                                key = platform.replace("bilibili", "B站")
                                if key not in price_map or price < price_map[key]:
                                    price_map[key] = price
    except Exception as e:
        print(f"  ⚠️  聚合站抓取失败: {e}")
    
    return price_map


def update_deals_with_prices(deals, price_map):
    """用抓取到的价格更新优惠信息"""
    platform_key_map = {
        "腾讯视频": "腾讯",
        "爱奇艺": "爱奇艺",
        "优酷": "优酷",
        "芒果TV": "芒果",
        "B站": "B站",
    }
    for deal in deals:
        key = platform_key_map.get(deal["platform"])
        if key and key in price_map and deal["current_price"] is None:
            # 只在没有已知优惠价时使用抓取到的价格
            if deal["original_price"] and price_map[key] < deal["original_price"]:
                deal["current_price"] = price_map[key]
    return deals


def compute_discount(deal):
    """计算折扣"""
    if deal.get("original_price") and deal.get("current_price"):
        discount = deal["current_price"] / deal["original_price"]
        deal["discount"] = round(discount, 2)
        deal["save_amount"] = round(deal["original_price"] - deal["current_price"], 2)
    else:
        deal["discount"] = None
        deal["save_amount"] = None
    return deal


def load_price_history():
    """加载历史价格"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_price_history(deals):
    """保存价格历史"""
    history = load_price_history()
    today = datetime.now(CST).strftime("%Y-%m-%d")
    
    for deal in deals:
        if deal.get("current_price"):
            key = f"{deal['platform']}_{deal['name']}"
            if key not in history:
                history[key] = []
            # 去重：同一天不重复记录
            if not any(r["date"] == today for r in history[key]):
                history[key].append({
                    "date": today,
                    "price": deal["current_price"],
                })
            # 只保留最近90天
            history[key] = history[key][-90:]
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return history


def main():
    print("🎬 视频平台会员优惠监控")
    print("=" * 50)
    
    # 1. 收集各平台基础优惠信息
    print("\n📡 收集各平台优惠信息...")
    all_deals = []
    all_deals.extend(get_tencent_deals())
    all_deals.extend(get_iqiyi_deals())
    all_deals.extend(get_youku_deals())
    all_deals.extend(get_mgtv_deals())
    all_deals.extend(get_bilibili_deals())
    print(f"  ✅ 收集到 {len(all_deals)} 条优惠信息")
    
    # 2. 尝试从聚合站获取实时价格
    print("\n🔍 尝试获取实时价格...")
    price_map = fetch_deal_prices_from_aggregator()
    if price_map:
        print(f"  ✅ 获取到 {len(price_map)} 个平台的价格数据")
        all_deals = update_deals_with_prices(all_deals, price_map)
    else:
        print("  ℹ️  未获取到实时价格，使用已知参考价")
    
    # 3. 计算折扣
    all_deals = [compute_discount(d) for d in all_deals]
    
    # 4. 保存价格历史
    history = save_price_history(all_deals)
    
    # 5. 生成最终数据
    now = datetime.now(CST)
    result = {
        "updated_at": now.isoformat(),
        "deals": all_deals,
        "price_history": history,
        "tips": [
            "💡 618和双11是各平台会员最低价时间，年卡通常5-6折",
            "💡 淘宝88VIP（88元）含优酷年卡，性价比极高",
            "💡 京东PLUS+爱奇艺联合年卡约148元，适合京东用户",
            "💡 移动/联通/电信用户关注运营商合作套餐",
            "💡 各平台APP内经常有弹窗专属优惠，留意一下",
            "💡 拼多多/闲鱼等渠道价格通常更低，但注意防骗",
        ],
    }
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到 {OUTPUT_FILE}")
    print(f"   共 {len(all_deals)} 条优惠，{len(history)} 条历史记录")
    print(f"   更新时间: {now.strftime('%Y-%m-%d %H:%M:%S')} CST")


if __name__ == "__main__":
    main()
