from tool import get_completion,get_completion_from_messages
import panel as pn
import json
import html

# -------------------------------
# 1. 初始化 context（系统设定）
# -------------------------------
context = [{'role': 'system', 'content': """
你是订餐机器人，为披萨餐厅自动收集订单信息。
你要首先问候顾客。然后等待用户回复收集订单信息。收集完信息需确认顾客是否还需要添加其他内容。
最后需要询问是否自取或外送，如果是外送，你要询问地址。
最后告诉顾客订单总金额，并送上祝福。

请确保明确所有选项、附加项和尺寸，以便从菜单中识别出该项唯一的内容。
你的回应应该以简短、非常随意和友好的风格呈现。

菜单包括：

菜品：
意式辣香肠披萨（大、中、小） 12.95、10.00、7.00
芝士披萨（大、中、小） 10.95、9.25、6.50
茄子披萨（大、中、小） 11.95、9.75、6.75
薯条（大、小） 4.50、3.50
希腊沙拉 7.25

配料：
奶酪 2.00
蘑菇 1.50
香肠 3.00
加拿大熏肉 3.50
AI酱 1.50
辣椒 1.00

饮料：
可乐（大、中、小） 3.00、2.00、1.00
雪碧（大、中、小） 3.00、2.0.0、1.00
瓶装水 5.00
"""}]

# -------------------------------
# 2. 设置 UI 面板
# -------------------------------
inp = pn.widgets.TextInput(
    placeholder='请输入您的订单...', 
    width=650,
    styles={
        'font-size': '15px',
        'border': '2px solid #FF6B35',
        'border-radius': '25px',
        'padding': '12px 20px'
    }
)
conversation_panel = pn.Column(
    height=450, 
    scroll=True,
    styles={
        'background-color': '#FFF8F0',
        'border-radius': '15px',
        'padding': '15px',
        'box-shadow': 'inset 0 2px 8px rgba(0,0,0,0.05)'
    }
)

# 使用 HTML 按钮来完全自定义样式
button_conversation_html = pn.pane.HTML("""
    <button id="sendBtn" style="
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 15px;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
        width: 150px;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(255, 107, 53, 0.4)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 10px rgba(255, 107, 53, 0.3)';">
        发送对话
    </button>
""", width=150)

button_json_html = pn.pane.HTML("""
    <button id="jsonBtn" style="
        background: linear-gradient(135deg, #C73E1D 0%, #E85D04 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 15px;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba(199, 62, 29, 0.3);
        transition: all 0.3s ease;
        width: 150px;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(199, 62, 29, 0.4)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 10px rgba(199, 62, 29, 0.3)';">
        生成订单
    </button>
""", width=150)

# 使用原生 Panel 按钮（备用方案）
button_conversation = pn.widgets.Button(
    name="发送对话", 
    button_type="default",
    width=150,
    height=45,
    stylesheets=["""
        :host(.bk-btn-default) .bk-btn {
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            font-weight: bold !important;
            font-size: 15px !important;
            box-shadow: 0 4px 10px rgba(255, 107, 53, 0.3) !important;
        }
        :host(.bk-btn-default) .bk-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(255, 107, 53, 0.4) !important;
        }
    """]
)

button_json = pn.widgets.Button(
    name="生成订单", 
    button_type="default",
    width=150,
    height=45,
    stylesheets=["""
        :host(.bk-btn-default) .bk-btn {
            background: linear-gradient(135deg, #C73E1D 0%, #E85D04 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            font-weight: bold !important;
            font-size: 15px !important;
            box-shadow: 0 4px 10px rgba(199, 62, 29, 0.3) !important;
        }
        :host(.bk-btn-default) .bk-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(199, 62, 29, 0.4) !important;
        }
    """]
)
dialogs = []  # 对话历史 

