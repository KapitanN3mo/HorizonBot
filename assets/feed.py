class Feed:
    feeds = []

    def __init__(self, name, emoji, f_id):
        self.name = name
        self.emoji = emoji
        self.id = f_id
        self.feeds.append(self)

    @classmethod
    def get_feeds(cls):
        return cls.feeds

    @classmethod
    def get_feed_by_id(cls, feed_id):
        for feed in cls.feeds:
            if feed.id == feed_id:
                print(feed)
                return feed


pizza = Feed('Пицца', '🍕', 'pizza')
soup = Feed('Суп', '🍲', 'soup')
hamburger = Feed('Гамбургер', '🍔', 'hamburger')
hot_dog = Feed('Хот-дог', '🌭', 'hot_dog')
strawberry = Feed('Клубника', '🍓', 'strawberry')
cherry = Feed('Вишня', '🍒', 'cherry')
pear = Feed('Груша', '🍐', 'pear')
apple = Feed('Яблоко', '🍎', 'apple')
banana = Feed('Банан', '🍌', 'banana')
meat = Feed('Окорок', '🍗', 'meat')
rice = Feed('Рис', '🍚', 'rice')
spaghetti = Feed('Спаггети', '🍝', 'spaghetti')
bread = Feed('Хлеб', '🍞', 'bread')
fri = Feed('Картошка Фри', '🍟', 'fri')
sushi = Feed('Суши', '🍣', 'sushi')
shrimp = Feed('Креветки', '🍤', 'shrimp')
ice_cream = Feed('Мороженное', '🍦', 'ice_cream')
fruit_ice = Feed('Фруктовый лёд', '🍧', 'fruit_ice')
donut = Feed('Пончик', '🍩', 'donut')
cookie = Feed('Печенье', '🍪', 'cookie')
chocolate = Feed('Шоколад', '🍫', 'chocolate')
sweets = Feed('Конфеты', '🍬', 'sweets')
custard = Feed('Заварной крем', '🍮', 'custard')
