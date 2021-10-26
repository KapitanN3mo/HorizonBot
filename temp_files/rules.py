import json
import main
rules = [json.dumps({'title': '1. Каждый участник сервера обязан:', 'text': '''1.1 Знать и соблюдать правила сервера и правила проекта; 
1.2 Не допускать внутри серверных конфликтов; 
1.3 Заботиться о репутации сервера; 
1.4 Быть активным участником.
''', 'color': '0xFFFFFF', 'author': 'False'}), json.dumps({'title': '2. Участнику сервера запрещается:', 'text': '''2.1 - Разглашать внутреннюю информацию сервера;
2.2 - Разглашать личную информацию и переписки с участниками сервера без их ведома;
2.3 - Оскорблять участников по любому поводу;
2.4 - Использовать мат;
2.5 - Отправлять NSFW-контент в текстовые каналы, не предназначенные для этого;
2.6 - Устраивать конфликты;
2.7 - Присваивать права и обязанности Администрации сервера, если участник не входит в её состав;
2.8 - Писать где-либо от имени сервера, если участник не является Администратором;
2.9 - Отмечать участников сервера через "everyone" без позволения Администрации;
2.10 - Без разумных причин голосовать за изгнание участника сервера;
2.11 - Любыми действиями портить репутацию сервера.
''', 'color': '0xFFFFFF', 'author': 'False'}), json.dumps({'title': '3. Участник сервера имеет право:', 'text': '''3.1 Вступать в другие сервера организаций;
3.2 Оказывать какую-либо помощь любому из участников;
3.3 Приглашать людей из своего круга общения;
3.4 Предлагать изменения сервера и события Администрации.
''', 'color': '0xFFFFFF', 'author': 'False'}),
         json.dumps({'title': '4. Вступление на сервер:', 'text': '''4.1 Участником сервера может стать любой участник, прочитавший и согласившийся с правилами сервера; 
4.2 Заявка на вступление одобряется при ознакомлении с правилами и их принятии. Так же Администрация имеет право выгнать участника без объяснения причин. 
''', 'color': '0xFFFFFF', 'author': 'False'}),
         json.dumps({'title': '5. Исключение и наказание: ', 'text': '''5.1 Любой участник сервера вправе требовать о 
         наказании или исключении из сервера любого другого участника, который: 
         - не выполняет в полной мере свои обязанности; 
         - своими действиями (бездействием) делает невозможной успешную деятельность сервера или существенно её затрудняет; 
         - портит взаимоотношения с участниками; 
         - нарушает настоящие Правила сервера; 
         - оскорбляет участников в грубой форме. 
         5.2 - Решение об исключении из сервера принимается Администрацией. 
         5.3 - Наказание может варьироваться от мута в голосовом канале до пожизненного бана на сервере. При нарушении 
         правил дважды, участнику выдается предупреждение. На третий раз система автоматически банит его на 
         пожизненный срок.''', 'color': '0xFFFFFF', 'author': 'False'}),
         json.dumps({'title': '6. Изменения или внесения в правила дополнений:',
                     'text': '''Правом изменения или внесения в устав дополнений обладает только Администрация.''',
                     'color': '0xFFFFFF', 'author': 'False'})]
