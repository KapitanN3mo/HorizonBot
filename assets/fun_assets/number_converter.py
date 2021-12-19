def convert_number_to_emoji(number: int):
    num_emoji = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣',
                 9: '9️⃣'}
    if number in num_emoji:
        return num_emoji[number]
    else:
        return None