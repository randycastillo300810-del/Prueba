# models/arbol_decision.py

import math
from collections import Counter

class NodoDecision:
    """Nodo del árbol de decisión"""
    def __init__(self, atributo=None, prediccion=None):
        self.atributo = atributo      # Atributo por el que se divide
        self.prediccion = prediccion  # Si es hoja, la predicción
        self.hijos = {}               # {valor_atributo: nodo_hijo}
    
    def es_hoja(self):
        return self.prediccion is not None

class ArbolDecisionID3:
    """
    Árbol de decisión con algoritmo ID3
    """
    
    def __init__(self):
        self.raiz = None
    
    def entropia(self, datos):
        """Calcula la entropía de un conjunto de datos"""
        if len(datos) == 0:
            return 0
        
        contador = Counter([e.deserto for e in datos])
        total = len(datos)
        
        entropia = 0
        for clase in contador:
            prob = contador[clase] / total
            entropia -= prob * math.log2(prob)
        
        return entropia
    
    def ganancia_informacion(self, datos, atributo):
        """Calcula la ganancia de información al dividir por un atributo"""
        entropia_original = self.entropia(datos)
        total = len(datos)
        
        # Obtener valores únicos del atributo
        valores = set([getattr(e, atributo) for e in datos])
        
        entropia_ponderada = 0
        for valor in valores:
            subconjunto = [e for e in datos if getattr(e, atributo) == valor]
            if len(subconjunto) > 0:
                peso = len(subconjunto) / total
                entropia_ponderada += peso * self.entropia(subconjunto)
        
        return entropia_original - entropia_ponderada
    
    def mejor_atributo(self, datos, atributos):
        """Selecciona el atributo con mayor ganancia de información"""
        mejor_ganancia = -1
        mejor_atributo = None
        
        for atributo in atributos:
            ganancia = self.ganancia_informacion(datos, atributo)
            if ganancia > mejor_ganancia:
                mejor_ganancia = ganancia
                mejor_atributo = atributo
        
        return mejor_atributo
    
    def clase_mayoritaria(self, datos):
        """Retorna la clase más común"""
        contador = Counter([e.deserto for e in datos])
        return contador.most_common(1)[0][0]
    
    def id3(self, datos, atributos_disponibles, profundidad=0, max_profundidad=10):
        """Algoritmo ID3 recursivo"""
        
        # Caso base: todos tienen la misma clase
        clases = [e.deserto for e in datos]
        if len(set(clases)) == 1:
            return NodoDecision(prediccion=clases[0])
        
        # Caso base: no hay atributos o profundidad máxima
        if len(atributos_disponibles) == 0 or profundidad >= max_profundidad:
            return NodoDecision(prediccion=self.clase_mayoritaria(datos))
        
        # Seleccionar mejor atributo
        mejor = self.mejor_atributo(datos, atributos_disponibles)
        
        if mejor is None:
            return NodoDecision(prediccion=self.clase_mayoritaria(datos))
        
        # Crear nodo
        nodo = NodoDecision(atributo=mejor)
        
        # Valores del atributo
        valores = set([getattr(e, mejor) for e in datos])
        nuevos_atributos = [a for a in atributos_disponibles if a != mejor]
        
        # Crear ramas
        for valor in valores:
            subconjunto = [e for e in datos if getattr(e, mejor) == valor]
            if len(subconjunto) == 0:
                nodo.hijos[valor] = NodoDecision(prediccion=self.clase_mayoritaria(datos))
            else:
                nodo.hijos[valor] = self.id3(subconjunto, nuevos_atributos, profundidad + 1, max_profundidad)
        
        return nodo
    
    def entrenar(self, estudiantes, atributos, max_profundidad=10):
        """Entrena el árbol"""
        self.raiz = self.id3(estudiantes, atributos, max_profundidad=max_profundidad)
    
    def predecir(self, estudiante):
        """Predice si un estudiante desertará"""
        if self.raiz is None:
            return False
        
        nodo = self.raiz
        while not nodo.es_hoja():
            valor = getattr(estudiante, nodo.atributo)
            if valor not in nodo.hijos:
                return False
            nodo = nodo.hijos[valor]
        
        return nodo.prediccion
    
    def imprimir(self, nodo=None, nivel=0):
        """Imprime la estructura del árbol"""
        if nodo is None:
            nodo = self.raiz
        
        indentacion = "  " * nivel
        
        if nodo.es_hoja():
            print(f"{indentacion}└── Predicción: {'DESERTA' if nodo.prediccion else 'NO DESERTA'}")
        else:
            if nivel == 0:
                print(f"{indentacion}Raíz: {nodo.atributo}")
            else:
                print(f"{indentacion}├── {nodo.atributo}")
            
            for valor, hijo in nodo.hijos.items():
                print(f"{indentacion}│   Si {nodo.atributo} = {valor}:")
                self.imprimir(hijo, nivel + 2)