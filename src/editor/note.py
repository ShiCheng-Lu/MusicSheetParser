# from common.label import Label, Bbox
# from common.music import TONE_MAP, display_duration
# import pygame

# pygame.font.init()
# font = pygame.font.Font('freesansbold.ttf', 20)
# NON_NOTE_LABELS = [
#     "restDoubleWhole",
#     "restWhole",
#     "restHalf",
#     "restQuarter",
#     "rest8th",
#     "rest16th",
#     "rest32nd",
#     "rest64th",
#     "rest128th",
# ]
# PITCH_MAP_LABEL = {
#     pitch : font.render(pitch, True, (25, 25, 255))
#     for pitch in TONE_MAP + NON_NOTE_LABELS
# }

# class Note(Label):
#     def __init__(self, bbox, name, duration):
#         super().__init__(bbox, name)
#         self.name = name
#         self.duration = duration
#         durationText = music.display_duration(duration) if 'rest' not in name else ''
#         self.text = font.render(f"{durationText}{name}", True, (25, 25, 255))

#         self.textRect = self.text.get_rect()
#         self.textRect.x = self.x_min
#         self.textRect.bottom = self.y_min
#         self.renderBox = Bbox(bbox)
#         self.renderColour = (25, 200, 25)
#         self.renderThickness = 3

#     def render(self, screen):
#         # draw box
#         xywh = [
#             self.renderBox.x_min, 
#             self.renderBox.y_min, 
#             self.renderBox.width + self.renderThickness, 
#             self.renderBox.height + self.renderThickness]
#         pygame.draw.rect(screen, self.renderColour, xywh, self.renderThickness)
#         # draw text
#         screen.blit(self.text, self.textRect)
    
#     def update(self, name, duration):
#         self.duration = duration
#         self.name = name
#         durationText = music.display_duration(duration) if 'rest' not in name else ''
#         self.text = font.render(f"{durationText}{name}", True, (25, 25, 255))
    
#     def updatePos(self, x, y, scale):
#         self.renderBox.bbox = [
#             self.x_min * scale + x,
#             self.y_min * scale + y,
#             self.x_max * scale + x,
#             self.y_max * scale + y,
#         ]
#         self.textRect.x = self.renderBox.x_min
#         self.textRect.bottom = self.renderBox.y_min