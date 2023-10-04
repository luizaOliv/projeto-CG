
import pygame
import math
import events
import texture
import file

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def main():
    pygame.init()
    start_window()

    # Permite pressionar e manter pressionados os botões
    pygame.key.set_repeat(1, 10)

    last_mouse_position = {
        "x": 0,
        "y": 0
    }

    system = SolarSystem()

    while True:
        last_mouse_position = events.handle(last_mouse_position)

        # Cria uma esfera e aplica uma textura
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        system.draw_sun()
        system.draw_orbs()
        system.draw_lines()

        # Exibe a janela pygame
        pygame.display.flip()
        # Aguarda um determinado tempo para renderizar aproximadamente 60 frames por segundo (1 segundo / 60 frames = 1 frame a cada 0.016 segundos)
        # Geralmente atinge pelo menos 30 fps
        pygame.time.delay(16)


def start_window():
    """
    Inicia a janela com configurações padrão
    """
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    # Define o título da janela
    pygame.display.set_caption('Solar System')
    # Define o ícone da janela
    pygame_icon = pygame.image.load(file.resolve('icon.ico'))
    pygame.display.set_icon(pygame_icon)

    # Variáveis de distância do espectador ao plano de recorte
    NEAR_RENDERING_DISTANCE = 20
    FAR_RENDERING_DISTANCE = 400
    gluPerspective(
        40,
        (display[0]/display[1]),
        NEAR_RENDERING_DISTANCE,
        FAR_RENDERING_DISTANCE
    )


class OrbRotation:
    def __init__(self, speed):
        self.current = 0
        self.speed = speed


class OrbPosition:
    def __init__(self, sun_distance, speed):
        self.radius = sun_distance
        self.angle = 0

        self.current_x = 0
        self.current_y = 0

        self.speed = speed

    def update(self):
        if self.radius is None:
            return

        # Obtém o radiano pela nova posição desejada do ângulo
        radians = math.radians(self.angle)

        # Define a nova posição usando o ângulo e o seno/cosseno
        self.current_x = math.cos(radians) * self.radius
        self.current_y = math.sin(radians) * self.radius


class Orb:
    def __init__(self, rotation_speed, sun_distance, movement_speed, scale, texture_name):
        self.rotation = OrbRotation(rotation_speed)
        self.position = OrbPosition(sun_distance, movement_speed)

        self.scale = scale

        self.texture_id = texture.read(texture_name)

    def create_line(self, index):
        """
        Cria uma "função estática" (na verdade uma lista de instruções) que é compilada (por questões de desempenho),
        para o desenho da linha de movimento translacional do planeta

        """
        glNewList(index + 1, GL_COMPILE)
        glDisable(GL_LIGHTING)
        glColor3f(0.1, 0.1, 0.2)
        glBegin(GL_POINTS)

        angle = 0

        while angle <= 360:
            angle += 0.01
            radians = math.radians(angle)
            x = self.position.radius * math.cos(radians)
            y = self.position.radius * math.sin(radians)
            glVertex3f(x, y, 0.0)

        glEnd()
        glEnable(GL_LIGHTING)
        glEndList()

    def draw_line(self, index):
        """
        Chama a "função" de desenho da linha de movimento translacional         """
        glCallList(index + 1)

    def draw(self):
        """
        Cria uma esfera com textura e as modificações desejadas

        """
        # Escala o planeta para o tamanho desejado
        glScalef(self.scale, self.scale, self.scale)

        # Aplica a rotação no próprio eixo
        glRotatef(self.rotation.current, 0, 0, -1)

        # Aumenta a rotação para a próxima iteração usando a velocidade de rotação desejada
        self.rotation.current += self.rotation.speed
        # Se a rotação no próprio eixo estiver completa, reinicia a posição de rotação para zero
        if self.rotation.current >= 360:
            self.rotation.current = 0

        # Cria o objeto esfera e aplica a textura
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 1, 360, 180)
        gluDeleteQuadric(quadric)

        glDisable(GL_TEXTURE_2D)


class SolarSystem:
    def __init__(self):
        # Define o zoom inicial para que possamos ver o sol
        glTranslatef(0.0, 0.0, -100)

        self.start_light()

        # Inicia os planetas no sistema solar

        self.sun = Orb(0.037, None, None, 10, 'sun.jpg')
        self.orbs = [
            Orb(0.017, 35, 4.14, 0.38, 'mercury.jpg'),
            Orb(0.004, 45, 1.62, 0.94, 'venus.jpg'),
            Orb(1, 55, 1, 1, 'earth.jpg'),
            Orb(0.96, 65, 0.53, 0.53, 'mars.jpg'),
            Orb(2.4, 95, 0.084, 2.72, 'jupiter.jpg'),
            Orb(2.18, 115, 0.033, 2.28, 'saturn.jpg'),
            Orb(1.41, 145, 0.011, 0.99, 'uranus.jpg'),
            Orb(1.5, 175, 0.006, 0.96, 'neptune.jpg'),
            Orb(0.16, 205, 0.004, 0.7, 'pluto.jpg') 
        ]

        for index, orb in enumerate(self.orbs):
            orb.create_line(index)

    def start_light(self):
     
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        # Luz do sol
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0, 0, 0, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [0.0, 0.0, 1.0])
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 0.0)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)

    def draw_sun(self):
        glPushMatrix()  

        glTranslatef(0, 0, 0)  

        glDisable(GL_LIGHTING)

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        self.sun.draw()

        glPopMatrix()  

        glEnable(GL_LIGHTING)

    def draw_orbs(self):
        """
        (Re)draws each orb on system with updated rotation and position
        """
        for orb in self.orbs:
            glPushMatrix()  

            orb.position.update()

            if orb.position.angle >= 360:  
                orb.position.angle = 0
            else:  
                orb.position.angle += orb.position.speed

            glTranslatef(orb.position.current_x, orb.position.current_y, 0)

          
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1, 1, 1, 1])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 1, 1, 1])
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0, 0, 0, 1])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100)

            # textura
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

            orb.draw()

            glPopMatrix()  
    def draw_lines(self):
        for index, orb in enumerate(self.orbs):
            orb.draw_line(index)


if __name__ == "__main__":
    main()
