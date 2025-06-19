import pygame
import random
import os
import sys
import math

# Inicialización de Pygame
pygame.init()
pygame.mixer.init()

# Constantes del juego
VENTANA = (600, 800)
CUADRO = 40
GRID = VENTANA[0] // CUADRO, VENTANA[1] // CUADRO

# Colores (R,G,B)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROSA_CLARO = (255, 228, 234)
ROSA_OSCURO = (255, 208, 220)
VERDE = (50, 205, 50)
VERDE_OSCURO = (34, 139, 34)
ROJO = (255, 69, 69)
ROJO_OSCURO = (220, 20, 60)
MARRON = (160, 82, 45)
ROSA_TRANS = (255, 192, 203, 230)

# Configuración de ventana y fuente
pantalla = pygame.display.set_mode(VENTANA)
pygame.display.set_caption('Love Snake by Sandreke 💕')
FUENTE = pygame.font.Font("assets/LovelyFont.ttf", 36)
FUENTE_PEQUENA = pygame.font.Font("assets/LovelyFont.ttf", 24)

def crear_fondo():
    """Crea el fondo con patrón de tablero en tonos rosa"""
    fondo = pygame.Surface(VENTANA)
    for y in range(0, VENTANA[1], CUADRO):
        for x in range(0, VENTANA[0], CUADRO):
            pygame.draw.rect(fondo, 
                           ROSA_CLARO if (x + y) // CUADRO % 2 == 0 else ROSA_OSCURO, 
                           (x, y, CUADRO, CUADRO))
    return fondo

