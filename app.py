#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分析与可视化应用 - 增强版
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
import pandas as pd
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Radar, HeatMap
from pyecharts import options as opts
from pyecharts.globals import CurrentConfig
from streamlit.components.v1 import html
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
import math
import time

CurrentConfig.ONLINE_HOST = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/"

STOP_WORDS = set([
    '的', '了', '和', '是', '就', '都', '而', '及', '与', '在', '这', '那', '你', '我', '他', '她', '它',
    '们', '之', '于', '以', '为', '对', '上', '下', '左', '右', '前', '后', '来', '去', '到', '过', '着',
    '也', '但', '却', '并', '且', '还', '或', '又', '很', '更', '最', '太', '非常', '极', '总', '常', '将',
    '会', '要', '能', '可以', '应该', '应该', '必须', '可能', '也许', '一定', '肯定', '当然', '如果', '因为',
    '所以', '虽然', '但是', '然而', '因此', '因而', '于是', '由于', '为了', '关于', '对于', '通过', '根据',
    '按照', '经过', '随着', '使得', '导致', '造成', '带来', '产生', '引起', '发生', '变成', '成为', '作为',
    '觉得', '认为', '知道', '了解', '认识', '明白', '理解', '相信', '希望', '想要', '喜欢', '爱', '恨',
    '怕', '想', '说', '做', '看', '听', '读', '写', '吃', '喝', '玩', '乐', '学习', '工作', '生活', '家庭',
    '社会', '国家', '世界', '人类', '人民', '群众', '个人', '自己', '他人', '大家', '人们', '别人', '同学',
    '朋友', '老师', '学生', '父母', '子女', '兄弟', '姐妹', '丈夫', '妻子', '孩子', '老人', '青年', '中年',
    '少年', '儿童', '婴儿', '男人', '女人', '中国人', '外国人', '汉族', '少数民族', '古代', '现代', '当代',
    '未来', '历史', '现在', '今天', '明天', '昨天', '过去', '现在', '将来', '时间', '空间', '地点', '位置',
    '地方', '城市', '农村', '乡镇', '村庄', '街道', '社区', '学校', '医院', '公司', '工厂', '企业', '政府',
    '军队', '警察', '法律', '法规', '制度', '政策', '方针', '路线', '原则', '方法', '方式', '手段', '途径',
    '渠道', '工具', '设备', '机器', '电脑', '手机', '互联网', '网络', '信息', '数据', '知识', '文化', '教育',
    '科学', '技术', '艺术', '音乐', '美术', '文学', '体育', '运动', '健康', '疾病', '医疗', '卫生', '环境',
    '自然', '资源', '能源', '污染', '保护', '发展', '进步', '落后', '成功', '失败', '胜利', '失败', '优点',
    '缺点', '长处', '短处', '好', '坏', '优', '劣', '美', '丑', '善', '恶', '真', '假', '是', '非', '对', '错',
    '正', '反', '左', '右', '前', '后', '上', '下', '里', '外', '内', '外', '东', '西', '南', '北', '中', '间',
    '边', '角', '面', '点', '线', '片', '块', '个', '只', '条', '本', '张', '件', '双', '对', '群', '堆', '批',
    '伙', '帮', '班', '队', '组', '排', '列', '行', '列', '阵', '营', '军', '师', '旅', '团', '营', '连', '排',
    '班', '组', '人', '员', '工', '农', '兵', '商', '学', '兵', '党', '团', '队', '组织', '团体', '机构', '部门',
    '单位', '公司', '企业', '工厂', '商店', '学校', '医院', '银行', '邮局', '车站', '机场', '码头', '港口',
    '道路', '桥梁', '建筑', '房屋', '公寓', '别墅', '酒店', '餐厅', '商店', '超市', '市场', '商场', '广场',
    '公园', '花园', '森林', '草原', '沙漠', '海洋', '河流', '湖泊', '山脉', '山峰', '平原', '高原', '盆地',
    '丘陵', '岛屿', '半岛', '海峡', '海湾', '海港', '海滩', '沙滩', '海岸', '河岸', '湖边', '河边', '海边',
    '山边', '路边', '窗边', '门边', '河边', '湖边', '海边', '山边', '路边', '窗边', '门边'
])

COLOR_THEMES = {
    "经典蓝": ["#1e88e5", "#42a5f5", "#64b5f6", "#90caf9", "#bbdefb"],
    "活力橙": ["#ff7043", "#ff8a65", "#ffa726", "#ffb74d", "#ffcc80"],
    "清新绿": ["#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9", "#e8f5e9"],
    "优雅紫": ["#7e57c2", "#9575cd", "#ab47bc", "#ba68c8", "#ce93d8"],
    "热情红": ["#ef5350", "#e57373", "#ef9a9a", "#ffcdd2", "#ffebee"],
    "科技感": ["#00bcd4", "#26c6da", "#4dd0e1", "#80deea", "#b2ebf2"],
}

CHART_SHAPES = ["circle", "cardioid", "diamond", "triangle-forward", "triangle", "pentagon", "star"]

POSITIVE_WORDS = set([
    '好', '优秀', '棒', '出色', '精彩', '完美', '成功', '喜悦', '幸福', '快乐', '满意',
    '感谢', '赞赏', '赞美', '称赞', '肯定', '认可', '支持', '鼓励', '希望', '信心',
    '进步', '发展', '创新', '突破', '成就', '荣誉', '荣耀', '辉煌', '卓越', '杰出',
    '美好', '温馨', '和谐', '友善', '真诚', '热情', '积极', '乐观', '自信', '勇敢',
    '坚强', '努力', '奋斗', '拼搏', '坚持', '执着', '勤奋', '刻苦', '认真', '负责'
])

