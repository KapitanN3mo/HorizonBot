import random
from typing import List, Any

import disnake


class RaidType:
    pass


class World:
    daily_raids: List[RaidType] = []
    weather = 'clear'
    available_weather = {
        'clear': 4, 'rain': 3, 'cloudy': 4, 'eclipse': 1, 'energy_storm': 1
    }
    current_weather = 'clear'
    rus_translation = {'clear': 'ясно',
                       'rain': 'дождь',
                       'cloudy': 'облачно'}

    @classmethod
    def update_weather(cls):
        all_variants = []
        for var, count in cls.available_weather.items():
            [all_variants.append(var) for i in range(int(count))]
        selected = random.choice(all_variants)
        if selected == cls.current_weather:
            cls.current_weather = selected
            return None
        else:
            cls.current_weather = selected
            return selected

    @classmethod
    def gen_weather_embed(cls):
        emb = disnake.Embed(title='Погода изменилась',
                            colour=disnake.Colour(0x2930FF),
                            description=f'Текущая погода: {cls.current_weather}', )
        emb.set_image()
