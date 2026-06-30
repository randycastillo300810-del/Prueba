# models/apriori.py

from itertools import combinations

class Apriori:
    
    def __init__(self, soporte_minimo=0.05, confianza_minima=0.6):
        self.soporte_minimo = soporte_minimo
        self.confianza_minima = confianza_minima
        self.reglas = []
    
    def calcular_soporte(self, itemset, transacciones):
        """Calcula el soporte de un itemset"""
        if len(transacciones) == 0:
            return 0
        
        count = 0
        for trans in transacciones:
            if itemset.issubset(trans):
                count += 1
        
        return count / len(transacciones)
    
    def encontrar_itemsets_frecuentes(self, transacciones):
        """Encuentra itemsets frecuentes"""
        itemsets_frecuentes = {}
        
        # Itemsets de tamaño 1
        itemsets_t1 = {}
        for trans in transacciones:
            for item in trans:
                itemsets_t1[frozenset([item])] = itemsets_t1.get(frozenset([item]), 0) + 1
        #CODIGO DE RANDY CASTILLO 30727559
        total = len(transacciones)
        k = 1
        itemsets_frecuentes[k] = {
            itemset: count / total 
            for itemset, count in itemsets_t1.items() 
            if count / total >= self.soporte_minimo
        }
        
        # Generar itemsets de mayor tamaño
        while itemsets_frecuentes[k]:
            k += 1
            itemsets_frecuentes[k] = {}
            
            itemsets_prev = list(itemsets_frecuentes[k-1].keys())
            for i in range(len(itemsets_prev)):
                for j in range(i+1, len(itemsets_prev)):
                    union = itemsets_prev[i] | itemsets_prev[j]
                    if len(union) == k:
                        soporte = self.calcular_soporte(union, transacciones)
                        if soporte >= self.soporte_minimo:
                            itemsets_frecuentes[k][union] = soporte
        
        # Eliminar último vacío
        if k in itemsets_frecuentes and not itemsets_frecuentes[k]:
            del itemsets_frecuentes[k]
        
        return itemsets_frecuentes
    
    def generar_reglas(self, transacciones):
        """Genera reglas de asociación"""
        itemsets_frecuentes = self.encontrar_itemsets_frecuentes(transacciones)
        self.reglas = []
        
        for k, itemsets in itemsets_frecuentes.items():
            if k < 2:
                continue
            
            for itemset, soporte_itemset in itemsets.items():
                itemset_lista = list(itemset)
                for i in range(1, len(itemset_lista)):
                    for antecedente in combinations(itemset_lista, i):
                        antecedente_set = frozenset(antecedente)
                        consecuente_set = itemset - antecedente_set
                        
                        soporte_ant = self.calcular_soporte(antecedente_set, transacciones)
                        
                        if soporte_ant > 0:
                            confianza = soporte_itemset / soporte_ant
                            
                            if confianza >= self.confianza_minima:
                                self.reglas.append({
                                    'antecedente': antecedente_set,
                                    'consecuente': consecuente_set,
                                    'soporte': soporte_itemset,
                                    'confianza': confianza
                                })
        
        self.reglas.sort(key=lambda x: x['confianza'], reverse=True)
        return self.reglas
    
    def obtener_reglas_desercion(self):
        return [r for r in self.reglas if 'deserto' in r['consecuente']]