NEGATIVE_WORDS = set([
    '坏', '糟糕', '失败', '失望', '痛苦', '悲伤', '难过', '伤心', '愤怒', '生气',
    '讨厌', '厌恶', '憎恨', '批评', '指责', '抱怨', '不满', '失望', '遗憾', '惋惜',
    '困难', '挫折', '障碍', '问题', '麻烦', '困扰', '烦恼', '忧虑', '焦虑', '恐惧',
    '担心', '害怕', '紧张', '压力', '疲惫', '无聊', '枯燥', '乏味', '单调', '沉闷',
    '错误', '失误', '疏忽', '损失', '浪费', '错过', '落后', '退步', '衰退', '恶化'
])

TOPIC_KEYWORDS = {
    '科技': ['科技', '技术', '互联网', '人工智能', 'AI', '数据', '软件', '硬件', '电脑', '手机'],
    '财经': ['经济', '金融', '股票', '投资', '市场', '企业', '公司', '商业', '贸易', '消费'],
    '教育': ['教育', '学校', '学生', '老师', '学习', '考试', '课程', '培训', '知识', '教育'],
    '娱乐': ['娱乐', '电影', '音乐', '游戏', '明星', '综艺', '演出', '艺术', '文化', '媒体'],
    '体育': ['体育', '运动', '比赛', '足球', '篮球', '奥运', '健身', '健康', '锻炼', '竞技'],
    '政治': ['政治', '政府', '政策', '国家', '国际', '外交', '法律', '社会', '民生', '改革'],
    '生活': ['生活', '健康', '饮食', '旅游', '美食', '购物', '家居', '时尚', '情感', '家庭'],
    '军事': ['军事', '国防', '军队', '战争', '武器', '安全', '演习', '战略', '情报', '防御'],
}