def create_empty_json_html():
    """创建空的JSON显示"""
    return """
    <div style="
        background: linear-gradient(135deg, #FFE5D9 0%, #FFDBC5 100%);
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        border: 3px dashed #FF8C42;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.15);
    ">
        <div style="font-size: 48px; margin-bottom: 15px;">🍕</div>
        <p style="
            color: #C73E1D;
            font-size: 16px;
            margin: 0;
            font-weight: 600;
        ">点击 "生成订单" 查看美味详情</p>
    </div>
    """

def create_styled_json_html(json_obj):
    """创建美化的JSON显示"""
    formatted_json = json.dumps(json_obj, ensure_ascii=False, indent=2)
    escaped_json = html.escape(formatted_json)
    
    return f"""
    <div style="
        background: linear-gradient(135deg, #FFF5E1 0%, #FFE8CC 100%);
        border-radius: 15px;
        padding: 25px;
        border: 3px solid #FF8C42;
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.2);
    ">
        <h3 style="
            margin: 0 0 20px 0; 
            color: #C73E1D;
            font-family: 'Arial', sans-serif;
            display: flex;
            align-items: center;
            font-size: 22px;
            font-weight: bold;
        ">
            <span style="font-size: 28px; margin-right: 12px;">🍕</span>
            订单摘要
        </h3>
        <div style="
            background-color: #FFFFFF;
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #FFBD88;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 2;
            overflow-x: auto;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
        ">
            <pre style="
                margin: 0;
                color: #8B4513;
                white-space: pre-wrap;
                word-wrap: break-word;
            "><code>{escaped_json}</code></pre>
        </div>
        <div style="
            margin-top: 15px;
            padding: 12px;
            background-color: #FFF0E0;
            border-radius: 8px;
            text-align: center;
            color: #C73E1D;
            font-weight: bold;
        ">
            🔥 新鲜出炉，即将送达！
        </div>
    </div>
    """

def generate_order_json():
    """基于当前 context 生成订单 JSON 摘要"""
    messages = context.copy()
    messages.append({
        'role': 'system',
        'content': '''
        创建上一个食品订单的 json 摘要。
        逐项列出每件商品的价格，字段应该是：
        1) 披萨，包括大小
        2) 配料列表
        3) 饮料列表，包括大小
        4) 配菜列表，包括大小
        5) 总价

        你应该返回一个可解析的 JSON 对象，只返回 JSON，不要加任何解释。
        格式示例：
        {
        "pizza": [{"name": "意式辣香肠披萨", "size": "大", "price": 12.95}],
        "toppings": [{"name": "奶酪", "price": 2.00}],
        "drinks": [{"name": "可乐", "size": "中", "price": 2.00}],
        "sides": [{"name": "薯条", "size": "大", "price": 4.50}],
        "total": 19.45
        }
        '''
    })
    try:
        response = get_completion_from_messages(messages, temperature=0)
        # 尝试解析 JSON
        parsed = json.loads(response.strip())
        json_panel.object = create_styled_json_html(parsed)  # 更新面板
    except Exception as e:
        error_html = f"""
            <div style="
                background: linear-gradient(135deg, #FFE5E5 0%, #FFD0D0 100%);
                border-radius: 15px;
                padding: 25px;
                border: 3px solid #FF6B6B;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
            ">
                <h3 style="color: #D32F2F; margin-top: 0; font-size: 20px;">
                    ⚠️ 订单生成失败
                </h3>
                <p style="color: #666; margin: 0; font-size: 14px;">
                    {str(e)}
                </p>
            </div>
            """
        json_panel.object = error_html

