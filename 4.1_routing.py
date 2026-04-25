
DISTANCE_MATRIX = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
POINTS = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3
}

# Bir rota sırası verildiğinde bunun distance'ını hesaplayan bir fonksiyon yazalım.
def calculate_distance(route: list[str]) -> int:
    """ Verilen bir rota sırasının distance'ını hesaplar.
    Örneğin: ['C', 'B', 'D', 'A'] rotası için:
    C -> B = 35
    B -> D = 25
    D -> A = 30
    Toplam distance = 35 + 25 + 30 = 90
    
    Args:
        route: Rota sırası, örneğin ['C', 'B', 'D', 'A']
    Returns:
        Rota sırasının distance'ı, örneğin 90
    """
    
    total_distance = 0
    for i in range(len(route) - 1):
        # rota içerisinden sırayla iki nokta alalım
        #  örneğin: C -> B, B -> D, D -> A
        #  bu noktaların id'lerini alalım
        from_node_id = route[i]
        to_node_id = route[i + 1]
        # id'si bilinen noktaların distance matrix'de nerede olduğunu bulmak için:
        #  POINTS dict içinden id'leri index'e çevirelim
        from_node_index = POINTS[from_node_id]
        to_node_index = POINTS[to_node_id]
        # aradaki mesafeyi distance matrix'den alalım ve total_distance'a ekleyelim
        total_distance += DISTANCE_MATRIX[from_node_index][to_node_index]
    return total_distance


def is_good_solution(previous_distance, new_distance):
    """ Yeni bulunan rota sırasının önceki rota sırasından daha iyi olup olmadığını kontrol eder.
    
    Args:
        previous_distance: Önceki rota sırasının distance'ı
        new_distance: Yeni rota sırasının distance'ı
    Returns:
        Yeni rota sırasının önceki rota sırasından daha iyi olup olmadığı (True/False)
    
    """
    return new_distance < previous_distance


random_route = ['B', 'A', 'C', 'D']

best_distance = float('inf')
best_route = None

# Tahmini olarak 4 elemanlı bir rota için 24 farklı permütasyon vardır.
# Ben burada 25 kere rota sırasını döndürerek farklı bir rota sırası elde etmeye çalışacağım.
for i in range(50):
    result = calculate_distance(random_route)
    print("Rota: ", random_route)
    print("Toplam Mesafe: ", result)
    
    if is_good_solution(best_distance, result):
        best_distance = result
        best_route = random_route.copy()
        
    random_route = random_route[1:] + [random_route[0]]  # Rotate the route
    
print("En iyi rota: ", best_route)
print("En iyi rota mesafesi: ", best_distance)



""" 

NOT 25.04.2026 : 
Burada basit tutmak için özellikle bazı detaylara girmedim.
Örneğin 4 point ile basit tuttum. Başlangıç rotasını sadece son elemanı başa alarak yeni rota elde edecek şekilde 
değiştirerek rota optimizasyonu yapmaya çalıştım. Burada önemli olan bir sonraki kodda bunu bir tool olarak tanımlayarak 
LLM'in bu tool'u kullanarak rota optimizasyonu yapmasını sağlamak. 

Kodu copilotun her boka girip beni sinir etmesi dışında ben yazdım. AQ copilotu hala bir şey öneriyor yorum satırında bile. 
Ama rota listesinin son elemanını başa almayı o önerdi gg. 
"""