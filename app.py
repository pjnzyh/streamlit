#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分析与可视化应用

功能：
1. 从URL获取文本内容
2. 文本清洗与处理
3. 中文分词与词频统计
4. 多种数据可视化图表
5. 交互式用户界面
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
import pandas as pd
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Radar, HeatMap
from pyecharts import options as opts
from streamlit.components.v1 import html

# 常见停用词列表
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
    '山边', '路边', '窗边', '门边', '河边', '湖边', '海边', '山边', '路边', '窗边', '门边', '上', '下', '左',
    '右', '前', '后', '里', '外', '内', '外', '东', '西', '南', '北', '中', '间', '边', '角', '面', '点', '线',
    '片', '块', '个', '只', '条', '本', '张', '件', '双', '对', '群', '堆', '批', '伙', '帮', '班', '队', '组',
    '排', '列', '行', '列', '阵', '营', '军', '师', '旅', '团', '营', '连', '排', '班', '组', '人', '员', '工',
    '农', '兵', '商', '学', '兵', '党', '团', '队', '组织', '团体', '机构', '部门', '单位', '公司', '企业',
    '工厂', '商店', '学校', '医院', '银行', '邮局', '车站', '机场', '码头', '港口', '道路', '桥梁', '建筑',
    '房屋', '公寓', '别墅', '酒店', '餐厅', '商店', '超市', '市场', '商场', '广场', '公园', '花园', '森林',
    '草原', '沙漠', '海洋', '河流', '湖泊', '山脉', '山峰', '平原', '高原', '盆地', '丘陵', '岛屿', '半岛',
    '海峡', '海湾', '海港', '海滩', '沙滩', '海岸', '河岸', '湖边', '河边', '海边', '山边', '路边', '窗边',
    '门边', '河边', '湖边', '海边', '山边', '路边', '窗边', '门边', '上', '下', '左', '右', '前', '后', '里',
    '外', '内', '外', '东', '西', '南', '北', '中', '间', '边', '角', '面', '点', '线', '片', '块', '个', '只',
    '条', '本', '张', '件', '双', '对', '群', '堆', '批', '伙', '帮', '班', '队', '组', '排', '列', '行', '列',
    '阵', '营', '军', '师', '旅', '团', '营', '连', '排', '班', '组'
])

