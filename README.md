# 🎬 视频平台会员优惠监控器

自动监控各主流视频平台（腾讯视频、爱奇艺、优酷、芒果TV、B站）的会员优惠活动，帮你找到最便宜的开通方式。

## 功能

- 🔍 自动抓取各平台官方活动页面的优惠信息
- 📊 多平台价格对比，一目了然
- 🔄 GitHub Actions 定时更新，数据保持最新
- 🌐 精美网页展示，手机电脑都好用
- 💰 历史低价追踪，不再错过好价

## 技术栈

- Python 3 + requests + BeautifulSoup
- Jinja2 模板渲染静态页面
- GitHub Actions 自动更新数据
- GitHub Pages 免费托管

## 本地运行

```bash
pip install -r requirements.txt
python scripts/fetch_deals.py
python scripts/build_site.py
# 然后打开 output/index.html
```

## 自动更新

项目配置了 GitHub Actions，每天自动抓取最新优惠并更新页面。

## 数据来源

- 各平台官方活动页面
- 知乎/什么值得买等公开优惠信息汇总
- 运营商合作套餐信息

---

> 💡 本工具仅用于聚合公开的优惠信息，帮助用户做出更明智的消费决策。
