from tool import get_completion,get_completion_from_messages
import panel as pn
import json

pn.extension()

panels = []
context = [{'role':'system', 'content':"""
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
雪碧（大、中、小） 3.00、2.00、1.00
瓶装水 5.00
"""} ]

json_display = pn.pane.Markdown("**点击'生成订单JSON'按钮查看订单详情**", width=600)

def collect_messages(_):
    prompt = inp.value
    inp.value = ''
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
    
    panels.append(
        pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(
        pn.Row(
            'Assistant:', 
            pn.pane.Markdown(response, width=600),
            styles={'background-color': '#F6F6F6'}))
    
    return pn.Column(*panels)

def generate_json(_):
    """手动触发生成JSON"""
    messages = context.copy()
    messages.append({
        'role':'system', 
        'content': '''创建上一个食品订单的 json 摘要。\
逐项列出每件商品的价格，字段应该是 1) 披萨，包括大小 2) 配料列表 3) 饮料列表，包括大小 4) 配菜列表包括大小 5) 总价
你应该给我返回一个可解析的Json对象，包括上述字段'''
    })
    
    try:
        response = get_completion_from_messages(messages, temperature=0)
        try:
            json_obj = json.loads(response)
            formatted_json = json.dumps(json_obj, ensure_ascii=False, indent=2)
        except:
            formatted_json = response
        json_display.object = f"**订单JSON：**\n```json\n{formatted_json}\n```"
    except Exception as e:
        json_display.object = f"**生成失败：** {str(e)}"

inp = pn.widgets.TextInput(value="你好", placeholder='这里输入聊天内容…')
button_conversation = pn.widgets.Button(name="Chat!")
button_json = pn.widgets.Button(name="生成订单JSON", button_type="primary")

interactive_conversation = pn.bind(collect_messages, button_conversation)
interactive_json = pn.bind(generate_json, button_json)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation, button_json),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
    pn.layout.Divider(),
    pn.panel(interactive_json, loading_indicator=True),
    json_display
)

pn.serve(dashboard)