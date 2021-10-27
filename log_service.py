import logging

logger = logging.getLogger('LOG_SERVICE')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('bot.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info('Лог-сервис успешно запущен!')
