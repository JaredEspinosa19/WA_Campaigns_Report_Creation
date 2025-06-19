from langchain_ollama import ChatOllama

chat_model = ChatOllama(model="llama3.1", device="cuda")

response = chat_model.invoke("Who was the first man on the moon?")

print(response.model_dump_json())