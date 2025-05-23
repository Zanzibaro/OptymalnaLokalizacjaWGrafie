import networkx as nx
import matplotlib.pyplot as plt

class FireStationOptimizer:
    def __init__(self):
        self.graph = nx.Graph()
        self.positions = {}
        
    def create_example_graph(self):
        """Tworzy przykładowy graf reprezentujący miasteczko z budynkami i drogami."""
        # Dodajemy węzły - budynki w miasteczku
        buildings = [
            "Dom1", "Dom2", "Dom3", "Dom4", "Dom5", 
            "Sklep", "Szkoła", "Urząd", "Kościół", "Park"
        ]
        
        # Dodajemy węzły do grafu z pozycjami dla wizualizacji
        self.graph.add_node("Dom1", pos=(0, 0))
        self.graph.add_node("Dom2", pos=(1, 2))
        self.graph.add_node("Dom3", pos=(3, 1))
        self.graph.add_node("Dom4", pos=(5, 0))
        self.graph.add_node("Dom5", pos=(6, 2))
        self.graph.add_node("Sklep", pos=(2, 0))
        self.graph.add_node("Szkoła", pos=(4, 2))
        self.graph.add_node("Urząd", pos=(2, 3))
        self.graph.add_node("Kościół", pos=(0, 4))
        self.graph.add_node("Park", pos=(5, 4))
        
        # Zapisujemy pozycje węzłów do wizualizacji
        self.positions = nx.get_node_attributes(self.graph, 'pos')
        
        # Dodajemy krawędzie - drogi między budynkami z wagami (odległościami)
        self.graph.add_edge("Dom1", "Dom2", weight=2.5)
        self.graph.add_edge("Dom1", "Sklep", weight=2)
        self.graph.add_edge("Dom2", "Urząd", weight=1.5)
        self.graph.add_edge("Dom2", "Szkoła", weight=3)
        self.graph.add_edge("Dom3", "Sklep", weight=1)
        self.graph.add_edge("Dom3", "Szkoła", weight=1.5)
        self.graph.add_edge("Dom3", "Dom4", weight=2)
        self.graph.add_edge("Dom4", "Dom5", weight=2.5)
        self.graph.add_edge("Dom4", "Szkoła", weight=2)
        self.graph.add_edge("Dom5", "Szkoła", weight=2.5)
        self.graph.add_edge("Dom5", "Park", weight=3)
        self.graph.add_edge("Sklep", "Dom2", weight=1.5)
        self.graph.add_edge("Szkoła", "Urząd", weight=2)
        self.graph.add_edge("Szkoła", "Park", weight=2)
        self.graph.add_edge("Urząd", "Kościół", weight=2)
        self.graph.add_edge("Urząd", "Park", weight=3)
        self.graph.add_edge("Kościół", "Park", weight=5)
        
        print(f"Stworzono przykładowy graf miasteczka z {len(buildings)} budynkami.")
        
    def load_graph_from_file(self, file_path):
        """Wczytuje graf z pliku tekstowego."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                # Wczytaj liczbę węzłów
                n = int(lines[0].strip())
                
                # Wczytaj węzły i ich pozycje
                for i in range(1, n+1):
                    if i < len(lines):
                        parts = lines[i].strip().split()
                        if len(parts) >= 3:
                            node_name = parts[0]
                            x, y = float(parts[1]), float(parts[2])
                            self.graph.add_node(node_name, pos=(x, y))
                
                # Zapisz pozycje do wizualizacji
                self.positions = nx.get_node_attributes(self.graph, 'pos')
                
                # Wczytaj krawędzie
                for i in range(n+1, len(lines)):
                    parts = lines[i].strip().split()
                    if len(parts) >= 3:
                        node1, node2, weight = parts[0], parts[1], float(parts[2])
                        self.graph.add_edge(node1, node2, weight=weight)
                
                print(f"Wczytano graf z pliku: {file_path}")
                print(f"Liczba węzłów: {self.graph.number_of_nodes()}")
                print(f"Liczba krawędzi: {self.graph.number_of_edges()}")
                
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku: {e}")
            return False
        return True
    
    def manual_input(self):
        """Pozwala użytkownikowi ręcznie wprowadzić dane grafu."""
        try:
            self.graph.clear()
            n = int(input("Podaj liczbę budynków (węzłów): "))
            
            print("Wprowadź nazwy budynków i ich współrzędne (x, y):")
            for i in range(n):
                node_input = input(f"Budynek {i+1} (nazwa x y): ").strip().split()
                if len(node_input) >= 3:
                    node_name = node_input[0]
                    x, y = float(node_input[1]), float(node_input[2])
                    self.graph.add_node(node_name, pos=(x, y))
            
            # Zapisz pozycje do wizualizacji
            self.positions = nx.get_node_attributes(self.graph, 'pos')
            
            m = int(input("Podaj liczbę dróg (krawędzi): "))
            print("Wprowadź drogi (budynek1 budynek2 odległość):")
            for i in range(m):
                edge_input = input(f"Droga {i+1}: ").strip().split()
                if len(edge_input) >= 3:
                    node1, node2, weight = edge_input[0], edge_input[1], float(edge_input[2])
                    self.graph.add_edge(node1, node2, weight=weight)
            
            print("Graf został utworzony pomyślnie.")
            return True
        except Exception as e:
            print(f"Błąd podczas wprowadzania danych: {e}")
            return False
    
    def find_optimal_location(self):
        """
        Znajduje optymalną lokalizację straży pożarnej używając algorytmu centrum grafu.
        Zwraca węzeł będący centrum grafu (minimalizujący maksymalną odległość do najdalszego węzła).
        """
        if not self.graph:
            print("Graf jest pusty. Najpierw utwórz graf.")
            return None
        
        # Dla każdego węzła obliczamy najdłuższą najkrótszą ścieżkę do innego węzła
        eccentricities = {}
        
        print("\nObliczanie optymalnej lokalizacji straży pożarnej...")
        print("Obliczanie ekscentryczności dla każdego węzła:")
        
        # Dla każdego węzła obliczamy najkrótsze ścieżki do wszystkich innych węzłów
        for node in self.graph.nodes:
            # Obliczamy najkrótsze ścieżki od tego węzła do wszystkich innych
            shortest_paths = nx.single_source_dijkstra_path_length(self.graph, node, weight='weight')
            
            # Ekscentryczność to maksymalna odległość do najdalszego węzła
            eccentricity = max(shortest_paths.values())
            eccentricities[node] = eccentricity
            
            print(f"Węzeł: {node}, Ekscentryczność: {eccentricity:.2f}")
        
        # Centrum grafu to węzeł o najmniejszej ekscentryczności
        optimal_location = min(eccentricities, key=eccentricities.get)
        min_eccentricity = eccentricities[optimal_location]
        
        # Znajdź wszystkie węzły o minimalnej ekscentryczności (może być więcej niż jeden)
        optimal_locations = [node for node, ecc in eccentricities.items() if abs(ecc - min_eccentricity) < 1e-9]
        
        return optimal_locations, min_eccentricity, eccentricities
    
    def visualize_graph(self, optimal_locations=None, eccentricities=None):
        """Wizualizuje graf miasteczka z zaznaczeniem optymalnej lokalizacji straży pożarnej."""
        if not self.graph:
            print("Graf jest pusty. Najpierw utwórz graf.")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Rysujemy węzły
        nx.draw_networkx_nodes(self.graph, self.positions, node_size=500, 
                              node_color='lightblue', alpha=0.8)
        
        # Jeśli mamy optymalne lokalizacje, zaznaczamy je na czerwono
        if optimal_locations:
            optimal_nodes = nx.draw_networkx_nodes(self.graph, self.positions, 
                                                 nodelist=optimal_locations, 
                                                 node_color='red', node_size=700, alpha=0.8)
            optimal_nodes.set_edgecolor('black')
        
        # Rysujemy krawędzie z wagami
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edges(self.graph, self.positions, width=1.5, alpha=0.7)
        nx.draw_networkx_edge_labels(self.graph, self.positions, edge_labels=edge_labels, font_size=8)
        
        # Dodajemy etykiety węzłów
        nx.draw_networkx_labels(self.graph, self.positions, font_size=10, font_weight='bold')
        
        # Jeśli mamy ekscentryczności, dodajemy je jako etykiety
        if eccentricities:
            pos_labels = {}
            for node, (x, y) in self.positions.items():
                pos_labels[node] = (x, y-0.2)
                
            eccent_labels = {node: f"E: {ecc:.2f}" for node, ecc in eccentricities.items()}
            nx.draw_networkx_labels(self.graph, pos_labels, labels=eccent_labels, font_size=8, font_color='blue')
        
        # Dodajemy tytuł
        if optimal_locations:
            plt.title(f"Optymalna lokalizacja straży pożarnej: {', '.join(optimal_locations)}")
        else:
            plt.title("Graf miasteczka")
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig("wizualizacja_grafu.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_results_to_file(self, optimal_locations, min_eccentricity, eccentricities):
        """Zapisuje wyniki do pliku tekstowego."""
        with open("wyniki.txt", "w", encoding="utf-8") as f:
            f.write("WYNIKI OPTYMALIZACJI LOKALIZACJI STRAŻY POŻARNEJ\n")
            f.write("=================================================\n\n")
            
            f.write(f"Optymalna lokalizacja straży pożarnej: {', '.join(optimal_locations)}\n")
            f.write(f"Minimalna maksymalna odległość: {min_eccentricity:.2f}\n\n")
            
            f.write("Ekscentryczności dla wszystkich węzłów:\n")
            f.write("-------------------------------------\n")
            
            # Sortujemy węzły według ekscentryczności
            sorted_nodes = sorted(eccentricities.items(), key=lambda x: x[1])
            
            for node, ecc in sorted_nodes:
                f.write(f"{node}: {ecc:.2f}\n")
        
        print(f"Wyniki zapisano do pliku: wyniki.txt")


def main():
    optimizer = FireStationOptimizer()
    
    while True:
        print("\n" + "="*50)
        print("PROGRAM DO OPTYMALIZACJI LOKALIZACJI STRAŻY POŻARNEJ")
        print("="*50)
        print("1. Stwórz przykładowy graf miasteczka")
        print("2. Wczytaj graf z pliku")
        print("3. Wprowadź graf ręcznie")
        print("4. Znajdź optymalną lokalizację straży pożarnej")
        print("5. Wizualizuj graf")
        print("6. Wyjście")
        
        choice = input("\nWybierz opcję (1-6): ")
        
        if choice == '1':
            optimizer.create_example_graph()
        
        elif choice == '2':
            file_path = input("Podaj ścieżkę do pliku: ")
            optimizer.load_graph_from_file(file_path)
        
        elif choice == '3':
            optimizer.manual_input()
        
        elif choice == '4':
            if optimizer.graph.number_of_nodes() == 0:
                print("Graf jest pusty. Najpierw utwórz graf.")
                continue
                
            optimal_locations, min_eccentricity, eccentricities = optimizer.find_optimal_location()
            
            print(f"\nWYNIKI:")
            print(f"Optymalna lokalizacja straży pożarnej: {', '.join(optimal_locations)}")
            print(f"Minimalna maksymalna odległość: {min_eccentricity:.2f}")
            
            # Zapisz wyniki
            optimizer.save_results_to_file(optimal_locations, min_eccentricity, eccentricities)
            
            # Wizualizuj wyniki
            optimizer.visualize_graph(optimal_locations, eccentricities)
        
        elif choice == '5':
            optimizer.visualize_graph()
        
        elif choice == '6':
            print("Dziękuję za skorzystanie z programu!")
            break
        
        else:
            print("Niepoprawna opcja. Wybierz ponownie.")


if __name__ == "__main__":
    main()