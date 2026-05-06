

Bu repo llm'lerin farklı araçlar ile nasıl etkileşim kurudğunu öğrenmem için oluşturduğum bir çalışma alanıdır. Burada özellikle Ollama ve LangChain kullanarak detaylarıöğrenmeyi amaçlıyorum.


### Kurulum 

1. Gerekli kütüphaneleri yükleyin:

   ```bash
   pip install -r requirements.txt
   ```



| File | Description | 
|------|-------------|
| 1_langchain.py | Ana LangChain ajanı kodu |
| 2_ollama.py | Ollama ile entegrasyon örneği |
| 3_langgraph.py | LangGraph kullanarak ajan oluşturma |
| 4.1_route-optimizer.py | Rota optimizasyonu yapan bir script |
| 4.2_route-optimizer-agent.py | Verilen bir rota örneğinin distance'ını hesaplayan ajan (function call yapan) |
| 4.3_route-optimizer-agent.py | Rota optimizasyonu yapan bir ajan, optimum rotayı verir | 







ÖRnek:

(myenv) ➜  llm-to-agent git:(master) ✗ python3 4.3_route-optimizer-agent.py 
Rota optimizer chati basladi. Cikmak icin 'q' yaz.
Sen: merhaba
Ajan: Merhaba! Nasıl yardımcı olabilirim?
Sen: rota optimize eder misin, başlangıç rotan ['A', 'B', 'C', 'D']
Ajan: En iyi rotam: ['C', 'D', 'A', 'B']  
En iyi mesafemiz: 60 km  

Bu en iyi rotayı tekrar doğrulmak için, başlangıç rotanız olan ['A', 'B', 'C', 'D'] ile aynı obje üzerinde tekrardan bir deneme yaptım. En iyi sonuç, önceki denemelerden elde ettiğimiz en iyi mesafeyi korudur.

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
