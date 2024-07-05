import time

class CooldownManager:
    def __init__(self, cooldown_time):
        self.cooldown_time = cooldown_time
        self.user_last_download_time = {}

    def is_on_cooldown(self, user_id):
        current_time = time.time()
        if user_id in self.user_last_download_time:
            last_time = self.user_last_download_time[user_id]
            if current_time - last_time < self.cooldown_time:
                return True
        self.user_last_download_time[user_id] = current_time
        return False

cooldown_manager = CooldownManager(cooldown_time=60)