def collect_messages(event):
    '''收集用户消息与模型回复，并更新上下文'''
    prompt = inp.value
    if not prompt.strip():
        return
    inp.value = ''

    # 添加用户消息
    context.append({'role': 'user', 'content': prompt})

    # 获取助手回复
    try:
        response = get_completion_from_messages(context)
    except Exception as e:
        response = f"抱歉，出错了：{str(e)}"

    context.append({'role': 'assistant', 'content': response})

    # 更新对话 UI
    dialogs.append(
        pn.Row(
            '👤', 
            pn.pane.Markdown(prompt, width=550),
            styles={
                'background': 'linear-gradient(135deg, #FFFFFF 0%, #FFF8F0 100%)',
                'padding': '15px 20px',
                'margin': '8px 0',
                'border-radius': '20px 20px 5px 20px',
                'border-left': '4px solid #FF6B35',
                'box-shadow': '0 2px 8px rgba(0,0,0,0.08)'
            }
        )
    )
    dialogs.append(
        pn.Row(
            '🤖', 
            pn.pane.Markdown(response, width=550),
            styles={
                'background': 'linear-gradient(135deg, #FFE8D6 0%, #FFD4B3 100%)',
                'padding': '15px 20px',
                'margin': '8px 0',
                'border-radius': '20px 20px 20px 5px',
                'border-left': '4px solid #F7931E',
                'box-shadow': '0 2px 8px rgba(247, 147, 30, 0.15)'
            }
        )
    )

    conversation_panel.clear()
    conversation_panel.extend(dialogs)

button_conversation.on_click(collect_messages)
button_json.on_click(generate_order_json)
json_panel = pn.pane.HTML(
            create_empty_json_html(),
            sizing_mode='stretch_width'
        )

# 初始欢迎语
dialogs.append(
    pn.Row(
    '🤖', 
    pn.pane.Markdown(
        "**你好呀！** 👋\n\n我是你的专属披萨订餐助手！\n\n想来点什么美味呢？", 
        width=550
    ),
    styles={
        'background': 'linear-gradient(135deg, #FFE8D6 0%, #FFD4B3 100%)',
        'padding': '15px 20px',
        'margin': '8px 0',
        'border-radius': '20px 20px 20px 5px',
        'border-left': '4px solid #F7931E',
        'box-shadow': '0 2px 8px rgba(247, 147, 30, 0.15)'
    })
)

conversation_panel.extend(dialogs)

custom_css = """
body {
    background-color: #FFFAE5 !important; /* 设置页面背景颜色 */
}
"""
# 将CSS添加到Panel配置中
pn.config.raw_css.append(custom_css)

# 布局：左侧对话，右侧 JSON
dashboard = pn.template.FastListTemplate(
    title="🍕 披萨订餐机器人",
    header_background='#C73E1D',
    theme_toggle=False,  # 关闭主题切换按钮
    main=[
        pn.Column(
            pn.pane.Markdown(
                "### 🔥 开始您的美味之旅",
                styles={
                    'color': '#C73E1D',
                    'text-align': 'center',
                    'padding': '10px',
                    'background': 'linear-gradient(135deg, #FFF5E1 0%, #FFE8CC 100%)',
                    'border-radius': '15px',
                    'margin-bottom': '15px'
                }
            ),
            inp,
            pn.Row(
                button_conversation, 
                pn.Spacer(width=20),
                button_json,
                styles={
                    'padding': '15px 0',
                    'justify-content': 'center'
                }
            ),
            conversation_panel,
            styles={
                'background-color': '#FFFAF5',
                'padding': '25px',
                'border-radius': '20px'
            },
            width_policy='max'
        )
    ],
    sidebar=[
        pn.Column(
            pn.pane.Markdown(
                "### 订单面板",
                styles={
                    'color': '#C73E1D',
                    'text-align': 'center',
                    'padding': '10px',
                    'background': 'linear-gradient(135deg, #FFF5E1 0%, #FFE8CC 100%)',
                    'border-radius': '15px',
                    'margin-bottom': '15px'
                }
            ),
            json_panel,
            styles={
                'background': 'linear-gradient(135deg, #FFF8F0 0%, #FFEEDD 100%)',
                'padding': '20px',
                'border-radius': '20px',
                'box-shadow': '0 4px 20px rgba(199, 62, 29, 0.1)'
            },
            margin=(10, 10, 10, 10)
        )
    ],
    sidebar_width=450
)

# 显示
dashboard.show()