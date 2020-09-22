import sys
sys.path.insert(0, '~/Documents/alienInvasionAI/lib')
from time import sleep

import pygame

from src.ui.settings import Settings
from src.ui.game_stats import GameStats
from src.ui.scoreboard import Scoreboard
from src.ui.elements.button import Button
from src.gameObjects.ship import Ship
from src.gameObjects.bullet import Bullet
from src.gameObjects.alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initiate the game and create game resources."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width 
        self.settings.screen_height = self.screen.get_rect().height 
        pygame.display.set_caption("Alien Invasion")
        pygame.mouse.set_visible(False)

        # Create an instance to store game statistics,
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Make the play button.
        self.play_button = Button(self, "Press P to play")

        # Difficulty buttons
        self.easy_button = Button(self, "1 - Easy")
        self.medium_button = Button(self, "2- Medium")
        self.hard_button = Button(self, "3 - Hard")
        self.impossible_button = Button(self, "4 - Impossible")

        self.easy_button.rect.topleft = self.easy_button.screen_rect.topleft
        self.easy_button.msg_image_rect.center = self.easy_button.rect.center

        self.medium_button.rect.topleft = self.easy_button.rect.bottomleft
        self.medium_button.msg_image_rect.center = self.medium_button.rect.center

        self.hard_button.rect.topleft = self.medium_button.rect.bottomleft
        self.hard_button.msg_image_rect.center = self.hard_button.rect.center

        self.impossible_button.rect.topleft = self.hard_button.rect.bottomleft
        self.impossible_button.msg_image_rect.center = self.impossible_button.rect.center


    # Main loop
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    # User input
    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
               self._check_keyup_events(event)

    def _check_play_button(self):
        """Start a new game when the player clicks Play."""
        if not self.stats.game_active:
            # Reset game settings and score
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

    def _choose_difficulty(self, difficulty):
        if difficulty == "easy" and not self.stats.game_active:
            self.settings.easy()
        if difficulty == "medium" and not self.stats.game_active:
            self.settings.medium()
        if difficulty == "hard" and not self.stats.game_active:
            self.settings.hard()
        if difficulty == "impossible" and not self.stats.game_active:
            self.settings.impossible()

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

        elif event.key == pygame.K_p:
            sleep(0.5)
            self._check_play_button()

        elif event.key == pygame.K_1:
            self._choose_difficulty("easy")

        elif event.key == pygame.K_2:
            self._choose_difficulty("medium")

        elif event.key == pygame.K_3:
            self._choose_difficulty("hard")

        elif event.key == pygame.K_4:
            self._choose_difficulty("impossible")


        elif event.key == pygame.K_ESCAPE:
            sys.exit()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    # Bullets
    def _fire_bullet(self):
        """Create a new bullet and add it to te bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of the bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_colision()

        # Repopulating the fleet
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _check_bullet_alien_colision(self):
        """Check for any bullets that have hit aliens.
        If so, get rid of the bullet and the alien."""
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for alien in collisions.values():
                self.stats.score += self.settings.alien_score * len(alien)
                self.sb.prep_score()
                self.sb.check_high_score()


    def _check_alien_ship_collision(self):
        """Check for alien-ship collision."""
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

    def _ship_hit(self):
        """Respond to a ship being hit by an alien.."""
        if self.stats.ships_left > 1:

            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship.
            if self.settings.fleet_direction < 0:
                self.settings.fleet_direction *= -1
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else: 
            self.stats.game_active = False

    def _check_aliens_bottom(self):
        """ Check if an alien has reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same way has if the ship got hit.
                self._ship_hit()
                break
    # Aliens

    def _update_aliens(self):
        """Respond to bullet-alien collisions,"""
        # Remove any bullets and aliens that have collided. 
        # Creates a new fleet when the previous one is empty.
        self._check_fleet_edges()
        self.aliens.update()

        # Check for alien-ship collision.
        self._check_alien_ship_collision()

        # Check if an alien has reached the bottom of the screen.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Determine the number of alien in one row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
                                (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens. 
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        # Place alien in the right place within the row.
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        # Place alien in the right row.
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Responde appropriatly if any alens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    # Render screen
    def _update_screen(self):
        """ Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        if self.stats.game_active:
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw the scoreboard information.
        self.sb.show_score()

        # Draw the Play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.medium_button.draw_button()
            self.hard_button.draw_button()
            self.impossible_button.draw_button()

        pygame.display.flip()






        


# Start

if __name__ == '__main__':
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()