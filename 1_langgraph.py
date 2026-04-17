# 1. Gerekli kütüphaneleri yükleyin:
# pip install langchain langchain-ollama langgraph

import os
import datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
# from langgraph.prebuilt import create_react_agent BU APTAL FONKSİYON KALDIRILMIŞ
from langchain.agents import create_agent
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
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Ana Program ---
def main():
    # 2. Ollama ile yerel LLM'i yapılandırın.
    llm = ChatOllama(model="qwen2.5-3b")

    # 3. Kullanılabilir araçları bir listeye ekleyin.
    tools = [hesap_makinesi, simdiki_zaman]

    # 4. Ajan için bir sistem mesajı (prompt) oluşturun.
    system_message = "Sen araçları kullanabilen yardımsever bir asistansın."

    # 5. LangGraph ile güncel ajan yapısını oluşturun.
    agent = create_agent(llm, tools, system_prompt=system_message)

    # 6. Ajanı test edelim!
    print("--- Hesap Makinesi Testi ---")
    # Artık girdilerimizi bir mesaj listesi olarak gönderiyoruz.
    response1 = agent.invoke({"messages": [("user", "15 ile 7'yi topla")]})
    # Sonucu ekrana yazdır (Cevaplar artık messages listesinin en son elemanında dönüyor)
    print(response1["messages"][-1].content)

    print("\n--- Zaman Testi ---")
    response2 = agent.invoke({"messages": [("user", "Bugün ayın kaçı?")]})
    print(response2["messages"][-1].content)

if __name__ == "__main__":
    main()