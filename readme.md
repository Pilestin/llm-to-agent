# LLM to Agent

Bu repo llm'lerin farklı araçlar ile nasıl etkileşim kurudğunu öğrenmem için oluşturduğum bir çalışma alanıdır. Burada özellikle Ollama ve LangChain kullanarak detaylarıöğrenmeyi amaçlıyorum.


### Kurulum 

1. Gerekli kütüphaneleri yükleyin:

   ```bash
   pip install -r requirements.txt
   ```

2. Ollama'yı kurun ve yapılandırın. (https://ollama.com/docs/installation)

3. LangChain ve LangGraph hakkında bilgi edinmek için resmi dokümantasyonlarına göz atabilirsiniz:
   - LangChain: https://langchain.com/docs/
   - LangGraph: https://langgraph.com/docs/
   

- Aşağıdaki dosyalar, bu repo içerisinde bulunan örnek kodları ve açıklamalarını içermektedir:


| File | Description | 
|------|-------------|
| 1_langchain.py | Ana LangChain ajanı kodu |
| 2_ollama.py | Ollama ile entegrasyon örneği |
| 3_langgraph.py | LangGraph kullanarak ajan oluşturma |
| 4.1_route-optimizer.py | Rota optimizasyonu yapan bir script |
| 4.2_route-optimizer-agent.py | Verilen bir rota örneğinin distance'ını hesaplayan ajan (function call yapan) |
| 4.3_route-optimizer-agent.py | Rota optimizasyonu yapan bir ajan, optimum rotayı verir | 


Daha önce hiç rotalama ile uğraştıysanız bu problemin bir sıralama problemi olduğunu görmüşsünüzdür. Yani elimizde bir rota sırası var, bu sırayı değiştirerek en kısa mesafeli olacak şekilde optimize etmek istiyoruz. 

Bunun için basit bir örnek üzerinden gidelim. Diyelim ki elimizde 4 nokta var: A, B, C ve D. Bu noktalar arasındaki mesafeler biliniyor olsun ve biz bu noktaların hepsine uğramalıyız (teslimat problemi veya klasik TSP). Örneğin şu sırada/rotada ['A', 'B', 'C', 'D'] ziyaretleri yapsak sonuç ne olurdu?. Biz bu rotayı optimize etmek istiyoruz, yani en kısa mesafeli rotayı bulmak istiyoruz.

Bunun için [4.1_routing.py](4.1_routing.py) koduna bakabilirsiniz. Basit bir şekilde başlangıçta verilen rota sırasını hesaplayan (matrisden mesafeleri okuyup toplayan) ve daha sonra bu sırayı noktaların yerlerini değiştirerek optimize etmeye çalışan bir fonksiyon var. Burada iki önemli fonksiyon var: 
1. `calculate_distance` 
2. `optimize_route`. 


`calculate_distance` fonksiyonu verilen bir rota sırasının toplam mesafesini hesaplıyor. Aslında matris(veya tablo) içerisinden pointler arasındaki mesafeleri okuyup topluyor. `optimize_route` fonksiyonu ise verilen bir rota sırasını optimize etmeye çalışıyor. Bu işlem için basit bir algoritma kullanıyor, yani noktaların yerlerini değiştirerek daha kısa bir rota bulmaya çalışıyor. Bunu belirli bir iterasyon sayısı kadar yapıyor ve her iterasyonda sonuca bakarak en iyisini yakalamaya çalışıyor. (Aslında çok ilkel ama bu örnek için yeterli).

Şimdi asıl soru geliyor: 

- Bu optimizasyon fonksiyonlarını bir AI AGENT'a vererek kullandırtabilir miyiz? Yani kullanıcı text olarak direktifi verdiğinde, bu fonksiyonları kullanarak sonucu söylesin.

- CEVAP: Evet, LangChain / LangGraph framework ve OLLAMA gibi araçları kullanarak bu fonksiyonları bir AI AGENT'a entegre edebiliriz.



Öncelikle [4.2_route-calculater-agent.py](4.2_route-calculater-agent.py) kodunu inceleyebilirsiniz. Burada verilen bir rotanın toplam mesafesini hesaplayan bir ajan var. Yani `calculate_distance` fonksiyonunu kullanabiliyor. 

Daha sonra [4.3_route-optimizer-agent.py](4.3_route-optimizer-agent.py) koduna bakabilirsiniz. Burada ise `optimize_route` fonksiyonunu da kullanarak rota optimizasyonu yapan bir ajan var. Yani kullanıcı text olarak bir başlangıç rotası verdiğinde, bu ajan bu rotayı optimize ediyor ve en iyi rotayı ve mesafeyi söylüyor.









ÖRnek:
```python
(myenv) ➜  llm-to-agent git:(master) ✗ python3 4.3_route-optimizer-agent.py 
Rota optimizer chati basladi. Cikmak icin 'q' yaz.
Sen: merhaba
Ajan: Merhaba! Nasıl yardımcı olabilirim?
Sen: rota optimize eder misin, başlangıç rotan ['A', 'B', 'C', 'D']
Ajan: En iyi rotam: ['C', 'D', 'A', 'B']  
En iyi mesafemiz: 60 km  
```


Bu en iyi rotayı tekrar doğrulmak için, başlangıç rotanız olan ['A', 'B', 'C', 'D'] ile aynı obje üzerinde tekrardan bir deneme yaptım. 

```python
Sen: peki ['A', 'B', 'C', 'D'] bu rotanın mesafesini verir misin
Ajan: It appears that you've provided a list of route distances for traveling from point A (let's call it "A") to point D (let's call it "D"), via points B and C, in different orders. Each entry shows the distance for one possible order of visiting these three points.

Here are the distances:

1. A → B → C → D: 75 units
2. B → A → C → D: 85 units
3. C → A → B → D: 60 units
4. D → A → B → C: 65 units

This pattern continues with different combinations of these points, each time changing the order in which they are visited.

If you need any specific information or analysis from this list (like finding the shortest path, longest path, average distance, etc.), please let me know!
Sen: 
```
