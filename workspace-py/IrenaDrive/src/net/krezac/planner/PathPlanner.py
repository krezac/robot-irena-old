'''
Created on Jun 6, 2010

@author: krezac
'''
import sys, pygame, os


if __name__ == '__main__':
    pygame.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,20'
    size = width, height = 1300, 745
    screen = pygame.display.set_mode(size, pygame.NOFRAME)
    map = pygame.image.load("rkpark.png")
    map.set_alpha(120)
    maprect = map.get_rect()
    while 1:
        #pygame.time.wait(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q or event.key == pygame.K_SPACE:
                    #robbusThread.requestTermination()
                    #robbusThread.join(2)
                    sys.exit()
            screen.fill(pygame.Color('white'))
            screen.blit(map, maprect)
            pygame.display.flip()