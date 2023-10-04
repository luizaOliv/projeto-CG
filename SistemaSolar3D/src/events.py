import math
import pygame
import OpenGL.GL as gl


def handle(last_pos):
    """
    Lida com eventos do pygame para mover e ampliar a câmera usando as setas do teclado e cliques do mouse

    """
    # Obtém as atividades do usuário, chamadas de eventos
    for event in pygame.event.get():
         # Sai se o usuário fechar a janela

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # Rotação com as setas do teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                gl.glRotatef(1, 0, 1, 0)
            if event.key == pygame.K_RIGHT:
                gl.glRotatef(1, 0, -1, 0)
            if event.key == pygame.K_UP:
                gl.glRotatef(1, -1, 0, 0)
            if event.key == pygame.K_DOWN:
                gl.glRotatef(1, 1, 0, 0)

        # Ampliar e reduzir com a roda do mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: 
                gl.glScaled(1.05, 1.05, 1.05)
            if event.button == 5:  
                gl.glScaled(0.95, 0.95, 0.95)

        # Rotacionar com clique do mouse e arrastar
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            dx = x - last_pos["x"]
            dy = y - last_pos["y"]
            mouseState = pygame.mouse.get_pressed()

            if mouseState[0]: # Botão esquerdo pressionado
                modelView = (gl.GLfloat * 16)()
                gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, modelView)

                   # Para combinar rotação nos eixos x e y
                temp = (gl.GLfloat * 3)()
                temp[0] = modelView[0]*dy + modelView[1]*dx
                temp[1] = modelView[4]*dy + modelView[5]*dx
                temp[2] = modelView[8]*dy + modelView[9]*dx
                norm_xy = math.sqrt(temp[0]*temp[0] + temp[1] * temp[1] + temp[2]*temp[2])

                if norm_xy != 0:
                    gl.glRotatef(math.sqrt(dx*dx+dy*dy), temp[0] / norm_xy, temp[1] / norm_xy, temp[2] / norm_xy)

            last_pos["x"] = x
            last_pos["y"] = y

    # Retorna a posição atualizada
    return last_pos
