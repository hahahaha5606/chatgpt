import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv 

def get_openai_key():
    _ = load_dotenv(find_dotenv())
    # load_dotenv()读取该.env文件，并将其中的环境变量加载到当前的运行环境中  
    # find_dotenv()寻找并定位.env文件的路径
    # 如果你设置的是全局的环境变量，这行代码则没有任何作用。
    return os.environ['OPENAI_API_KEY']

# 一个封装 OpenAI 接口的函数，参数为 Prompt，返回对应结果
def get_completion(prompt, model="qwen3-vl-32b-thinking"): 
    client = OpenAI(api_key=get_openai_key(), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    '''
    prompt: 对应的提示词
    model: 调用的模型
    '''
    messages = [{
        "role": "user", 
        "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # 模型输出的温度系数，控制输出的随机程度
    )
    # 调用 OpenAI 的 ChatCompletion 接口
    return response.choices[0].message.content

def get_completion_from_messages(messages, model="qwen3-vl-32b-thinking", temperature=0):
    client = OpenAI(api_key=get_openai_key(), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, # 控制模型输出的随机程度
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message.content


