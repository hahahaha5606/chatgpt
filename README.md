# 订餐机器人

原案例来自：https://datawhalechina.github.io/llm-cookbook/#/C1/8.%20%E8%81%8A%E5%A4%A9%E6%9C%BA%E5%99%A8%E4%BA%BA%20Chatbot

## 项目简介
一个“订餐机器人”的简单实践：我们需要这个机器人自动收集用户消息，接受比萨饼店的订单。

同时，我们要求该订餐机器人模型对上一个订单创建 JSON 摘要，方便我们发送给订单系统。
JSON 摘要中应包括以下字段：

1.  披萨，包括尺寸
2.  配料列表
3.  饮料列表
4.  辅菜列表，包括尺寸，
5.  总价格。

## 运行说明
1. 安装可视化界面库 `pip install panel` 。

2. 使用时需要创建.env文件用来存储模型的 API_KEY ，文件内容为：
`OPENAI_API_KEY="sk-..."`

## 效果
<img width="1836" height="913" alt="image" src="https://github.com/user-attachments/assets/fa9d3bf2-8447-4ea2-a700-8acd5caa97a2" />
