import os

from langchain_openai import ChatOpenAI

default_model_name="doubao-seed-1.6-250615"

def init_chat_model():
    # 配置 OpenAI API
    api_key = os.getenv("OPENAI_API_KEY")

    return ChatOpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
        model=default_model_name)


if __name__ == '__main__':
     print(init_chat_model().invoke("你好"))
