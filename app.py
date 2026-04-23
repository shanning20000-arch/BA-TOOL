"""
车企经销商智能杜邦分析系统 - Web版本
使用 Streamlit 构建
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 页面配置
st.set_page_config(
    page_title="车企经销商杜邦分析系统",
    page_icon="🚗",
    layout="wide"
)

# 业务数据配置
BUSINESS_DATA = {
    '现金牛产品': {
        'desc': '常规保养/维修服务',
        'base_margin': 0.12,
        'margin_range': (0.08, 0.20),
        'base_turnover': 3.5,
        'turnover_range': (2.5, 4.5),
        'base_leverage': 1.8,
        'leverage_range': (1.2, 2.5),
        'base_share': 0.40,
        'share_range': (0.30, 0.50),
        'adjust_factor': 0.3
    },
    '明星产品': {
        'desc': '新能源车销售',
        'base_margin': 0.08,
        'margin_range': (0.05, 0.15),
        'base_turnover': 2.8,
        'turnover_range': (2.0, 3.5),
        'base_leverage': 2.0,
        'leverage_range': (1.5, 2.8),
        'base_share': 0.25,
        'share_range': (0.15, 0.35),
        'adjust_factor': 0.8
    },
    '问题产品': {
        'desc': '二手车业务',
        'base_margin': 0.05,
        'margin_range': (0.02, 0.10),
        'base_turnover': 1.5,
        'turnover_range': (1.0, 2.0),
        'base_leverage': 2.2,
        'leverage_range': (1.8, 3.0),
        'base_share': 0.20,
        'share_range': (0.10, 0.30),
        'adjust_factor': 1.2
    },
    '瘦狗产品': {
        'desc': '低毛利配件',
        'base_margin': 0.03,
        'margin_range': (0.01, 0.08),
        'base_turnover': 1.0,
        'turnover_range': (0.5, 1.5),
        'base_leverage': 2.5,
        'leverage_range': (2.0, 3.5),
        'base_share': 0.15,
        'share_range': (0.05, 0.25),
        'adjust_factor': 2.0
    }
}

PRODUCT_ORDER = ['现金牛产品', '明星产品', '问题产品', '瘦狗产品']
COLORS = ['#FFD700', '#FF6B6B', '#4ECDC4', '#95E1D3']

def init_session_state():
    """初始化会话状态"""
    if 'current_params' not in st.session_state:
        st.session_state.current_params = {}
        for product_name, data in BUSINESS_DATA.items():
            st.session_state.current_params[product_name] = {
                'revenue_share': data['base_share'],
                'margin': data['base_margin'],
                'turnover': data['base_turnover'],
                'leverage': data['base_leverage']
            }
    
    if 'total_revenue' not in st.session_state:
        st.session_state.total_revenue = 1000.0
    
    if 'target_margin' not in st.session_state:
        st.session_state.target_margin = 7.5

def calculate_indicators():
    """计算杜邦分析指标"""
    indicators = {}
    total_profit = 0
    total_assets = 0
    total_equity = 0
    
    for product_name, params in st.session_state.current_params.items():
        revenue = st.session_state.total_revenue * params['revenue_share']
        profit = revenue * params['margin']
        assets = revenue / params['turnover'] if params['turnover'] > 0 else 0
        equity = assets / params['leverage'] if params['leverage'] > 0 else 0
        roe = (profit / equity * 100) if equity > 0 else 0
        
        indicators[product_name] = {
            'revenue': revenue,
            'profit': profit,
            'assets': assets,
            'equity': equity,
            'roe': roe
        }
        
        total_profit += profit
        total_assets += assets
        total_equity += equity
    
    overall_margin = (total_profit / st.session_state.total_revenue * 100) if st.session_state.total_revenue > 0 else 0
    overall_turnover = (st.session_state.total_revenue / total_assets) if total_assets > 0 else 0
    overall_leverage = (total_assets / total_equity) if total_equity > 0 else 0
    overall_roe = (total_profit / total_equity * 100) if total_equity > 0 else 0
    
    indicators['整体'] = {
        'margin': overall_margin,
        'turnover': overall_turnover,
        'leverage': overall_leverage,
        'roe': overall_roe
    }
    
    return indicators

def smart_optimize():
    """智能优化算法"""
    current_margin = calculate_indicators()['整体']['margin']
    gap = st.session_state.target_margin - current_margin
    
    if abs(gap) < 0.1:
        return "当前参数已接近目标，无需调整"
    
    gap_pct = gap / 100
    
    # 计算调整权重
    adjustment_weights = {}
    total_weight = 0
    
    for product_name, data in BUSINESS_DATA.items():
        params = st.session_state.current_params[product_name]
        weight = params['revenue_share'] * data['adjust_factor']
        adjustment_weights[product_name] = weight
        total_weight += weight
    
    if total_weight == 0:
        return "优化失败"
    
    # 归一化权重
    for product_name in adjustment_weights:
        adjustment_weights[product_name] /= total_weight
    
    # 执行优化
    for product_name, weight in adjustment_weights.items():
        data = BUSINESS_DATA[product_name]
        params = st.session_state.current_params[product_name]
        
        adjustment = gap_pct * weight * 2.0
        
        # 调整净利率
        new_margin = params['margin'] + adjustment
        new_margin = max(data['margin_range'][0], min(data['margin_range'][1], new_margin))
        
        # 调整周转率
        margin_room = new_margin - params['margin']
        if abs(margin_room) < abs(adjustment) * 0.5:
            turnover_adjust = adjustment * 0.5
            new_turnover = params['turnover'] + turnover_adjust
            new_turnover = max(data['turnover_range'][0], min(data['turnover_range'][1], new_turnover))
            params['turnover'] = new_turnover
        
        # 调整收入结构
        remaining_gap = gap_pct - (new_margin - params['margin'])
        if abs(remaining_gap) > 0.001:
            share_adjust = remaining_gap * data['adjust_factor'] * 0.3
            new_share = params['revenue_share'] + share_adjust
            new_share = max(data['share_range'][0], min(data['share_range'][1], new_share))
            params['revenue_share'] = new_share
        
        params['margin'] = new_margin
    
    new_margin = calculate_indicators()['整体']['margin']
    if abs(new_margin - st.session_state.target_margin) < 0.5:
        return f"优化成功！净利率：{new_margin:.1f}% (目标：{st.session_state.target_margin}%)"
    else:
        return f"部分优化！净利率：{new_margin:.1f}% (目标：{st.session_state.target_margin}%)"

def reset_all():
    """重置所有数据"""
    for product_name, data in BUSINESS_DATA.items():
        st.session_state.current_params[product_name] = {
            'revenue_share': data['base_share'],
            'margin': data['base_margin'],
            'turnover': data['base_turnover'],
            'leverage': data['base_leverage']
        }
    st.session_state.total_revenue = 1000.0
    st.session_state.target_margin = 7.5
    return "已重置为初始状态"

def generate_advice(indicators):
    """生成智能经营建议"""
    overall = indicators['整体']
    margin_gap = overall['margin'] - st.session_state.target_margin
    
    advice = []
    
    # 目标差距分析
    if abs(margin_gap) < 0.5:
        advice.append(f"净利率已接近目标，差距：{margin_gap:.1f}个百分点")
    elif margin_gap > 0:
        advice.append(f"净利率已超过目标，超出：{margin_gap:.1f}个百分点")
    else:
        advice.append(f"净利率低于目标，差距：{-margin_gap:.1f}个百分点")
    
    # ROE水平评估
    if overall['roe'] >= 20:
        advice.append("ROE优秀（≥20%），处于行业领先水平")
    elif overall['roe'] >= 15:
        advice.append("ROE良好（15-20%），超过行业平均水平")
    elif overall['roe'] >= 10:
        advice.append("ROE一般（10-15%），接近行业平均")
    else:
        advice.append("ROE偏低（<10%），亟需提升")
    
    return advice

# 主应用
def main():
    init_session_state()
    
    # 标题
    st.title("🚗 车企经销商智能杜邦分析系统")
    st.markdown("---")
    
    # 顶部：目标设置
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        st.session_state.total_revenue = st.number_input(
            "总收入（万元）",
            min_value=100,
            max_value=100000,
            value=int(st.session_state.total_revenue),
            step=100
        )
    
    with col2:
        st.session_state.target_margin = st.number_input(
            "目标净利率（%）",
            min_value=1.0,
            max_value=30.0,
            value=st.session_state.target_margin,
            step=0.5
        )
    
    with col3:
        if st.button("🚀 智能优化", type="primary", use_container_width=True):
            result = smart_optimize()
            st.success(result)
    
    with col4:
        if st.button("🔄 重置", use_container_width=True):
            result = reset_all()
            st.info(result)
    
    st.markdown("---")
    
    # 左侧：参数控制
    with st.expander("📊 产品参数控制（点击展开）", expanded=True):
        for i, product_name in enumerate(PRODUCT_ORDER):
            data = BUSINESS_DATA[product_name]
            params = st.session_state.current_params[product_name]
            
            with st.container():
                st.markdown(f"**{product_name}** - {data['desc']}")
                
                cols = st.columns(4)
                with cols[0]:
                    new_share = st.slider(
                        "收入占比（%）",
                        min_value=int(data['share_range'][0] * 100),
                        max_value=int(data['share_range'][1] * 100),
                        value=int(params['revenue_share'] * 100),
                        key=f"share_{product_name}"
                    )
                    st.session_state.current_params[product_name]['revenue_share'] = new_share / 100
                
                with cols[1]:
                    new_margin = st.slider(
                        "净利率（%）",
                        min_value=int(data['margin_range'][0] * 100),
                        max_value=int(data['margin_range'][1] * 100),
                        value=int(params['margin'] * 100),
                        key=f"margin_{product_name}"
                    )
                    st.session_state.current_params[product_name]['margin'] = new_margin / 100
                
                with cols[2]:
                    new_turnover = st.slider(
                        "资产周转率",
                        min_value=int(data['turnover_range'][0] * 10),
                        max_value=int(data['turnover_range'][1] * 10),
                        value=int(params['turnover'] * 10),
                        key=f"turnover_{product_name}"
                    )
                    st.session_state.current_params[product_name]['turnover'] = new_turnover / 10
                
                with cols[3]:
                    new_leverage = st.slider(
                        "权益乘数",
                        min_value=int(data['leverage_range'][0] * 10),
                        max_value=int(data['leverage_range'][1] * 10),
                        value=int(params['leverage'] * 10),
                        key=f"leverage_{product_name}"
                    )
                    st.session_state.current_params[product_name]['leverage'] = new_leverage / 10
                
                st.markdown("---")
    
    # 计算指标
    indicators = calculate_indicators()
    overall = indicators['整体']
    
    # 顶部：关键指标展示
    st.subheader("📈 关键指标")
    
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("当前净利率", f"{overall['margin']:.2f}%", 
                 f"{overall['margin'] - st.session_state.target_margin:.2f}%")
    with metric_cols[1]:
        st.metric("当前ROE", f"{overall['roe']:.2f}%")
    with metric_cols[2]:
        st.metric("资产周转率", f"{overall['turnover']:.2f}")
    with metric_cols[3]:
        st.metric("权益乘数", f"{overall['leverage']:.2f}")
    
    st.markdown("---")
    
    # 左侧：经营建议
    advice = generate_advice(indicators)
    st.subheader("💡 智能经营建议")
    
    for item in advice:
        if "超过" in item or "接近" in item or "良好" in item or "优秀" in item:
            st.success(f"✅ {item}")
        elif "偏低" in item or "低于" in item or "一般" in item:
            st.warning(f"⚠️ {item}")
        else:
            st.info(f"ℹ️ {item}")
    
    # 右侧：业务线ROE排名
    st.subheader("🏆 业务线ROE排名")
    roe_data = []
    for product_name in PRODUCT_ORDER:
        if product_name in indicators:
            roe = indicators[product_name]['roe']
            share = st.session_state.current_params[product_name]['revenue_share'] * 100
            roe_data.append({
                '产品': product_name,
                'ROE（%）': round(roe, 2),
                '收入占比（%）': round(share, 1)
            })
    
    roe_df = pd.DataFrame(roe_data)
    roe_df = roe_df.sort_values('ROE（%）', ascending=False)
    roe_df.index = ['🥇', '🥈', '🥉', '📉']
    st.dataframe(roe_df, use_container_width=True)
    
    st.markdown("---")
    
    # 可视化区域
    st.subheader("📊 可视化分析")
    
    # 图表1 & 2
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 收入结构饼图
        pie_data = []
        for product_name in PRODUCT_ORDER:
            share = st.session_state.current_params[product_name]['revenue_share'] * 100
            pie_data.append({'产品': product_name, '收入占比': share})
        
        fig = px.pie(pie_data, values='收入占比', names='产品', 
                     title='收入结构分布', color_discrete_sequence=COLORS)
        fig.update_layout(template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # 利润贡献柱状图
        profit_data = []
        for product_name in PRODUCT_ORDER:
            if product_name in indicators:
                profit_data.append({
                    '产品': product_name,
                    '利润（万元）': round(indicators[product_name]['profit'], 2)
                })
        
        fig = px.bar(profit_data, x='产品', y='利润（万元）', 
                     title='利润贡献（万元）', color='产品', color_discrete_sequence=COLORS)
        fig.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # 图表3 & 4
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # ROE对比图
        roe_chart_data = []
        for product_name in PRODUCT_ORDER:
            if product_name in indicators:
                roe_chart_data.append({
                    '产品': product_name,
                    'ROE（%）': round(indicators[product_name]['roe'], 2)
                })
        roe_chart_data.append({
            '产品': '整体',
            'ROE（%）': round(overall['roe'], 2)
        })
        
        fig = px.bar(roe_chart_data, x='产品', y='ROE（%）', 
                     title='ROE对比（%）', color='产品', 
                     color_discrete_sequence=COLORS + ['#2E8B57'])
        fig.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col4:
        # 杜邦分析图
        dupont_data = pd.DataFrame({
            '因素': ['净利率', '周转率', '杠杆'],
            '数值': [f"{overall['margin']:.1f}%", f"{overall['turnover']:.2f}", f"{overall['leverage']:.2f}"],
            '颜色': COLORS[:3]
        })
        
        fig = go.Figure()
        
        # 添加杜邦公式展示
        fig.add_trace(go.Indicator(
            mode="number",
            value=overall['roe'],
            title={"text": "ROE = 净利率 × 周转率 × 杠杆"},
            number={"suffix": "%"},
            domain={'x': [0, 1], 'y': [0.6, 1]}
        ))
        
        # 添加三因素展示
        for i, (factor, value, color) in enumerate(zip(
            ['净利率', '周转率', '杠杆'],
            [f"{overall['margin']:.1f}%", f"{overall['turnover']:.2f}", f"{overall['leverage']:.2f}"],
            COLORS[:3]
        )):
            fig.add_trace(go.Indicator(
                mode="number",
                value=1,
                number={"suffix": ""},
                title={"text": f"{factor}<br><span style='font-size:20px'>{value}</span>"},
                domain={'x': [i/3, (i+1)/3], 'y': [0, 0.5]},
            ))
        
        fig.update_layout(
            title={'text': '🔬 杜邦分析三因素', 'x': 0.5},
            template='plotly_white',
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 详细数据表
    st.markdown("---")
    st.subheader("📋 详细数据")
    
    detail_data = []
    for product_name in PRODUCT_ORDER:
        params = st.session_state.current_params[product_name]
        ind = indicators[product_name]
        detail_data.append({
            '产品': product_name,
            '收入占比': f"{params['revenue_share']*100:.1f}%",
            '净利率': f"{params['margin']*100:.1f}%",
            '周转率': f"{params['turnover']:.2f}",
            '杠杆': f"{params['leverage']:.2f}",
            '收入': f"{ind['revenue']:.1f}万",
            '利润': f"{ind['profit']:.1f}万",
            'ROE': f"{ind['roe']:.1f}%"
        })
    
    detail_df = pd.DataFrame(detail_data)
    st.dataframe(detail_df, use_container_width=True)
    
    # 页脚
    st.markdown("---")
    st.caption("车企经销商智能杜邦分析系统 v2.0 | Powered by Streamlit")

if __name__ == "__main__":
    main()