class TextAnalyzer:
    """文本分析类"""
    
    def __init__(self):
        self.text = ""
        self.word_freq = Counter()
        self.cleaned_text = ""
    
    def fetch_url_content(self, url):
        """获取URL内容"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
    
    def clean_text(self, html_content):
        """清洗HTML内容"""
        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 获取纯文本
        text = soup.get_text()
        
        # 清理空白字符
        text = ' '.join(text.split())
        
        # 保存清理后的文本
        self.cleaned_text = text
        return text
    
    def analyze_text(self, text, min_length=2):
        """分析文本，计算词频"""
        # 中文分词
        words = jieba.cut(text)
        
        # 过滤停用词和短词
        filtered_words = [
            word for word in words 
            if len(word) >= min_length and word not in STOP_WORDS
        ]
        
        # 统计词频
        self.word_freq = Counter(filtered_words)
        return self.word_freq
    
    def get_top_words(self, n=20, sort_by='frequency', ascending=False):
        """获取词频排名前n的词汇"""
        if sort_by == 'frequency':
            # 按频率排序
            top_words = self.word_freq.most_common(n)
            if ascending:
                top_words = reversed(top_words)
        else:
            # 按字母顺序排序
            sorted_words = sorted(self.word_freq.items(), key=lambda x: x[0], reverse=not ascending)
            top_words = sorted_words[:n]
        
        return list(top_words)
    
    def filter_by_frequency(self, min_freq):
        """过滤低频词"""
        filtered = {word: freq for word, freq in self.word_freq.items() if freq >= min_freq}
        return Counter(filtered)
    
    def get_word_cloud_data(self, max_words=100):
        """获取词云数据"""
        return self.word_freq.most_common(max_words)

def create_word_cloud(data):
    """创建词云图"""
    wordcloud = WordCloud()
    
    wordcloud.add(
        series_name="词频",
        data_pair=data,
        word_size_range=[15, 80],
        shape="circle"
    )
    
    wordcloud.set_global_opts(
        title_opts=opts.TitleOpts(title="词云图", title_textstyle_opts=opts.TextStyleOpts(font_size=25)),
        tooltip_opts=opts.TooltipOpts(is_show=True)
    )
    return wordcloud

def create_bar_chart(data, title="柱状图"):
    """创建柱状图"""
    bar = Bar()
    
    words, freqs = zip(*data)
    bar.add_xaxis(list(words))
    bar.add_yaxis(series_name="词频", y_axis=list(freqs))
    
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=25)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name="词汇", axislabel_opts=opts.LabelOpts(rotate=45)),
        yaxis_opts=opts.AxisOpts(name="词频"),
    )
    return bar

def create_pie_chart(data, title="饼图"):
    """创建饼图"""
    pie = Pie()
    
    pie.add(series_name="词频", data_pair=data, radius=["35%", "75%"])
    
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c} ({d}%)"),
        legend_opts=opts.LegendOpts(
            orient="horizontal", 
            pos_bottom="5%", 
            textstyle_opts=opts.TextStyleOpts(font_size=12),
            type_="scroll",  # 启用滚动图例
            page_button_position="end"
        ),
    )
    
    # 设置系列选项，优化饼图标签
    pie.set_series_opts(
        label_opts=opts.LabelOpts(
            font_size=10,  # 减小标签字体大小
            formatter="{b}: {d}%",  # 只显示名称和百分比
            position="outside",  # 标签显示在外部
            distance=15,  # 调整标签与饼图的距离
            overflow="truncate"  # 长文本截断
        )
    )
    return pie

def create_line_chart(data, title="折线图"):
    """创建折线图"""
    line = Line()
    
    words, freqs = zip(*data)
    line.add_xaxis(list(words))
    line.add_yaxis(series_name="词频", y_axis=list(freqs), is_smooth=True)
    
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=25)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name="词汇", axislabel_opts=opts.LabelOpts(rotate=45)),
        yaxis_opts=opts.AxisOpts(name="词频"),
    )
    return line

def create_scatter_chart(data, title="散点图"):
    """创建散点图"""
    scatter = Scatter()
    
    # 准备散点图数据
    scatter_data = [[i+1, freq] for i, (_, freq) in enumerate(data)]
    scatter.add_xaxis([i+1 for i in range(len(data))])
    scatter.add_yaxis(series_name="词频", y_axis=[freq for _, freq in data])
    
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=25)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name="词汇索引"),
        yaxis_opts=opts.AxisOpts(name="词频"),
    )
    return scatter

def create_radar_chart(data, title="雷达图"):
    """创建雷达图"""
    # 雷达图只适合较少的数据，最多6个维度，避免文字重叠
    data = data[:6]
    
    radar = Radar()
    
    # 配置雷达图维度，优化标签显示
    schema = [opts.RadarIndicatorItem(name=word, max_=max(freq for _, freq in data) + 5) for word, freq in data]
    radar.add_schema(
        schema=schema,
        shape="polygon",  # 使用多边形雷达图
        textstyle_opts=opts.TextStyleOpts(font_size=12)  # 减小指标名称字体
    )
    
    # 添加数据
    radar.add(
        series_name="词频", 
        data=[[freq for _, freq in data]], 
        areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        linestyle_opts=opts.LineStyleOpts(width=2)  # 线条宽度
    )
    
    # 设置全局选项
    radar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c}"),
        legend_opts=opts.LegendOpts(
            orient="horizontal",
            pos_bottom="5%",
            textstyle_opts=opts.TextStyleOpts(font_size=12)
        )
    )
    
    # 设置系列选项
    radar.set_series_opts(
        label_opts=opts.LabelOpts(
            font_size=10,  # 减小数据标签字体
            is_show=True,  # 显示数据标签
            formatter="{c}"  # 只显示数值
        )
    )
    return radar

def create_heat_map(data, title="热力图"):
    """创建热力图"""
    # 限制热力图显示的类别数量，避免x轴标签过多导致重叠
    max_categories = 15
    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:max_categories]
    
    categories = [word for word, _ in sorted_data]
    categories.sort()
    
    # 获取所有频率值
    freqs = [freq for _, freq in sorted_data]
    max_freq = max(freqs) if freqs else 1
    
    # 创建HeatMap实例
    heatmap = HeatMap()
    
    # 准备x轴和y轴数据
    x_axis = categories
    y_axis = ["词频"]
    
    # 准备热力图数据格式: [[x_index, y_index, value], ...]
    heat_data = []
    for i, category in enumerate(x_axis):
        # 查找对应类别的频率
        freq = next((freq for word, freq in sorted_data if word == category), 0)
        heat_data.append([i, 0, freq])
    
    # 设置x轴和y轴
    heatmap.add_xaxis(xaxis_data=x_axis)
    heatmap.add_yaxis(
        series_name="词频",
        yaxis_data=y_axis,
        value=heat_data
    )
    
    # 设置全局选项，优化文字显示
    heatmap.set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=22)),
        tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c}"),
        visualmap_opts=opts.VisualMapOpts(
            min_=0, 
            max_=max_freq,
            orient="horizontal",  # 水平放置
            pos_bottom="5%",  # 调整到底部更下方位置，避免遮挡
            pos_left="center",  # 居中放置，不再影响左下角
            textstyle_opts=opts.TextStyleOpts(font_size=10),
            item_width=15,  # 调整图例项宽度
            item_height=100,  # 调整图例项高度
            range_opacity=[0.3, 1.0],  # 设置透明度范围
            is_calculable=True,  # 启用拖拽计算功能
            border_color="#ccc",  # 边框颜色
            border_width=1  # 边框宽度
        ),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            axislabel_opts=opts.LabelOpts(
                rotate=45,  # 旋转45度
                font_size=10,  # 减小字体大小
                interval=0,  # 显示所有标签
                overflow="truncate"  # 长文本截断
            )
        ),
        yaxis_opts=opts.AxisOpts(
            type_="category",
            axislabel_opts=opts.LabelOpts(font_size=12)
        )
    )
    
    # 设置系列选项
    heatmap.set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=True,
            font_size=9,  # 减小热力图内部数值字体
            formatter="{c}",  # 只显示数值
            position="inside"  # 确保数值显示在热力图内部
        )
    )
    return heatmap

def create_chart(data, chart_type, title=""):
    """根据类型创建不同的图表"""
    if chart_type == "词云图":
        return create_word_cloud(data)
    elif chart_type == "柱状图":
        return create_bar_chart(data, title=title)
    elif chart_type == "饼图":
        return create_pie_chart(data, title=title)
    elif chart_type == "折线图":
        return create_line_chart(data, title=title)
    elif chart_type == "散点图":
        return create_scatter_chart(data, title=title)
    elif chart_type == "雷达图":
        return create_radar_chart(data, title=title)
    elif chart_type == "热力图":
        return create_heat_map(data, title=title)
    else:
        raise ValueError(f"不支持的图表类型: {chart_type}")

def main():
    """主函数"""
    # 设置页面标题
    st.title("文本分析与可视化应用")
    
    # 创建侧边栏
    st.sidebar.title("设置")
    
    # URL输入
    url = st.text_input("请输入文章URL:", "https://www.lanqiao.cn/questions/1065710/")
    
    # 提交按钮
    if st.button("分析文本"):
        if not url:
            st.error("请输入有效的URL")
            return
        
        # 显示加载状态
        with st.spinner("正在获取并分析文本..."):
            try:
                # 创建文本分析器
                analyzer = TextAnalyzer()
                
                # 获取URL内容
                html_content = analyzer.fetch_url_content(url)
                
                # 清理文本
                text = analyzer.clean_text(html_content)
                
                # 分析文本
                analyzer.analyze_text(text)
                
                # 保存分析器和当前URL到会话状态
                st.session_state['analyzer'] = analyzer
                st.session_state['analysis_done'] = True
                st.session_state['current_url'] = url  # 保存当前URL
                
                st.success("文本分析完成！")
                
            except Exception as e:
                st.error(f"分析失败: {e}")
                return
    
    # 检查当前URL是否与上次分析的URL一致
    if st.session_state.get('analysis_done') and st.session_state.get('current_url') != url:
        # 如果URL已更改，清除之前的分析结果
        st.session_state['analysis_done'] = False
    
    # 如果分析完成，显示结果
    if st.session_state.get('analysis_done'):
        analyzer = st.session_state['analyzer']
        # 显示当前分析的URL
        st.sidebar.info(f"当前分析URL: {st.session_state.get('current_url')}")
        
        # 侧边栏设置
        st.sidebar.subheader("图表设置")
        
        # 图表类型选择
        chart_type = st.sidebar.selectbox(
            "选择图表类型:",
            ["词云图", "柱状图", "饼图", "折线图", "散点图", "雷达图", "热力图"]
        )
        
        # 低频词过滤
        min_freq = st.sidebar.slider(
            "低频词过滤阈值:",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )
        
        # 词频排名数量
        top_n = st.sidebar.slider(
            "词频排名数量:",
            min_value=10,
            max_value=50,
            value=20,
            step=5
        )
        
        # 排序方式
        sort_by = st.sidebar.radio(
            "排序方式:",
            ["frequency", "alphabetical"],
            format_func=lambda x: "按频率" if x == "frequency" else "按字母顺序"
        )
        
        # 排序顺序
        ascending = st.sidebar.checkbox("升序排列", value=False)
        
        # 过滤低频词
        filtered_word_freq = analyzer.filter_by_frequency(min_freq)
        st.sidebar.write(f"过滤后剩余词汇: {len(filtered_word_freq)} 个")
        
        # 获取排序后的前n个词汇
        top_words = analyzer.get_top_words(n=top_n, sort_by=sort_by, ascending=ascending)
        
        # 显示词频排名
        st.subheader(f"词频排名前{top_n}的词汇")
        
        # 创建DataFrame显示词频排名
        df = pd.DataFrame(top_words, columns=["词汇", "频率"])
        st.dataframe(df, use_container_width=True)
        
        # 生成图表
        st.subheader("可视化图表")
        
        # 根据选择的图表类型生成图表
        chart = create_chart(top_words[:10], chart_type, title=f"{chart_type} - 词频排名前10")
        
        # 渲染图表
        chart_html = chart.render_embed()
        html(chart_html, height=600)
        
        # 显示清理后的文本（可选）
        if st.checkbox("显示清理后的文本"):
            st.subheader("清理后的文本")
            st.text_area("", analyzer.cleaned_text, height=200)

if __name__ == "__main__":
    # 初始化jieba
    jieba.initialize()
    
    # 运行主函数
    main()
