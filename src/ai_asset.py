# File: src/ai_asset.py
import os
import pygame

class DynamicAssetGenerator:
    """
    A simple AI agent to select dynamic background assets based on game parameters.
    """

    def __init__(self, asset_folder="assets/backgrounds"):
        self.asset_folder = asset_folder
        self.backgrounds = self.load_backgrounds()

    def load_backgrounds(self):
        """
        Loads all background image filenames from the asset folder.
        """
        files = []
        try:
            for file in os.listdir(self.asset_folder):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    files.append(file)
        except Exception as e:
            print("Error loading background assets:", e)
        return files

    def pick_background(self, game_params):
        """
        Selects a background based on game parameters.
        For this example, we'll use the player's score to choose the image.
        """
        score = game_params.get("score", 0)
        if self.backgrounds:
            # Simple algorithm: change background every 200 score units
            index = (score // 200) % len(self.backgrounds)
            selected = self.backgrounds[index]
            return os.path.join(self.asset_folder, selected)
        else:
            return None

    def load_background(self, game_params, screen_size=(800, 600)):
        """
        Loads and returns a pygame surface for the background image.
        """
        bg_file = self.pick_background(game_params)
        if bg_file and os.path.exists(bg_file):
            try:
                background_img = pygame.image.load(bg_file)
                # Scale the image to fit the screen
                background_img = pygame.transform.scale(background_img, screen_size)
                return background_img
            except Exception as e:
                print("Error loading background image:", bg_file, e)
                return None
        else:
            return None
