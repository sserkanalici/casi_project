import mysql.connector
from bs4 import BeautifulSoup
from datetime import datetime

# MySQL bağlantısı
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="casibom_db"
)



# MySQL imleci
cursor = db.cursor()

# HTML dosyasını okuma ve çözümleme
def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Her bahis öğesini bulma
    bets = soup.find_all('div', class_='wlc-profile-bet-history-list__item')

    for bet in bets:
        try:
            # Bahis numarası
            bet_number_element = bet.find('div', class_='wlc-profile-bet-history-list__num')
            bet_number_element2 = bet_number_element.find('div', class_='wlc-profile-table__cell-content')
            bet_no = bet_number_element2.text.strip() if bet_number_element else '0'
            cleaned_bet_no = bet_no.replace('#', '')

            # Bahis saati
            bet_time_element = bet.find('div', class_='wlc-profile-bet-history-list__time')

            bet_time_element2 = bet_time_element.find('span')
            bet_time = bet_time_element2.text.strip() if bet_time_element else '00.00.0000 00:00:00'
            bet_time2 = datetime.strptime(bet_time, "%d.%m.%Y %H:%M:%S")
            bet_time3 = bet_time2.strftime("%Y-%m-%d %H:%M:%S")

            # # Miktar
            # amount_int_element = bet.find('span', class_='wlc-amount__amount--int')
            # amount_minus_element = bet.find('span', class_='wlc-amount__minus')
            # amount_decimal_element = bet.find('span', class_='wlc-amount__amount--decimal')
            # amount_int = amount_int_element.text.strip() if amount_int_element else '0'
            # amount_decimal = amount_decimal_element.text.strip() if amount_decimal_element else '0'
            
            # # 'amount_int' ve 'amount_decimal' değerlerini birleştirme
            # if ',' in amount_decimal:
            #     amount = float(amount_int.replace('.', '') + amount_decimal.replace(',', '.'))
            # else:
            #     amount = float(amount_int.replace('.', '') + '.' + amount_decimal)

            amount_int_element = bet.find('span', class_='wlc-amount__amount--int')
            amount_minus_element = bet.find('span', class_='wlc-amount__minus')
            amount_decimal_element = bet.find('span', class_='wlc-amount__amount--decimal')

            amount_int = amount_int_element.text.strip() if amount_int_element else '0'
            amount_decimal = amount_decimal_element.text.strip() if amount_decimal_element else '0'
            amount_minus = amount_minus_element.text.strip() if amount_minus_element else ''

            # 'amount_int' ve 'amount_decimal' değerlerini birleştirme
            if ',' in amount_decimal:
                amount = float(amount_int.replace('.', '') + amount_decimal.replace(',', '.'))
            else:
                amount = float(amount_int.replace('.', '') + '.' + amount_decimal)

            # Eğer '-' işareti varsa, miktarı negatif yap
            if amount_minus == '-':
                amount = -amount

            # Sağlayıcı
            provider_div = bet.find('div', class_='wlc-profile-table-merchant')
            if provider_div:
                provider_element = provider_div.find('span')
                provider = provider_element.text.strip() if provider_element else 'Bilinmiyor'
            else:
                provider = 'Bilinmiyor'

            # Oyun
            game_div = bet.find('div', class_='wlc-profile-bet-history-list__game')
            if game_div:
                game_element = game_div.find('span')
                game = game_element.text.strip() if game_element else 'Bilinmiyor'
            else:
                game = 'Bilinmiyor'

            # Verileri MySQL veri tabanına kaydetme
            cursor.execute('''
                INSERT INTO casi_uyg_bethistory2 (bet_number, bet_time, amount, provider, game)
                VALUES (%s, %s, %s, %s, %s)
            ''', (cleaned_bet_no, bet_time3, amount, provider, game))

            print(f"Kayıt eklendi: {cleaned_bet_no}, {bet_time3}, {amount}, {provider}, {game}")
        except ValueError as e:
            print(f"Veri alırken hata oluştu (ValueError): {e}")
        except AttributeError as e:
            print(f"Veri alırken hata oluştu (AttributeError): {e}")

    # Değişiklikleri kaydetme
    db.commit()

# HTML dosyasını analiz etme
#parse_html('demet/2.html')
parse_html('demet/24.07.2024_demet.html')

# Bağlantıyı kapatma
cursor.close()
db.close()