class ElementoBase:
    """Clase base para elementos del juego con funciones de dibujo comunes"""
    @staticmethod
    def dibujar_corazon(superficie, x, y, tamaño, color):
        """Dibuja un corazón con brillo"""
        puntos = [
            (x, y - tamaño//2), (x - tamaño, y - tamaño),
            (x - tamaño*1.5, y - tamaño//2), (x - tamaño, y),
            (x, y + tamaño), (x + tamaño, y),
            (x + tamaño*1.5, y - tamaño//2), (x + tamaño, y - tamaño)
        ]
        pygame.draw.polygon(superficie, color, puntos)
        pygame.draw.circle(superficie, BLANCO, (x - tamaño//2, y - tamaño//2), tamaño//4)

class PopupBase(ElementoBase):
    """Clase base para popups con fondo semi-transparente y decoraciones"""
    def __init__(self, ancho, alto):
        self.rect = pygame.Rect((VENTANA[0] - ancho)//2, (VENTANA[1] - alto)//2, ancho, alto)
        
    def dibujar_serpiente(self, superficie, x, y, tamaño):
        """Dibuja una serpiente decorativa con ojos de corazón y sonrisa"""
        pygame.draw.circle(superficie, VERDE, (x, y), tamaño)
        pygame.draw.circle(superficie, VERDE_OSCURO, (x, y), tamaño-5)
        
        # Ojos de corazón
        for dx in [-tamaño//2, tamaño//2]:
            self.dibujar_corazon(superficie, x + dx, y - tamaño//4, tamaño//4, ROJO)
        
        # Sonrisa feliz
        pygame.draw.arc(superficie, BLANCO, 
                       pygame.Rect(x - tamaño//2, y, tamaño, tamaño//2), 
                       math.pi, 2*math.pi, 3)
        # Hoyuelos
        for dx in [-tamaño//2, tamaño//2]:
            pygame.draw.circle(superficie, BLANCO, (int(x + dx), int(y + tamaño//4)), 3)

    def dibujar_fondo(self, superficie):
        """Dibuja el fondo del popup con esquinas redondeadas"""
        # Overlay semi-transparente
        overlay = pygame.Surface(VENTANA, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        superficie.blit(overlay, (0, 0))
        
        # Sombra y fondo del popup
        for offset, color in [(5, (0, 0, 0, 128)), (0, ROSA_TRANS)]:
            rect = self.rect.copy()
            rect.x += offset
            rect.y += offset
            pygame.draw.rect(superficie, color, rect, border_radius=20)
        
        # Decoraciones
        self.dibujar_serpiente(superficie, 
                             self.rect.x + self.rect.width//3,
                             self.rect.y + 70, 30)
        
        # Corazón flotante
        offset = math.sin(pygame.time.get_ticks() * 0.004) * 5
        self.dibujar_corazon(superficie,
                            self.rect.x + self.rect.width*2//3,
                            self.rect.y + 70 + offset, 25, ROJO)

class Boton:
    """Botón con efecto hover y esquinas redondeadas"""
    def __init__(self, x, y, ancho, alto, texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.hover = False
        
    def dibujar(self, superficie):
        color_fondo = BLANCO if self.hover else NEGRO
        color_texto = NEGRO if self.hover else BLANCO
        pygame.draw.rect(superficie, color_fondo, self.rect, border_radius=10)
        texto = FUENTE_PEQUENA.render(self.texto, True, color_texto)
        texto_rect = texto.get_rect(center=self.rect.center)
        superficie.blit(texto, texto_rect)
        
    def actualizar(self, evento):
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
        return self.hover and evento.type == pygame.MOUSEBUTTONDOWN

class PopupGameOver(PopupBase):
    """Popup de fin de juego con puntuación y botón de reinicio"""
    def __init__(self, puntos):
        super().__init__(400, 300)
        self.puntos = puntos
        self.boton = Boton(self.rect.x + 100, self.rect.y + 220, 200, 50, "Jugar de nuevo")
        
    def dibujar(self, superficie):
        self.dibujar_fondo(superficie)
        texto = FUENTE.render(f"¡Te ganaste {self.puntos} besos!", True, BLANCO)
        texto_rect = texto.get_rect(center=(VENTANA[0]//2, self.rect.y + 160))
        superficie.blit(texto, texto_rect)
        self.boton.dibujar(superficie)
        
    def actualizar(self, evento):
        return self.boton.actualizar(evento)

class PopupPausa(PopupBase):
    """Popup de pausa con instrucciones"""
    def __init__(self):
        super().__init__(400, 200)
        
    def dibujar(self, superficie):
        self.dibujar_fondo(superficie)
        for i, texto in enumerate(["Pausa", "Presiona ESC para continuar"]):
            fuente = FUENTE if i == 0 else FUENTE_PEQUENA
            superficie.blit(fuente.render(texto, True, BLANCO),
                          fuente.render(texto, True, BLANCO).get_rect(
                              center=(VENTANA[0]//2, self.rect.y + 140 + i*30)))

class Obstaculo:
    """Obstáculo con efecto 3D"""
    def __init__(self, pos):
        self.pos = pos
        
    def dibujar(self, superficie):
        x, y = self.pos[0] * CUADRO, self.pos[1] * CUADRO
        # Cuerpo principal
        pygame.draw.polygon(superficie, MARRON, [
            (x, y + CUADRO), (x, y),
            (x + CUADRO, y), (x + CUADRO, y + CUADRO)
        ])
        # Efecto 3D
        pygame.draw.polygon(superficie, 
                          tuple(max(0, c-30) for c in MARRON), [
            (x + 5, y + 5), (x + CUADRO - 5, y + 5),
            (x + CUADRO - 5, y + CUADRO - 5), (x + 5, y + CUADRO - 5)
        ])

class Comida(ElementoBase):
    """Comida en forma de corazón con animación flotante"""
    def __init__(self):
        self.pos = (0, 0)
        self.randomizar()
        
    def randomizar(self):
        self.pos = (random.randint(0, GRID[0]-1), random.randint(0, GRID[1]-1))
        
    def dibujar(self, superficie):
        x, y = self.pos
        offset = math.sin(pygame.time.get_ticks() * 0.004) * 5
        for color, dy in [(ROJO_OSCURO, 5), (ROJO, 0)]:
            self.dibujar_corazon(superficie,
                               x * CUADRO + CUADRO//2,
                               y * CUADRO + CUADRO//2 + offset + dy,
                               CUADRO//3, color)

class Serpiente:
    """Serpiente con ojos de corazón y lengua animada"""
    def __init__(self):
        self.reiniciar()
        
    def reiniciar(self):
        self.pos = [(GRID[0]//2, GRID[1]//2)]
        self.dir = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.puntos = 0
        self.creciendo = False
        self.tiempo_lengua = 0
        self.lengua_fuera = False
        
    def cerca_comida(self, comida_pos):
        dx = self.pos[0][0] - comida_pos[0]
        dy = self.pos[0][1] - comida_pos[1]
        return (dx*dx + dy*dy) < 9
    
    def actualizar(self):
        # Animación de lengua
        self.tiempo_lengua += 1
        if self.tiempo_lengua > 60:
            self.lengua_fuera = not self.lengua_fuera
            self.tiempo_lengua = 0
            
        # Movimiento
        nuevo = ((self.pos[0][0] + self.dir[0]) % GRID[0],
                (self.pos[0][1] + self.dir[1]) % GRID[1])
        
        if nuevo in self.pos[2:]:
            return False
            
        self.pos.insert(0, nuevo)
        if not self.creciendo:
            self.pos.pop()
        self.creciendo = False
        return True
    
    def dibujar_ojo(self, superficie, x, y, tamaño):
        """Dibuja un ojo en forma de corazón"""
        puntos = [
            (x, y - tamaño//2), (x - tamaño//2, y - tamaño),
            (x - tamaño, y - tamaño//2), (x - tamaño//2, y),
            (x, y + tamaño//2), (x + tamaño//2, y),
            (x + tamaño, y - tamaño//2), (x + tamaño//2, y - tamaño)
        ]
        pygame.draw.polygon(superficie, ROJO, puntos)
        pygame.draw.circle(superficie, BLANCO, (int(x - tamaño//4), int(y - tamaño//4)),
                           tamaño//4)
    
    def dibujar_lengua(self, superficie, inicio, direccion):
        """Dibuja la lengua con animación"""
        if not self.lengua_fuera:
            return
            
        fin = (inicio[0] + direccion[0]*12, inicio[1] + direccion[1]*12)
        bifurcacion = [(fin[0] + d*6, fin[1] + d*6) for d in [-1, 1]]
        
        pygame.draw.line(superficie, ROJO, inicio, fin, 3)
        for b in bifurcacion:
            pygame.draw.line(superficie, ROJO, fin, b, 3)
    
    def dibujar(self, superficie, comida_pos):
        """Dibuja la serpiente con todos sus detalles"""
        cerca_comida = self.cerca_comida(comida_pos)
        
        for i, p in enumerate(self.pos):
            x, y = p[0] * CUADRO, p[1] * CUADRO
            centro = (x + CUADRO//2, y + CUADRO//2)
            
            if i == 0:  # Cabeza
                pygame.draw.circle(superficie, VERDE, centro, CUADRO//2)
                
                # Ojos
                ojo_tamaño = 8
                dx = CUADRO*2//3 if self.dir[0] >= 0 else CUADRO//3
                for dy in [CUADRO//3, CUADRO*2//3]:
                    self.dibujar_ojo(superficie, x + dx, y + dy, ojo_tamaño)
                
                # Lengua
                if cerca_comida or self.lengua_fuera:
                    pos_lengua = {
                        (1, 0): (x + CUADRO, y + CUADRO//2),
                        (-1, 0): (x, y + CUADRO//2),
                        (0, -1): (x + CUADRO//2, y),
                        (0, 1): (x + CUADRO//2, y + CUADRO)
                    }
                    self.dibujar_lengua(superficie, pos_lengua[self.dir], self.dir)
            else:  # Cuerpo
                pygame.draw.circle(superficie, VERDE, centro, CUADRO//2)
                pygame.draw.circle(superficie, VERDE_OSCURO, centro, CUADRO//3)

class Juego:
    """Controlador principal del juego"""
    def __init__(self):
        self.serpiente = Serpiente()
        self.comida = Comida()
        self.fondo = crear_fondo()
        self.obstaculos = []
        self.game_over = False
        self.pausado = False
        self.popup_game_over = None
        self.popup_pausa = PopupPausa()
        self.configurar_obstaculos()
        
    def configurar_obstaculos(self):
        """Configura los obstáculos según el puntaje"""
        self.obstaculos = []
        for _ in range(5 + self.serpiente.puntos // 5):
            while True:
                pos = (random.randint(0, GRID[0]-1), random.randint(0, GRID[1]-1))
                if (pos != self.serpiente.pos[0] and 
                    pos != self.comida.pos and 
                    pos not in [o.pos for o in self.obstaculos]):
                    self.obstaculos.append(Obstaculo(pos))
                    break
    
    def reiniciar(self):
        """Reinicia el estado del juego"""
        self.serpiente.reiniciar()
        self.comida.randomizar()
        self.game_over = False
        self.popup_game_over = None
        self.configurar_obstaculos()
    
    def manejar_eventos(self):
        """Maneja los eventos de teclado y ratón"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
                
            if evento.type == pygame.KEYDOWN and not self.game_over:
                if evento.key == pygame.K_ESCAPE:
                    self.pausado = not self.pausado
                elif not self.pausado:
                    nuevas_dir = {
                        pygame.K_UP: (0, -1),
                        pygame.K_DOWN: (0, 1),
                        pygame.K_LEFT: (-1, 0),
                        pygame.K_RIGHT: (1, 0)
                    }
                    if evento.key in nuevas_dir:
                        nueva = nuevas_dir[evento.key]
                        if (-nueva[0], -nueva[1]) != self.serpiente.dir:
                            self.serpiente.dir = nueva
                            
            if self.game_over and self.popup_game_over:
                if self.popup_game_over.actualizar(evento):
                    self.reiniciar()
                    
        return True
    
    def actualizar(self):
        """Actualiza el estado del juego"""
        if self.pausado or self.game_over:
            return
            
        if not self.serpiente.actualizar() or any(o.pos == self.serpiente.pos[0]
                                                  for o in self.obstaculos):
            self.game_over = True
            self.popup_game_over = PopupGameOver(self.serpiente.puntos)
            return
            
        if self.serpiente.pos[0] == self.comida.pos:
            self.serpiente.creciendo = True
            self.serpiente.puntos += 1
            self.comida.randomizar()
            while any(o.pos == self.comida.pos for o in self.obstaculos):
                self.comida.randomizar()
            if self.serpiente.puntos % 5 == 0:
                self.configurar_obstaculos()
    
    def dibujar(self):
        """Dibuja todos los elementos del juego"""
        pantalla.blit(self.fondo, (0, 0))
        
        # Elementos del juego
        for obs in self.obstaculos:
            obs.dibujar(pantalla)
        self.serpiente.dibujar(pantalla, self.comida.pos)
        self.comida.dibujar(pantalla)
        
        # Puntuación
        texto = FUENTE.render(f'Score: {self.serpiente.puntos}', True, BLANCO)
        sombra = FUENTE.render(f'Score: {self.serpiente.puntos}', True, NEGRO)
        pantalla.blit(sombra, (12, 12))
        pantalla.blit(texto, (10, 10))
        
        # Popups
        if self.game_over and self.popup_game_over:
            self.popup_game_over.dibujar(pantalla)
        if self.pausado:
            self.popup_pausa.dibujar(pantalla)
        
        pygame.display.update()
    
    def ejecutar(self):
        """Bucle principal del juego"""
        reloj = pygame.time.Clock()
        while True:
            if not self.manejar_eventos():
                break
            self.actualizar()
            self.dibujar()
            reloj.tick(10)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Juego().ejecutar()