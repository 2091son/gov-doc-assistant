from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 创建 OpenAI 客户端 - 直接写死 Key（测试用）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 生成文章路由
@app.route('/generate', methods=['POST'])
def generate():
    # 获取用户提交的数据
    topic = request.form.get('topic')
    doc_type = request.form.get('doc_type')
    style = request.form.get('style')

    print(f"收到请求: topic={topic}, doc_type={doc_type}, style={style}")

    # 构建 Prompt
    prompt = f"""
你是一位资深公文写作专家。请根据以下要求写一篇公文：

主题：{topic}
文种：{doc_type}
风格：{style}

要求：
1. 格式规范，符合公文写作标准
2. 语言得体，符合所选风格
3. 结构清晰，有标题、正文、落款
    """

    # 调用 AI
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一位资深的公文写作专家。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # 获取 AI 生成的文本
    result = response.choices[0].message.content

    # 返回 JSON 给前端
    return jsonify({'result': result})

# 启动服务器
if __name__ == '__main__':
    app.run(debug=True)