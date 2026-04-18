# LangChain ve LangGraph: Kapsamlı Türkçe Dokümantasyon

Metin tabanlı asistanlar oluşturmak için **LangChain** ve çalışma mantığını graf tabanlı bir devlet makinesi ile birleştiren **LangGraph** çerçeveleri (framework) kullanılır. Sistemlerin takibi ve optimizasyonu ise **LangSmith** arayüzü sayesinde gerçekleştirilir. 

İncelenen dokümanların genel çerçevesi şu başlıklar etrafında toplanmıştır:

---

## 1. Modeller (Models)

Büyük Dil Modelleri (LLM), LangChain ajanlarının eyleme dökme kabiliyetini ve karar verme yetilerini yöneten yapay zeka üniteleridir. Bir model, araç kullanma (tool calling), verileri yapısal formda çıkarma (structured output) veya çoklu adımlı çözümleme özellikleri (reasoning) barındırabilir. 

### Temel Sınıflandırma
- **Chat Modelleri:** LLM çağırma komutları genellikle sohbet arayüzüne dayalıdır. `init_chat_model` ile OpenAI, Anthropic, Gemini, AWS Bedrock gibi modelleyiciler arası geçiş saniyeler içinde kod değişikliğine gerek olmadan yapılır. 
- **Çalıştırma Metotları:** 
  - `invoke()`: Modeli çağırır ve tam yanıtı bekler.
  - `stream()`: Yanıtı token bazlı akışla (stream) parça parça alır. Arayüzde yazma animasyonları için mükemmeldir.
  - `batch()`: Toplu veri işlerken birden fazla isteği paralel işler.
- **Yapılandırılmış Çıktı (Structured Output):** `with_structured_output(PydanticModel)` ile modelin çıktılarını kesin sınırlara sahip JSON schemalarına ya da Python sınıflarına dökmesi zorunlu kılınabilir. 
- **Araç Kullanımı:** Modellerin gerçek dünyayla etkileşime girebilmesi için `model.bind_tools([arac_1, arac_2])` formatında araçları bilmesi sağlanır. 

---

## 2. Mesajlar (Messages)

Model, geçmiş konuşma bilgisini ve yapısal komutları **Mesajlar (Messages)** formatında alır. 

- **SystemMessage:** Sistemin asıl kişiliğini ve kalıtsal kurallarını belirtir. Örn: "Sen deneyimli bir coğrafyacısın." 
- **HumanMessage:** Kullanıcıdan gelen sorular ve promptlardır. Metin, resim veya ses gibi Multimodal (Çoklu Model) verileri taşıyabilir. 
- **AIMessage:** Modelin cevaplarıdır; içeriklerin yanı sıra modelin yapmak istediği araç aramalarının bilgilerini (`tool_calls`) veya kullanılan token maliyetlerini içerir.
- **ToolMessage:** Model bir aracı çalıştırdığında aracın dış dünyadan (Örn: Veritabanından) elde edip getirdiği verileri LLM'in tekrar yorumlaması için mesaj zincirine eklendiği formattır.

---

## 3. Araçlar (Tools)

LangChain araçları, dil modellerini API'lere, veritabanlarına veya karmaşık fonksiyonlara bağlar. Modelin, kendi bilgi sınırlarını veya güncel olmayan verisini dışarıdan veri çekerek esnetmesine yardımcı olurlar. 

### Araç Oluşturma
Aracın model tarafından ne işe yaradığını anlaması için `@tool` dekoratörü ve kapsamlı bir `docstring` (Açıklama Bloku) eklenerek fonksiyon tanımlanır.

### ToolRuntime ve İç Bağlam (Context) Sınıfları
Gelişmiş LangGraph sistemlerinde araç sadece parametrelerini almakla kalmaz `ToolRuntime` kütüphanesi yardımıyla Ajanın anlık hafızasına (\`State\`), kalıcı veritabanı hafızasına (\`Store\`) veya oturum bilgilerine değişken aktarımı yapabilir, grafiğin çalışma anını doğrudan etkileyebilir.

### ToolNode
Sistemler `ToolNode` yapısıyla araçları LangGraph akışına dahil eder. Aracın çalışırken sadece basit bir metin mesajı değil, `Command(update={"messages": ...})` veya bir python `Dict` objesi dönmesi sağlanarak sistemin devam edeceği rotayı (Route) anlık tayin edebilir.

---

## 4. Ajanlar (Agents)

Ajanlar, modellerin ve araçların zekice harmanlanıp tekrar eden, düşünen (Reason) ve eyleme geçen (Act) döngüler kurmasını sağlayan sistemlerdir (**ReAct pattern**). Büyük bir görev küçük adımlara bölünür.

**Bileşenleri şunlardır:**
1. **Model:** Beyin görevi gören API.
2. **Tools:** Gerçek dünyayla eylemsel bağlantı. 
3. **State & Memory:** LangGraph'ın yönettiği sohbet ve durum geçmişi.
4. **Middleware (Ara Katmanlar):** Bazı durumlara ve kurallara göre dinamik sistem prompt'u atama, sadece kullanıcı girişi yapmışsa bazı spesifik araçları modele erişilebilir kılma (Dinamik Tools Seçimi) gibi işlevler middleware'lerle ajanlara aktarılabilir.

---

## 5. Çoklu Ajan Sistemleri (Multi-Agent Mimarisi)

Ajanlara yüzlerce araç verirsek veya karmaşıklık had safhaya çıkarsa, tek bir modelin kafası (Context Window limitati) karışabilir ve performansı çakılır. Bunun yerine işlevlerin **bağlam sınırlarını** daraltıp yetkilendirmesi olan **Multi-Agent Pattern** yapıları uygulanır:

- **Subagents:** Üst bir ajan, bazı işlemleri kendi araçları olarak tasarlanmış olan Alt Ajanlara devreder. Cevabı alt ajan ürettikten sonra tekrar ana ajana geçer. Maliyetli ama yönetim kolaydır.
- **Handoffs:** Ajanlar işlerini bitirdikçe grafın devam işini dinamik olarak sonraki ajana (State değiştirerek) aktarırlar. Paralel araç kullanımı için az, tekrarlı eylemler için maliyet etkilidir.
- **Skills:** Ajan aynı ajan olarak kalır ama sadece ihtiyaç anında dokümanları veya özel veri tabanı parçalarını dinamik bir skill olarak o anki State hafızasına geçirir. 
- **Router (Dağıtıcı):** İlk gelen kullanıcı isteğini "Bu isteğin uzmanlık alanı nedir?" diye analizler. Gerekli bir veya birkaç ajana paralel yönlendirme yapar, daha sonra "Sentezleyici Node" bu alt ajanların verilerini toparlayıp son cevabı derler. Verimliliği çok yüksektir.

---

## 6. LangSmith Platformu

Ajanlar ve LLM kullanım senaryoları büyüdükçe bu verilerin izlenmesi bir zorunluluktur. LangSmith **gözlemlenebilirlik (Observability)** ve **değerlendirme (Evaluation)** aracıdır.

- **Tracing:** Modelin hangi adımında durduğunu, hangi aracı hangi parametreyle çağırdığını saniye saniye debug etme ekranıdır. 
- **Promt Testleri:** Tasarladığınız bir araç promptunu değiştirdiğinizde, LangSmith veri testleri sayesinde eskiden başarılı olduğu verilerde hala başarılı olup olmadığını regression metrikleriyle kıyaslayarak size sunar.
- Ajanların ve log kayıtlarının CI/CD benzeri yapılandırılmasıyla ekiplerin paralel çalışması sağlanır. 
