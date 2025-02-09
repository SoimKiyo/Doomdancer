import pygame

# Si le mixer n'est pas encore initialisé, on l'initialise
if not pygame.mixer.get_init():
    pygame.mixer.init()

# Chargement des effets sonores
# Joueur
attack_sound = pygame.mixer.Sound("assets/audio/sfx/player/attack/player_attack.wav")
attackvoice_sound1 = pygame.mixer.Sound("assets/audio/sfx/player/attack/player_attack1.wav")
attackvoice_sound2 = pygame.mixer.Sound("assets/audio/sfx/player/attack/player_attack2.wav")
attackvoice_sound3 = pygame.mixer.Sound("assets/audio/sfx/player/attack/player_attack3.wav")
damage_sound = pygame.mixer.Sound("assets/audio/sfx/player/damage/player_hit.wav")
damagevoice_sound1 = pygame.mixer.Sound("assets/audio/sfx/player/damage/player_damage1.wav")
damagevoice_sound2 = pygame.mixer.Sound("assets/audio/sfx/player/damage/player_damage2.wav")
damagevoice_sound3 = pygame.mixer.Sound("assets/audio/sfx/player/damage/player_damage3.wav")
death_sound = pygame.mixer.Sound("assets/audio/sfx/player/death/player_death.wav")
moveonrock_sound = pygame.mixer.Sound("assets/audio/sfx/player/move/player_rock.wav")
moveongrass_sound = pygame.mixer.Sound("assets/audio/sfx/player/move/player_grass.wav")
dash_sound = pygame.mixer.Sound("assets/audio/sfx/player/move/player_dash.wav")
collect_sound = pygame.mixer.Sound("assets/audio/sfx/player/player_collect.wav")

# Arme
shoot_sound = pygame.mixer.Sound("assets/audio/sfx/weapons/weapon_shoot.wav")
reload_sound = pygame.mixer.Sound("assets/audio/sfx/weapons/weapon_reload.wav")

# Enemie
enemydeath_sound = pygame.mixer.Sound("assets/audio/sfx/enemy/enemy_death.wav")

# Jeu
gameend_sound = pygame.mixer.Sound("assets/audio/sfx/game/game_end.wav")
gamestart_sound = pygame.mixer.Sound("assets/audio/sfx/game/game_start.wav")
levelchange_sound = pygame.mixer.Sound("assets/audio/sfx/game/level_change.wav")
levelclear_sound = pygame.mixer.Sound("assets/audio/sfx/game/level_clear.wav")

# UI
menuback_sound = pygame.mixer.Sound("assets/audio/sfx/ui/menu_back.wav")
menuconfirm_sound = pygame.mixer.Sound("assets/audio/sfx/ui/menu_confirm.wav")
menuup_sound = pygame.mixer.Sound("assets/audio/sfx/ui/menu_up.wav")
menudown_sound = pygame.mixer.Sound("assets/audio/sfx/ui/menu_down.wav")
powerup_sound = pygame.mixer.Sound("assets/audio/sfx/ui/menu_powerup.wav")
dialog_sound = pygame.mixer.Sound("assets/audio/sfx/ui/dialog_text.wav")

# Cinematic
scene1_sound = pygame.mixer.Sound("assets/audio/sfx/cinematic/scene1.mp3")
scene2_sound = pygame.mixer.Sound("assets/audio/sfx/cinematic/scene2.mp3")
scene3_sound = pygame.mixer.Sound("assets/audio/sfx/cinematic/scene3.mp3")
scene4_sound = pygame.mixer.Sound("assets/audio/sfx/cinematic/scene4.mp3")
scene5_sound = pygame.mixer.Sound("assets/audio/sfx/cinematic/scene5.mp3")

def set_volume_all(volume):
    """
    Met à jour le volume de tous les effets sonores.
    La valeur volume doit être comprise entre 0.0 et 1.0.
    """
    # Joueur
    attack_sound.set_volume(volume)
    attackvoice_sound1.set_volume(volume)
    attackvoice_sound2.set_volume(volume)
    attackvoice_sound3.set_volume(volume)
    damage_sound.set_volume(volume)
    damagevoice_sound1.set_volume(volume)
    damagevoice_sound2.set_volume(volume)
    damagevoice_sound3.set_volume(volume)
    death_sound.set_volume(volume)
    moveonrock_sound.set_volume(volume)
    moveongrass_sound.set_volume(volume)
    dash_sound.set_volume(volume)
    collect_sound.set_volume(volume)

    # Arme
    shoot_sound.set_volume(volume)
    reload_sound.set_volume(volume)

    # Enemie
    enemydeath_sound.set_volume(volume)

    # Jeu
    gameend_sound.set_volume(volume)
    gamestart_sound.set_volume(volume)
    levelchange_sound.set_volume(volume)
    levelclear_sound.set_volume(volume)

    # UI
    menuback_sound.set_volume(volume)
    menuconfirm_sound.set_volume(volume)
    menuup_sound.set_volume(volume)
    menudown_sound.set_volume(volume)
    powerup_sound.set_volume(volume)
    dialog_sound.set_volume(volume)

    # Cinematic
    scene1_sound.set_volume(volume)
    scene2_sound.set_volume(volume)
    scene3_sound.set_volume(volume)
    scene4_sound.set_volume(volume)
    scene5_sound.set_volume(volume)