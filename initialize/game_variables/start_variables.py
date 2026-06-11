class GameVariables:
    def __init__(self):
        self.placing_turrets = False
        self.selected_turret = None
        self.current_turret_type = None
        
        # Health system
        self.computer_health = 100
        self.max_health = 100
        
        # Currency system
        self.player_currency = 200

    def take_damage(self, amount):
        self.computer_health = max(0, self.computer_health - amount)