class TextAnalyzer:
    def __init__(self):
        self.text = ""
        self.word_freq = Counter()
        self.cleaned_text = ""
        self.analysis_time = None
    
    def fetch_url_content(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
    
    def clean_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        text = soup.get_text()
        text = ' '.join(text.split())
        self.cleaned_text = text
        return text
    
    def set_text(self, text):
        self.cleaned_text = text
    
    def analyze_text(self, text=None, min_length=2):
        if text:
            self.cleaned_text = text
        words = jieba.cut(self.cleaned_text)
        filtered_words = [
            word for word in words 
            if len(word) >= min_length and word not in STOP_WORDS
        ]
        self.word_freq = Counter(filtered_words)
        self.analysis_time = datetime.now().isoformat()
        return self.word_freq
    
    def get_top_words(self, n=20, sort_by='frequency', ascending=False):
        if sort_by == 'frequency':
            top_words = self.word_freq.most_common(n)
            if ascending:
                top_words = list(reversed(top_words))
        else:
            sorted_words = sorted(self.word_freq.items(), key=lambda x: x[0], reverse=not ascending)
            top_words = sorted_words[:n]
        return list(top_words)
    
    def filter_by_frequency(self, min_freq):
        filtered = {word: freq for word, freq in self.word_freq.items() if freq >= min_freq}
        return Counter(filtered)
    
    def get_word_cloud_data(self, max_words=100):
        return self.word_freq.most_common(max_words)
    
    def count_characters(self):
        text = self.cleaned_text
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_chars = sum(1 for c in text if c.isalpha())
        total_chars = len(text)
        paragraphs = max(1, text.count('。') + text.count('！') + text.count('？'))
        return {
            'chinese': chinese_chars,
            'english': english_chars,
            'total': total_chars,
            'paragraphs': paragraphs
        }
    
    def estimate_reading_time(self):
        stats = self.count_characters()
        total_words = stats['chinese'] + math.ceil(stats['english'] / 5)
        difficulty = self._estimate_difficulty()
        base_speed = 400
        adjusted_speed = base_speed / difficulty
        minutes = math.ceil(total_words / adjusted_speed)
        return {
            'minutes': minutes,
            'total_words': total_words,
            'difficulty': difficulty,
            'difficulty_label': self._get_difficulty_label(difficulty)
        }
    
    def _estimate_difficulty(self):
        text = self.cleaned_text
        unique_ratio = len(set(text)) / len(text) if text else 0
        avg_word_length = sum(len(word) for word in self.word_freq.keys()) / len(self.word_freq) if self.word_freq else 0
        difficulty = 1.0 + unique_ratio * 0.3 + (avg_word_length - 2) * 0.1
        return min(2.0, max(0.5, difficulty))
    
    def _get_difficulty_label(self, difficulty):
        if difficulty < 0.7:
            return '简单'
        elif difficulty < 1.2:
            return '中等'
        elif difficulty < 1.5:
            return '较难'
        else:
            return '困难'
    
    def analyze_sentiment(self):
        text = self.cleaned_text
        positive_count = sum(1 for word in POSITIVE_WORDS if word in text)
        negative_count = sum(1 for word in NEGATIVE_WORDS if word in text)
        total = positive_count + negative_count
        
        if total == 0:
            score = 0
            sentiment = '中性'
        else:
            score = (positive_count - negative_count) / total
            if score > 0.3:
                sentiment = '积极'
            elif score < -0.3:
                sentiment = '消极'
            else:
                sentiment = '中性'
        
        return {
            'score': round(score, 2),
            'sentiment': sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def classify_topic(self):
        topic_scores = {}
        for topic, keywords in TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in self.cleaned_text)
            topic_scores[topic] = score
        
        max_score = max(topic_scores.values()) if topic_scores else 0
        if max_score > 0:
            topics = [topic for topic, score in topic_scores.items() if score == max_score]
            tags = []
            for topic in topics:
                tags.extend([kw for kw in TOPIC_KEYWORDS[topic] if kw in self.cleaned_text][:5])
            return {
                'topics': topics,
                'tags': list(set(tags))[:10],
                'scores': topic_scores
            }
        else:
            return {
                'topics': ['其他'],
                'tags': [],
                'scores': topic_scores
            }
    
    def to_dict(self):
        return {
            'text': self.text,
            'word_freq': dict(self.word_freq),
            'cleaned_text': self.cleaned_text,
            'analysis_time': self.analysis_time
        }
    
    @classmethod
    def from_dict(cls, data):
        analyzer = cls()
        analyzer.text = data.get('text', '')
        analyzer.word_freq = Counter(data.get('word_freq', {}))
        analyzer.cleaned_text = data.get('cleaned_text', '')
        analyzer.analysis_time = data.get('analysis_time')
        return analyzer

class HistoryManager:
    HISTORY_FILE = "analysis_history.json"
    PAGE_SIZE = 10
    
    @staticmethod
    def load_history():
        if os.path.exists(HistoryManager.HISTORY_FILE):
            try:
                with open(HistoryManager.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    @staticmethod
    def save_history(history):
        with open(HistoryManager.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def add_record(source_type, source_content, analyzer):
        history = HistoryManager.load_history()
        record = {
            'id': len(history) + 1,
            'source_type': source_type,
            'source_content': source_content[:500] + '...' if len(source_content) > 500 else source_content,
            'analysis_time': analyzer.analysis_time,
            'word_count': len(analyzer.word_freq),
            'top_words': analyzer.get_top_words(10),
            'data': analyzer.to_dict()
        }
        history.insert(0, record)
        if len(history) > 100:
            history = history[:100]
        HistoryManager.save_history(history)
        return history
    
    @staticmethod
    def get_history_page(page=1, page_size=None):
        if page_size is None:
            page_size = HistoryManager.PAGE_SIZE
        history = HistoryManager.load_history()
        total_records = len(history)
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_records = history[start_idx:end_idx]
        return {
            'records': page_records,
            'total_pages': total_pages,
            'total_records': total_records,
            'current_page': page
        }
    
    @staticmethod
    def get_record(record_id):
        history = HistoryManager.load_history()
        for record in history:
            if record['id'] == record_id:
                return record
        return None
    
    @staticmethod
    def delete_record(record_id):
        history = HistoryManager.load_history()
        history = [r for r in history if r['id'] != record_id]
        HistoryManager.save_history(history)
        return history
    
    @staticmethod
    def clear_history():
        HistoryManager.save_history([])

def recommend_chart_type(data, data_type='word_frequency'):
    if data_type == 'word_frequency':
        if len(data) > 10:
            return ['词云图', '柱状图']
        else:
            return ['饼图', '柱状图']
    elif data_type == 'trend':
        return ['折线图', '柱状图']
    elif data_type == 'distribution':
        return ['散点图', '热力图']
    elif data_type == 'comparison':
        return ['雷达图', '柱状图']
    else:
        return ['柱状图', '饼图']

def compare_articles(analyzers):
    if len(analyzers) < 2:
        return None
    
    all_words = set()
    word_freqs = []
    
    for analyzer in analyzers:
        words = set(analyzer.word_freq.keys())
        all_words.update(words)
        word_freqs.append(analyzer.word_freq)
    
    common_words = all_words
    for freq in word_freqs:
        common_words = common_words.intersection(set(freq.keys()))
    
    common_words = list(common_words)[:15]
    
    comparison_data = []
    for word in common_words:
        row = {'word': word}
        for i, freq in enumerate(word_freqs):
            row[f'freq_{i}'] = freq.get(word, 0)
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    
    total_words_1 = sum(word_freqs[0].values())
    total_words_2 = sum(word_freqs[1].values())
    common_sum = sum(min(word_freqs[0].get(w, 0), word_freqs[1].get(w, 0)) for w in all_words)
    jaccard = common_sum / (total_words_1 + total_words_2 - common_sum) if (total_words_1 + total_words_2 - common_sum) > 0 else 0
    
    top_words_1 = analyzers[0].get_top_words(10)
    top_words_2 = analyzers[1].get_top_words(10)
    
    return {
        'comparison_df': df,
        'similarity': round(jaccard, 2),
        'common_words': common_words,
        'top_words_1': top_words_1,
        'top_words_2': top_words_2
    }

def render_word_cloud(data, theme_colors, shape="circle", word_size_range=[15, 80]):
    if not data or len(data) == 0:
        st.warning("⚠️ 词云图数据为空")
        return False, "数据为空"
    
    try:
        wordcloud_html = generate_word_cloud_html(data, theme_colors, shape, word_size_range)
        html(wordcloud_html, height=450)
        return True, None
    except Exception as e:
        error_msg = f"词云图渲染失败: {str(e)}\n{traceback.format_exc()}"
        st.error(f"❌ {error_msg}")
        return False, error_msg

def generate_word_cloud_html(data, theme_colors, shape="circle", word_size_range=[15, 80]):
    words = [{"name": item[0], "value": item[1]} for item in data[:100]]
    color_list = ",".join([f"'{color}'" for color in theme_colors])
    
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>词云图</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.1.0/dist/echarts-wordcloud.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; }}
        #chart {{ width: 100%; height: 400px; }}
    </style>
</head>
<body>
    <div id="chart"></div>
    <script type="text/javascript">
        var chart = echarts.init(document.getElementById('chart'));
        var option = {{
            title: {{ text: '词云图', left: 'center', top: 10, textStyle: {{ fontSize: 22 }} }},
            tooltip: {{ trigger: 'item', formatter: function(params) {{ return params.name + ': ' + params.value; }} }},
            series: [{{
                type: 'wordCloud',
                shape: '{shape}',
                gridSize: 8,
                sizeRange: [{word_size_range[0]}, {word_size_range[1]}],
                rotationRange: [-90, 90],
                rotationStep: 45,
                drawOutOfBound: false,
                textStyle: {{
                    fontFamily: 'Microsoft YaHei, sans-serif',
                    fontWeight: 'bold',
                    color: function() {{
                        var colors = [{color_list}];
                        return colors[Math.floor(Math.random() * colors.length)];
                    }}
                }},
                emphasis: {{
                    focus: 'word',
                    textStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' }}
                }},
                data: {words}
            }}]
        }};
        chart.setOption(option);
        window.addEventListener('resize', function() {{ chart.resize(); }});
    </script>
</body>
</html>
    """
    return html_template

def safe_render_chart(chart, height=400):
    try:
        chart_html = chart.render_embed()
        if not chart_html or chart_html.strip() == "":
            return False, "图表渲染结果为空"
        html(chart_html, height=height)
        return True, None
    except Exception as e:
        error_msg = f"图表渲染失败: {str(e)}\n{traceback.format_exc()}"
        return False, error_msg

def create_bar_chart(data, title="柱状图", theme_colors=None, show_values=True):
    if not data or len(data) == 0:
        return None
    bar = Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
    words, freqs = zip(*data)
    bar.add_xaxis(list(words))
    bar.add_yaxis(series_name="词频", y_axis=list(freqs), itemstyle_opts=opts.ItemStyleOpts(color=theme_colors[0] if theme_colors else "#1e88e5"))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name="词汇", axislabel_opts=opts.LabelOpts(rotate=45, font_size=11)),
        yaxis_opts=opts.AxisOpts(name="词频"),
        legend_opts=opts.LegendOpts(is_show=True)
    )
    if show_values:
        bar.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position="top", font_size=10))
    return bar

def create_pie_chart(data, title="饼图", theme_colors=None):
    if not data or len(data) == 0:
        return None
    pie = Pie(init_opts=opts.InitOpts(width="100%", height="400px"))
    pie.add(series_name="词频", data_pair=data, radius=["40%", "75%"])
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c} ({d}%)"),
        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="5%", textstyle_opts=opts.TextStyleOpts(font_size=11), type_="scroll"),
    )
    if theme_colors:
        pie.set_colors(theme_colors)
    pie.set_series_opts(label_opts=opts.LabelOpts(font_size=10, formatter="{b}: {d}%", position="outside"))
    return pie

def create_line_chart(data, title="折线图", theme_colors=None, smooth=True, show_points=True):
    if not data or len(data) == 0:
        return None
    line = Line(init_opts=opts.InitOpts(width="100%", height="400px"))
    words, freqs = zip(*data)
    line.add_xaxis(list(words))
    line.add_yaxis(
        series_name="词频", y_axis=list(freqs), is_smooth=smooth,
        symbol="circle" if show_points else "none",
        linestyle_opts=opts.LineStyleOpts(width=3, color=theme_colors[0] if theme_colors else "#1e88e5")
    )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name="词汇", axislabel_opts=opts.LabelOpts(rotate=45, font_size=11)),
        yaxis_opts=opts.AxisOpts(name="词频"),
        legend_opts=opts.LegendOpts(is_show=True)
    )
    return line

def create_scatter_chart(data, title="散点图", theme_colors=None, bubble_size=False):
    if not data or len(data) == 0:
        return None
    scatter = Scatter(init_opts=opts.InitOpts(width="100%", height="400px"))
    x_data = [i+1 for i in range(len(data))]
    y_data = [freq for _, freq in data]
    scatter.add_xaxis(x_data)
    scatter.add_yaxis(
        series_name="词频", y_axis=y_data,
        symbol_size=[freq * 2 if bubble_size else 10 for _, freq in data],
        itemstyle_opts=opts.ItemStyleOpts(color=theme_colors[0] if theme_colors else "#1e88e5")
    )
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name="词汇索引"),
        yaxis_opts=opts.AxisOpts(name="词频"),
        legend_opts=opts.LegendOpts(is_show=True)
    )
    return scatter

def create_radar_chart(data, title="雷达图", theme_colors=None):
    if not data or len(data) == 0:
        return None
    data = data[:6]
    if len(data) == 0:
        return None
    radar = Radar(init_opts=opts.InitOpts(width="100%", height="400px"))
    max_freq = max(freq for _, freq in data) + 5
    schema = [opts.RadarIndicatorItem(name=word, max_=max_freq) for word, freq in data]
    radar.add_schema(schema=schema, shape="polygon", textstyle_opts=opts.TextStyleOpts(font_size=11))
    radar.add(
        series_name="词频", data=[[freq for _, freq in data]],
        areastyle_opts=opts.AreaStyleOpts(opacity=0.3, color=theme_colors[0] if theme_colors else "#1e88e5"),
        linestyle_opts=opts.LineStyleOpts(width=2, color=theme_colors[0] if theme_colors else "#1e88e5")
    )
    radar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c}"),
        legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="5%", textstyle_opts=opts.TextStyleOpts(font_size=11))
    )
    radar.set_series_opts(label_opts=opts.LabelOpts(font_size=9, is_show=True, formatter="{c}"))
    return radar

def create_heat_map(data, title="热力图", theme_colors=None):
    if not data or len(data) == 0:
        return None
    max_categories = 15
    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:max_categories]
    categories = [word for word, _ in sorted_data]
    if not categories:
        return None
    heatmap = HeatMap(init_opts=opts.InitOpts(width="100%", height="400px"))
    heat_data = [[i, 0, freq] for i, (word, freq) in enumerate(sorted_data)]
    heatmap.add_xaxis(xaxis_data=categories)
    heatmap.add_yaxis(series_name="词频", yaxis_data=["词频"], value=heat_data)
    max_freq = max(freq for _, freq in sorted_data)
    heatmap.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c}"),
        visualmap_opts=opts.VisualMapOpts(
            min_=0, max_=max_freq, orient="horizontal", pos_bottom="5%", pos_left="center",
            textstyle_opts=opts.TextStyleOpts(font_size=10), item_width=15, item_height=100, is_calculable=True
        ),
        xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(rotate=45, font_size=10, interval=0)),
        yaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(font_size=11))
    )
    heatmap.set_series_opts(label_opts=opts.LabelOpts(is_show=True, font_size=9, formatter="{c}", position="inside"))
    return heatmap

def display_analysis_results(analyzer, theme_colors, show_text=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 字数统计")
        char_stats = analyzer.count_characters()
        stats_df = pd.DataFrame({
            '项目': ['中文字符', '英文字符', '总字符数', '段落数'],
            '数值': [char_stats['chinese'], char_stats['english'], char_stats['total'], char_stats['paragraphs']]
        })
        st.dataframe(stats_df, use_container_width=True)
        
        st.subheader("⏱️ 阅读时长")
        reading_time = analyzer.estimate_reading_time()
        st.info(f"📖 预估阅读时间: **{reading_time['minutes']} 分钟**")
        st.info(f"📊 文本难度: **{reading_time['difficulty_label']}** (系数: {reading_time['difficulty']:.2f})")
        st.info(f"📝 总词数: **{reading_time['total_words']} 词**")
    
    with col2:
        st.subheader("💬 情感分析")
        sentiment = analyzer.analyze_sentiment()
        sentiment_color = "green" if sentiment['sentiment'] == '积极' else "red" if sentiment['sentiment'] == '消极' else "gray"
        st.markdown(f"**情感倾向:** <span style='color:{sentiment_color};font-size:24px'>{sentiment['sentiment']}</span>", unsafe_allow_html=True)
        st.progress((sentiment['score'] + 1) / 2)
        st.write(f"积极词汇: {sentiment['positive_count']} | 消极词汇: {sentiment['negative_count']}")
        
        st.subheader("🏷️ 主题分类")
        topic = analyzer.classify_topic()
        st.write(f"**主题标签:** {', '.join(topic['topics'])}")
        if topic['tags']:
            st.write("**关键词标签:**")
            st.markdown(' '.join([f"🏷️ {tag}" for tag in topic['tags']]))
    
    st.subheader("📊 主题分布")
    topic_scores = analyzer.classify_topic()['scores']
    if topic_scores:
        topic_df = pd.DataFrame(list(topic_scores.items()), columns=['主题', '匹配度'])
        topic_df['匹配度'] = topic_df['匹配度'] / max(topic_scores.values()) * 100
        st.dataframe(topic_df.sort_values('匹配度', ascending=False), use_container_width=True)
    
    if show_text:
        st.subheader("📄 原文预览")
        if st.checkbox("显示清理后的文本"):
            st.text_area("", analyzer.cleaned_text, height=200, key="text_preview")

def display_charts(analyzer, theme_colors, word_cloud_shape, show_values):
    chart_types = ["词云图", "柱状图", "饼图", "折线图", "散点图", "雷达图", "热力图"]
    recommended_charts = recommend_chart_type(analyzer.get_top_words(10))
    
    st.info(f"🎯 智能推荐图表类型: {', '.join(recommended_charts)}")
    selected_charts = st.multiselect("选择要显示的图表", chart_types, default=recommended_charts)
    
    top_n = st.slider("词频排名数量:", min_value=5, max_value=30, value=15, step=1)
    min_freq = st.slider("低频词过滤阈值:", min_value=1, max_value=10, value=2, step=1)
    sort_by = st.radio("排序方式:", ["frequency", "alphabetical"], format_func=lambda x: "按频率" if x == "frequency" else "按字母顺序", horizontal=True)
    ascending = st.checkbox("升序排列", value=False)
    
    filtered_word_freq = analyzer.filter_by_frequency(min_freq)
    top_words = analyzer.get_top_words(n=top_n, sort_by=sort_by, ascending=ascending)
    
    if top_words:
        df = pd.DataFrame(top_words, columns=["词汇", "频率"])
        st.dataframe(df, use_container_width=True)
        
        for chart_type in selected_charts:
            st.markdown(f"### {chart_type}")
            data = top_words[:10] if chart_type != "词云图" else analyzer.get_word_cloud_data(50)
            
            try:
                if chart_type == "词云图":
                    render_word_cloud(data, theme_colors, shape=word_cloud_shape)
                elif chart_type == "柱状图":
                    chart = create_bar_chart(data, title=f"{chart_type} - 词频排名", theme_colors=theme_colors, show_values=show_values)
                    if chart: safe_render_chart(chart, height=400)
                elif chart_type == "饼图":
                    chart = create_pie_chart(data, title=f"{chart_type} - 词频分布", theme_colors=theme_colors)
                    if chart: safe_render_chart(chart, height=400)
                elif chart_type == "折线图":
                    chart = create_line_chart(data, title=f"{chart_type} - 词频趋势", theme_colors=theme_colors)
                    if chart: safe_render_chart(chart, height=400)
                elif chart_type == "散点图":
                    chart = create_scatter_chart(data, title=f"{chart_type} - 词频分布", theme_colors=theme_colors)
                    if chart: safe_render_chart(chart, height=400)
                elif chart_type == "雷达图":
                    chart = create_radar_chart(data, title=f"{chart_type} - 词频对比", theme_colors=theme_colors)
                    if chart: safe_render_chart(chart, height=400)
                elif chart_type == "热力图":
                    chart = create_heat_map(data, title=f"{chart_type} - 词频热度", theme_colors=theme_colors)
                    if chart: safe_render_chart(chart, height=400)
            except Exception as e:
                st.error(f"❌ {chart_type}生成异常: {str(e)}")
    else:
        st.warning("⚠️ 没有足够的数据生成图表，请降低过滤阈值")

def main():
    st.set_page_config(page_title="文本分析与可视化", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
    
    if 'selected_words' not in st.session_state:
        st.session_state['selected_words'] = []
    if 'analysis_done' not in st.session_state:
        st.session_state['analysis_done'] = False
    if 'current_analyzer' not in st.session_state:
        st.session_state['current_analyzer'] = None
    if 'current_source_type' not in st.session_state:
        st.session_state['current_source_type'] = None
    if 'current_source_content' not in st.session_state:
        st.session_state['current_source_content'] = None
    if 'history_page' not in st.session_state:
        st.session_state['history_page'] = 1
    if 'selected_record_id' not in st.session_state:
        st.session_state['selected_record_id'] = None
    if 'comparison_list' not in st.session_state:
        st.session_state['comparison_list'] = []
    
    tabs = st.tabs(["📝 即时文本分析", "🔗 URL文本分析", "📜 历史记录", "📊 图表展示", "🔄 多文章对比"])
    
    with st.sidebar:
        st.title("📊 文本分析工具")
        st.markdown("---")
        
        st.subheader("🎨 图表样式")
        theme_name = st.selectbox("颜色主题", list(COLOR_THEMES.keys()), index=0)
        theme_colors = COLOR_THEMES[theme_name]
        word_cloud_shape = st.selectbox("词云形状", CHART_SHAPES, index=0)
        show_values = st.checkbox("显示数值标签", value=True)
        
        st.session_state['theme_colors'] = theme_colors
        st.session_state['word_cloud_shape'] = word_cloud_shape
        st.session_state['show_values'] = show_values
    
    with tabs[0]:
        st.title("📝 即时文本分析")
        st.markdown("直接在下方输入文本内容进行分析，无需从网页抓取")
        
        input_text = st.text_area(
            "请输入要分析的文本内容：",
            height=200,
            placeholder="在此输入文本内容..."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 立即分析", use_container_width=True, type="primary"):
                if not input_text.strip():
                    st.error("请输入要分析的文本内容")
                else:
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    try:
                        progress_text.text("🔄 正在初始化分析器...")
                        progress_bar.progress(10)
                        time.sleep(0.2)
                        
                        analyzer = TextAnalyzer()
                        
                        progress_text.text("📝 正在处理文本...")
                        progress_bar.progress(30)
                        time.sleep(0.2)
                        
                        analyzer.set_text(input_text)
                        
                        progress_text.text("🔍 正在分词和词频统计...")
                        progress_bar.progress(60)
                        time.sleep(0.3)
                        
                        analyzer.analyze_text(input_text)
                        
                        progress_text.text("📊 正在生成分析结果...")
                        progress_bar.progress(80)
                        time.sleep(0.2)
                        
                        st.session_state['current_analyzer'] = analyzer
                        st.session_state['current_source_type'] = '即时文本'
                        st.session_state['current_source_content'] = input_text[:200]
                        st.session_state['analysis_done'] = True
                        st.session_state['selected_record_id'] = None
                        
                        HistoryManager.add_record('即时文本', input_text, analyzer)
                        
                        progress_text.text("✅ 分析完成！")
                        progress_bar.progress(100)
                        time.sleep(0.3)
                        
                        st.success("✅ 文本分析完成！")
                        st.rerun()
                    except Exception as e:
                        progress_text.text(f"❌ 分析失败: {e}")
                        st.error(f"❌ 分析失败: {e}")
        
        st.markdown("---")
        
        if st.session_state.get('analysis_done') and st.session_state.get('current_source_type') == '即时文本':
            analyzer = st.session_state['current_analyzer']
            display_analysis_results(analyzer, st.session_state['theme_colors'], show_text=False)
        else:
            st.info("💡 请在上方输入文本内容并点击'立即分析'按钮开始分析")
    
    with tabs[1]:
        st.title("🔗 URL文本分析")
        
        url = st.text_input("请输入文章URL:", "https://www.lanqiao.cn/questions/1065710/", placeholder="https://example.com/article.html")
        
        if st.button("🚀 分析文本", use_container_width=True, type="primary"):
            if not url:
                st.error("请输入有效的URL")
            else:
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                try:
                    progress_text.text("🔄 正在连接服务器...")
                    progress_bar.progress(10)
                    time.sleep(0.3)
                    
                    analyzer = TextAnalyzer()
                    
                    progress_text.text("🌐 正在获取网页内容...")
                    progress_bar.progress(30)
                    time.sleep(0.5)
                    
                    html_content = analyzer.fetch_url_content(url)
                    
                    progress_text.text("🧹 正在清理HTML内容...")
                    progress_bar.progress(50)
                    time.sleep(0.3)
                    
                    text = analyzer.clean_text(html_content)
                    
                    progress_text.text("🔍 正在分词和词频统计...")
                    progress_bar.progress(70)
                    time.sleep(0.4)
                    
                    analyzer.analyze_text(text)
                    
                    progress_text.text("📊 正在生成分析结果...")
                    progress_bar.progress(90)
                    time.sleep(0.2)
                    
                    st.session_state['current_analyzer'] = analyzer
                    st.session_state['current_source_type'] = 'URL'
                    st.session_state['current_source_content'] = url
                    st.session_state['analysis_done'] = True
                    st.session_state['selected_record_id'] = None
                    
                    HistoryManager.add_record('URL', url, analyzer)
                    
                    progress_text.text("✅ 分析完成！")
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    
                    st.success("✅ 文本分析完成！")
                    st.rerun()
                except Exception as e:
                    progress_text.text(f"❌ 分析失败: {e}")
                    st.error(f"❌ 分析失败: {e}")
        
        st.markdown("---")
        
        if st.session_state.get('analysis_done') and st.session_state.get('current_source_type') == 'URL':
            analyzer = st.session_state['current_analyzer']
            display_analysis_results(analyzer, st.session_state['theme_colors'], show_text=True)
        else:
            st.info("💡 请在上方输入URL并点击'分析文本'按钮开始分析")
    
    with tabs[2]:
        st.title("📜 历史记录管理")
        
        page = st.session_state.get('history_page', 1)
        history_data = HistoryManager.get_history_page(page)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("⬅️ 上一页") and page > 1:
                st.session_state['history_page'] = page - 1
                st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>第 {page} / {history_data['total_pages']} 页 (共 {history_data['total_records']} 条记录)</h3>", unsafe_allow_html=True)
        with col3:
            if st.button("➡️ 下一页") and page < history_data['total_pages']:
                st.session_state['history_page'] = page + 1
                st.rerun()
        
        st.markdown("---")
        
        records = history_data['records']
        if records:
            for record in records:
                source_type = record.get('source_type', '未知')
                source_content = record.get('source_content', '')
                analysis_time = record.get('analysis_time', '')
                word_count = record.get('word_count', 0)
                top_words = record.get('top_words', [])
                record_id = record.get('id', 0)
                
                time_str = ""
                if analysis_time:
                    try:
                        time_str = datetime.fromisoformat(analysis_time).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        time_str = analysis_time
                
                source_label = "📝 即时文本" if source_type == '即时文本' else "🔗 URL"
                
                with st.expander(f"📋 记录 #{record_id} | {source_label} | {time_str}", expanded=False):
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.write(f"**来源类型:** {source_label}")
                        st.write(f"**来源内容:** {source_content[:100]}..." if len(source_content) > 100 else f"**来源内容:** {source_content}")
                        st.write(f"**分析时间:** {time_str}")
                        st.write(f"**词汇数量:** {word_count}")
                        if top_words:
                            st.write(f"**Top 5 关键词:** {', '.join([w[0] for w in top_words[:5]])}")
                    
                    with col2:
                        if st.button(f"📖 查看详情", key=f"view_{record_id}"):
                            st.session_state['selected_record_id'] = record_id
                            st.session_state['analysis_done'] = True
                            record_data = HistoryManager.get_record(record_id)
                            if record_data and 'data' in record_data:
                                analyzer = TextAnalyzer.from_dict(record_data['data'])
                                st.session_state['current_analyzer'] = analyzer
                                st.session_state['current_source_type'] = record_data.get('source_type', '历史记录')
                                st.session_state['current_source_content'] = record_data.get('source_content', '')
                            st.rerun()
                        
                        if st.button(f"➕ 添加到对比", key=f"compare_{record_id}"):
                            record_data = HistoryManager.get_record(record_id)
                            if record_data and 'data' in record_data:
                                analyzer = TextAnalyzer.from_dict(record_data['data'])
                                st.session_state['comparison_list'].append({
                                    'id': record_id,
                                    'source_content': record_data.get('source_content', ''),
                                    'analyzer': analyzer
                                })
                                st.success(f"✅ 已添加到对比列表！当前对比列表: {len(st.session_state['comparison_list'])} 篇")
            
            st.markdown("---")
            if st.button("🗑️ 清空全部历史", type="secondary"):
                HistoryManager.clear_history()
                st.session_state['history_page'] = 1
                st.success("✅ 历史记录已清空")
                st.rerun()
        else:
            st.info("📭 暂无历史记录")
    
    with tabs[3]:
        st.title("📊 图表展示")
        
        if st.session_state.get('analysis_done'):
            if st.session_state.get('selected_record_id'):
                record_id = st.session_state['selected_record_id']
                record_data = HistoryManager.get_record(record_id)
                if record_data and 'data' in record_data:
                    analyzer = TextAnalyzer.from_dict(record_data['data'])
                    st.session_state['current_analyzer'] = analyzer
            
            analyzer = st.session_state.get('current_analyzer')
            if analyzer:
                display_charts(analyzer, st.session_state['theme_colors'], st.session_state['word_cloud_shape'], st.session_state['show_values'])
            else:
                st.info("💡 请先进行文本分析")
        else:
            st.info("💡 请先在'即时文本分析'或'URL文本分析'标签页进行文本分析")
    
    with tabs[4]:
        st.title("🔄 多文章对比分析")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📋 对比列表")
            if st.session_state.get('comparison_list'):
                for i, item in enumerate(st.session_state['comparison_list']):
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(f"{i+1}. {item['source_content'][:30]}...")
                    if col_b.button("🗑️", key=f"remove_comp_{i}"):
                        st.session_state['comparison_list'].pop(i)
                        st.experimental_rerun()
            else:
                st.info("💡 暂无对比文章")
            
            if st.button("🗑️ 清空对比列表"):
                st.session_state['comparison_list'] = []
                st.experimental_rerun()
        
        with col2:
            st.subheader("📊 添加当前分析")
            if st.session_state.get('current_analyzer'):
                if st.button("➕ 添加当前结果到对比"):
                    exists = any(item['id'] == st.session_state.get('selected_record_id') for item in st.session_state['comparison_list'])
                    if not exists:
                        st.session_state['comparison_list'].append({
                            'id': st.session_state.get('selected_record_id', 0) or len(st.session_state['comparison_list']) + 100,
                            'source_content': st.session_state.get('current_source_content', '当前分析'),
                            'analyzer': st.session_state['current_analyzer']
                        })
                        st.success(f"✅ 已添加！当前对比列表: {len(st.session_state['comparison_list'])} 篇")
                    else:
                        st.warning("⚠️ 该文章已在对比列表中")
            else:
                st.info("💡 请先进行文本分析")
        
        st.markdown("---")
        
        comparison_list = st.session_state.get('comparison_list', [])
        if len(comparison_list) >= 2:
            st.subheader("🔍 对比分析结果")
            
            analyzers = [item['analyzer'] for item in comparison_list]
            result = compare_articles(analyzers)
            
            if result:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📊 关键词对比")
                    st.dataframe(result['comparison_df'], use_container_width=True)
                
                with col2:
                    st.subheader("📈 语义相似度")
                    similarity = result['similarity']
                    st.info(f"两篇文章的语义相似度: **{similarity * 100:.0f}%**")
                    
                    if similarity > 0.5:
                        st.success("✅ 两篇文章内容相似度较高")
                    elif similarity > 0.2:
                        st.warning("⚠️ 两篇文章内容有一定相似度")
                    else:
                        st.info("📌 两篇文章内容差异较大")
                
                st.subheader("🔗 共同关键词")
                if result['common_words']:
                    st.write("两篇文章的共同高频词:")
                    st.markdown(' '.join([f"**{word}**" for word in result['common_words']]))
                else:
                    st.info("没有找到共同关键词")
                
                st.subheader("📝 文章详情对比")
                col_a, col_b = st.columns([1, 1])
                
                with col_a:
                    st.write(f"**文章 1:** {comparison_list[0]['source_content'][:40]}...")
                    top_words = comparison_list[0]['analyzer'].get_top_words(5)
                    st.write(f"Top 5 关键词: {', '.join([w[0] for w in top_words])}")
                    sentiment = comparison_list[0]['analyzer'].analyze_sentiment()
                    st.write(f"情感倾向: {sentiment['sentiment']} (评分: {sentiment['score']})")
                
                with col_b:
                    st.write(f"**文章 2:** {comparison_list[1]['source_content'][:40]}...")
                    top_words = comparison_list[1]['analyzer'].get_top_words(5)
                    st.write(f"Top 5 关键词: {', '.join([w[0] for w in top_words])}")
                    sentiment = comparison_list[1]['analyzer'].analyze_sentiment()
                    st.write(f"情感倾向: {sentiment['sentiment']} (评分: {sentiment['score']})")
                
                st.subheader("📊 词频对比图表")
                theme_colors = st.session_state['theme_colors']
                
                if result['top_words_1'] and result['top_words_2']:
                    top_words_1 = result['top_words_1'][:5]
                    top_words_2 = result['top_words_2'][:5]
                    
                    all_words = set([w[0] for w in top_words_1] + [w[0] for w in top_words_2])
                    compare_data = []
                    for word in all_words:
                        freq1 = dict(top_words_1).get(word, 0)
                        freq2 = dict(top_words_2).get(word, 0)
                        compare_data.append((word, freq1, freq2))
                    
                    compare_df = pd.DataFrame(compare_data, columns=['词汇', '文章1词频', '文章2词频'])
                    st.dataframe(compare_df, use_container_width=True)
                    
                    bar_compare = Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
                    bar_compare.add_xaxis([item[0] for item in compare_data])
                    bar_compare.add_yaxis("文章1", [item[1] for item in compare_data], itemstyle_opts=opts.ItemStyleOpts(color=theme_colors[0]))
                    bar_compare.add_yaxis("文章2", [item[2] for item in compare_data], itemstyle_opts=opts.ItemStyleOpts(color=theme_colors[2]))
                    bar_compare.set_global_opts(
                        title_opts=opts.TitleOpts(title="词频对比柱状图", title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
                        tooltip_opts=opts.TooltipOpts(is_show=True),
                        xaxis_opts=opts.AxisOpts(name="词汇", axislabel_opts=opts.LabelOpts(rotate=45)),
                        yaxis_opts=opts.AxisOpts(name="词频"),
                        legend_opts=opts.LegendOpts(is_show=True)
                    )
                    safe_render_chart(bar_compare, height=400)
        else:
            st.info(f"💡 请添加至少两篇文章到对比列表（当前: {len(comparison_list)} 篇）")

if __name__ == "__main__":
    jieba.initialize()
    main()