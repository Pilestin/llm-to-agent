# 1. Gerekli kütüphaneleri yükleyin:
# pip install langchain langchain-ollama

import os
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

# --- Araçları (Tools) Tanımlayalım ---

@tool
def hesap_makinesi(ifade: str) -> str:
    """Verilen matematiksel ifadeyi hesaplar. Örneğin, '2 + 2'."""
    try:
        sonuc = eval(ifade)
        return f"{ifade} = {sonuc}"
    except Exception as e:
        return f"Hesaplama hatası: {e}"

@tool
def simdiki_zaman() -> str:
    """Bugünün tarihini ve saatini döndürür."""
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Ana Program ---
def main():
    # 2. Ollama ile yerel LLM'i yapılandırın.
    #    'llama3.2' yerine indirdiğiniz başka bir modeli yazabilirsiniz.
    llm = ChatOllama(model="qwen2.5-3b")

    # 3. Kullanılabilir araçları bir listeye ekleyin.
    tools = [hesap_makinesi, simdiki_zaman]

    # 4. Ajan için bir istem (prompt) şablonu oluşturun.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sen araçları kullanabilen yardımsever bir asistansın."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 5. Araç çağırabilen ajanı oluşturun.
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 6. Ajanı çalıştıracak yürütücüyü (executor) oluşturun.
    #    verbose=True diyerek ajanın düşünme sürecini görebiliriz.
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 7. Ajanı test edelim!
    print("--- Hesap Makinesi Testi ---")
    agent_executor.invoke({"input": "15 ile 7'yi topla"})

    print("n--- Zaman Testi ---")
    agent_executor.invoke({"input": "Bugün ayın kaçı?"})

if __name__ == "__main__":
    main()