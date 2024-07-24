from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from casi_uyg.models import BetHistory,BetHistory2
from django.db.models import Sum, F, Case, When, CharField, Value, FloatField, DecimalField, ExpressionWrapper,Func
from django.db.models.functions import TruncDate,ExtractWeekDay
from datetime import datetime,timedelta
from decimal import Decimal
from django.db import connection



def calculate_totals():
    # Veritabanındaki tüm kayıtları al
    records = BetHistory.objects.filter(bet_time__isnull=False)
    
    # Tarihlere göre gruplama yapma
    grouped_data = {}
    
    for record in records:
        tarih = record.bet_time.date()  # Sadece tarihi al
        if tarih not in grouped_data:
            grouped_data[tarih] = {'toplam_basilan_tutar': Decimal('0.00'), 'toplam_kazanc': Decimal('0.00')}
        
        if record.amount < 0:
            grouped_data[tarih]['toplam_basilan_tutar'] += abs(record.amount)
        else:
            grouped_data[tarih]['toplam_kazanc'] += record.amount
    
    # Kar/Zarar hesaplama
    result = []
    for tarih, values in grouped_data.items():
        toplam_basilan_tutar = values['toplam_basilan_tutar']
        toplam_kazanc = values['toplam_kazanc']
        kar_zarar = toplam_kazanc - toplam_basilan_tutar
        
        # Basılan tutarın %9'unu ekleme
        eklenmesi_gereken_miktar = toplam_basilan_tutar * Decimal('0.09')
        yeni_kar_zarar = kar_zarar + eklenmesi_gereken_miktar
        
        result.append({
            'tarih': tarih,
            'toplam_basilan_tutar': toplam_basilan_tutar,
            'toplam_kazanc': toplam_kazanc,
            'kar_zarar': yeni_kar_zarar
        })
    
    # Sonuçları tarihe göre azalan sırada sıralama (yeni tarihten eski tarihe doğru)
    result.sort(key=lambda x: x['tarih'], reverse=True)
    
    # Debug için sonuçları yazdır
    print("Sonuçlar:")
    for entry in result:
        print(entry)
    
    return result


def calculate_totals2():
    # Veritabanındaki tüm kayıtları al
    records = BetHistory2.objects.filter(bet_time__isnull=False)
    
    # Tarihlere göre gruplama yapma
    grouped_data = {}
    
    for record in records:
        tarih = record.bet_time.date()  # Sadece tarihi al
        if tarih not in grouped_data:
            grouped_data[tarih] = {'toplam_basilan_tutar': Decimal('0.00'), 'toplam_kazanc': Decimal('0.00')}
        
        if record.amount < 0:
            grouped_data[tarih]['toplam_basilan_tutar'] += abs(record.amount)
        else:
            grouped_data[tarih]['toplam_kazanc'] += record.amount
    
    # Kar/Zarar hesaplama
    result = []
    for tarih, values in grouped_data.items():
        toplam_basilan_tutar = values['toplam_basilan_tutar']
        toplam_kazanc = values['toplam_kazanc']
        kar_zarar = toplam_kazanc - toplam_basilan_tutar
        
        # Basılan tutarın %9'unu ekleme
        eklenmesi_gereken_miktar = toplam_basilan_tutar * Decimal('0.09')
        yeni_kar_zarar = kar_zarar + eklenmesi_gereken_miktar
        
        result.append({
            'tarih': tarih,
            'toplam_basilan_tutar': toplam_basilan_tutar,
            'toplam_kazanc': toplam_kazanc,
            'kar_zarar': yeni_kar_zarar
        })
    
    # Sonuçları tarihe göre azalan sırada sıralama (yeni tarihten eski tarihe doğru)
    result.sort(key=lambda x: x['tarih'], reverse=True)
    
    # Debug için sonuçları yazdır
    print("Sonuçlar:")
    for entry in result:
        print(entry)
    
    return result

def combine_totals():
    totals1 = calculate_totals()
    totals2 = calculate_totals2()
    
    combined_data = {}
    
    # Birinci toplamları işleme
    for entry in totals1:
        tarih = entry['tarih']
        if tarih not in combined_data:
            combined_data[tarih] = {'kar_zarar': Decimal('0.00')}
        combined_data[tarih]['kar_zarar'] += entry['kar_zarar']
    
    # İkinci toplamları işleme
    for entry in totals2:
        tarih = entry['tarih']
        if tarih not in combined_data:
            combined_data[tarih] = {'kar_zarar': Decimal('0.00')}
        combined_data[tarih]['kar_zarar'] += entry['kar_zarar']
    
    # Sonuçları tarihe göre azalan sırada sıralama (yeni tarihten eski tarihe doğru)
    combined_result = list(combined_data.items())
    combined_result.sort(key=lambda x: x[0], reverse=True)
    
    # Sonuçları formatlama
    final_result = []
    for tarih, values in combined_result:
        final_result.append({
            'tarih': tarih,
            'kar_zarar': values['kar_zarar']
        })
    
    # Debug için sonuçları yazdır
    print("Birleştirilmiş Sonuçlar:")
    for entry in final_result:
        print(entry)
    
    return final_result

def calculate_totals_in_range(start_date, end_date):
    records1 = BetHistory.objects.filter(bet_time__range=[start_date, end_date])
    records2 = BetHistory2.objects.filter(bet_time__range=[start_date, end_date])
    
    grouped_data = {}
    
    for records in [records1, records2]:
        for record in records:
            tarih = record.bet_time.date()
            if tarih not in grouped_data:
                grouped_data[tarih] = {
                    'toplam_basilan_tutar': Decimal('0.00'), 
                    'toplam_kazanc': Decimal('0.00')
                }
            
            if record.amount < 0:
                grouped_data[tarih]['toplam_basilan_tutar'] += abs(record.amount)
            else:
                grouped_data[tarih]['toplam_kazanc'] += record.amount
    
    result = []
    for tarih, values in grouped_data.items():
        toplam_basilan_tutar = values['toplam_basilan_tutar']
        toplam_kazanc = values['toplam_kazanc']
        
        # Toplam kazanca %9 bonus ekleme
        bonus = toplam_kazanc * Decimal('0.09')
        toplam_kazanc += bonus
        
        kar_zarar = toplam_kazanc - toplam_basilan_tutar
        
        result.append({
            'tarih': tarih,
            'kar_zarar': kar_zarar
        })
    
    # Sonuçları tarihe göre azalan sırada sıralama (yeni tarihten eski tarihe doğru)
    result.sort(key=lambda x: x['tarih'], reverse=True)
    
    return result

def index(request):
    totals = calculate_totals()
    totals2 = calculate_totals2()
    
    top_kar_zarar = combine_totals()
    
    # Başlangıç ve bitiş tarihlerini formdan alın (string olarak alıyoruz)
    start_date_str = request.GET.get('start_date', '2024-01-01')
    end_date_str = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # Tarihleri datetime.datetime formatına dönüştür
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # bitiş tarihi dahil değil
    except ValueError:
        # Tarih formatı geçersizse varsayılan tarihleri kullan
        start_date = datetime(2024, 1, 1)
        end_date = datetime.now()  # bitiş tarihi dahil değil

    # Tarih aralığında toplam kar/zararı hesaplama
    totals3 = calculate_totals_in_range(start_date, end_date + timedelta(days=1))
    
    # Gün sayısını hesaplama
    total_days = len(set(record['tarih'] for record in totals3))
    total_kar_zarar = sum(entry['kar_zarar'] for entry in totals3)*Decimal('1.09')


    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SUM(amount) AS Toplam_Kar
            FROM casi_uyg_bethistory;
        """)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names = [col[0] for col in cursor.description]
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SUM(amount) AS Toplam_Kar
            FROM casi_uyg_bethistory2;
        """)
        
        # Fetch all results
        results2 = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names2 = [col[0] for col in cursor.description]
    return render(request, 'index.html', {
        'veri': totals,
        'veri2': totals2,
        'toplam': top_kar_zarar,
        'total': total_kar_zarar,
        'total_days': total_days,
        'yunus_total':results,
        'column_names':column_names,
        'demet_total':results2,
        'column_names':column_names2
    })
   

def gunler(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CASE DAYOFWEEK(bet_time)
                    WHEN 1 THEN 'Pazartesi'
                    WHEN 2 THEN 'Salı'
                    WHEN 3 THEN 'Çarşamba'
                    WHEN 4 THEN 'Perşembe'
                    WHEN 5 THEN 'Cuma'
                    WHEN 6 THEN 'Cumartesi'
                    WHEN 7 THEN 'Pazar'
                END AS day_name,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bet,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_win,
                CASE 
                    WHEN SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) = 0 THEN 0
                    ELSE ((SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) /
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) * 100)
                END AS profit_loss_percentage
            FROM 
                casi_uyg_bethistory
            GROUP BY 
                day_name
            ORDER BY 
                profit_loss_percentage DESC;
        """)
        results = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]

    with connection.cursor() as cursor2:
            cursor2.execute("""
                SELECT 
                    CASE DAYOFWEEK(bet_time)
                        WHEN 1 THEN 'Pazartesi'
                        WHEN 2 THEN 'Salı'
                        WHEN 3 THEN 'Çarşamba'
                        WHEN 4 THEN 'Perşembe'
                        WHEN 5 THEN 'Cuma'
                        WHEN 6 THEN 'Cumartesi'
                        WHEN 7 THEN 'Pazar'
                    END AS day_name,
                    SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bet,
                    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_win,
                    CASE 
                        WHEN SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) = 0 THEN 0
                        ELSE ((SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                            SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) /
                            SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) * 100)
                    END AS profit_loss_percentage
                FROM 
                    casi_uyg_bethistory2
                GROUP BY 
                    day_name
                ORDER BY 
                    profit_loss_percentage DESC;
            """)
            results2 = cursor2.fetchall()
            column_names2 = [col[0] for col in cursor2.description]

        # Pass results to the template
        
    return render(request, 'gunler.html', {
        'results': results, 
        'column_names': column_names,
        'results2': results2, 
        'column_names2': column_names2,
    })

def oyunlar(request):
    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                game,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bet,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_win,
                CASE 
                    WHEN SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) = 0 THEN 0
                    ELSE ((SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) /
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) * 100)
                END AS profit_loss_percentage
            FROM 
                casi_uyg_bethistory
            GROUP BY 
                game
            ORDER BY 
                profit_loss_percentage DESC
        """)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names = [col[0] for col in cursor.description]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                game,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bet,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_win,
                CASE 
                    WHEN SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) = 0 THEN 0
                    ELSE ((SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) /
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) * 100)
                END AS profit_loss_percentage
            FROM 
                casi_uyg_bethistory2
            GROUP BY 
                game
            ORDER BY 
                profit_loss_percentage DESC
        """)
        
        # Fetch all results
        results2 = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names2 = [col[0] for col in cursor.description]


    # Render the results in the template
    return render(request, 'oyunlar.html', {
        'results': results, 
        'column_names': column_names,
        'results2': results2, 
        'column_names2': column_names2,

    })




def zaman(request):
    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                HOUR(bet_time) AS hour_of_day,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bet,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_win,
                CASE 
                    WHEN SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) = 0 THEN 0
                    ELSE ((SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) /
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) * 100)
                END AS profit_loss_percentage
            FROM 
                casi_uyg_bethistory
            GROUP BY 
                hour_of_day
            ORDER BY 
                profit_loss_percentage DESC;
        """)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names = [col[0] for col in cursor.description]
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                HOUR(bet_time) AS hour_of_day,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bet,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_win,
                CASE 
                    WHEN SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) = 0 THEN 0
                    ELSE ((SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) /
                           SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) * 100)
                END AS profit_loss_percentage
            FROM 
                casi_uyg_bethistory2
            GROUP BY 
                hour_of_day
            ORDER BY 
                profit_loss_percentage DESC;
        """)
        
        # Fetch all results
        results2 = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names2 = [col[0] for col in cursor.description]

    # Render the results in the template
    return render(request, 'zaman.html', {
        'results': results, 
        'column_names': column_names,
        'results2': results2, 
        'column_names2': column_names2,
    })


from django.shortcuts import render
from django.db import connection

def bahis_miktar(request):
    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN ABS(amount) <= 200 THEN '200 and below'
                    WHEN ABS(amount) > 200 AND ABS(amount) <= 300 THEN '201-300'
                    WHEN ABS(amount) > 300 AND ABS(amount) <= 400 THEN '301-400'
                    WHEN ABS(amount) > 400 AND ABS(amount) <= 500 THEN '401-500'
                    ELSE '501 and above'
                END AS bet_size,
                COUNT(CASE WHEN amount > 0 THEN 1 END) AS win_count,
                COUNT(CASE WHEN amount < 0 THEN 1 END) AS loss_count,
                (COUNT(CASE WHEN amount > 0 THEN 1 END) /
                 (COUNT(CASE WHEN amount < 0 THEN 1 END) + COUNT(CASE WHEN amount > 0 THEN 1 END)) * 100) AS win_rate_percentage,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_winnings,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bets,
                (SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                 SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) AS net_gain
            FROM 
                casi_uyg_bethistory
            GROUP BY 
                bet_size
            ORDER BY 
                net_gain DESC;
        """)

        # Fetch all results
        results = cursor.fetchall()

        # Get column names for rendering in the template
        column_names = [col[0] for col in cursor.description]
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN ABS(amount) <= 200 THEN '200 and below'
                    WHEN ABS(amount) > 200 AND ABS(amount) <= 300 THEN '201-300'
                    WHEN ABS(amount) > 300 AND ABS(amount) <= 400 THEN '301-400'
                    WHEN ABS(amount) > 400 AND ABS(amount) <= 500 THEN '401-500'
                    ELSE '501 and above'
                END AS bet_size,
                COUNT(CASE WHEN amount > 0 THEN 1 END) AS win_count,
                COUNT(CASE WHEN amount < 0 THEN 1 END) AS loss_count,
                (COUNT(CASE WHEN amount > 0 THEN 1 END) /
                 (COUNT(CASE WHEN amount < 0 THEN 1 END) + COUNT(CASE WHEN amount > 0 THEN 1 END)) * 100) AS win_rate_percentage,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_winnings,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS total_bets,
                (SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) -
                 SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END)) AS net_gain
            FROM 
                casi_uyg_bethistory2
            GROUP BY 
                bet_size
            ORDER BY 
                net_gain DESC;
        """)

        # Fetch all results
        results2 = cursor.fetchall()

        # Get column names for rendering in the template
        column_names2 = [col[0] for col in cursor.description]

    # Render the results in the template
    return render(request, 'bahis_miktar.html', {
        'results': results, 
        'column_names': column_names,
        'results2': results2, 
        'column_names2': column_names2,
    })


def son_oyunlar(request):
    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT
                t1.game,
                t1.amount AS bet_miktarı,
                t1.bet_time AS bet_time,
                t2.amount AS kazanç,
                t2.bet_time AS kazanç_time
            FROM (
                SELECT *
                FROM casi_uyg_bethistory
                WHERE amount < 0
                ORDER BY bet_time DESC
                LIMIT 30
            ) AS t1
            LEFT JOIN (
                SELECT *
                FROM casi_uyg_bethistory
                WHERE amount > 0
            ) AS t2 ON t1.game = t2.game
            AND ABS(TIMESTAMPDIFF(SECOND, t1.bet_time, t2.bet_time)) <= 300
            ORDER BY t1.bet_time desc;
                    """)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names = [col[0] for col in cursor.description]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t1.game,
                t1.amount AS bet_miktarı,
                t1.bet_time AS bet_time,
                t2.amount AS kazanç,
                t2.bet_time AS kazanç_time
            FROM (
                SELECT *
                FROM casi_uyg_bethistory2
                WHERE amount < 0
                ORDER BY bet_time DESC
                LIMIT 30
            ) AS t1
            LEFT JOIN (
                SELECT *
                FROM casi_uyg_bethistory2
                WHERE amount > 0
            ) AS t2 ON t1.game = t2.game
            AND ABS(TIMESTAMPDIFF(SECOND, t1.bet_time, t2.bet_time)) <= 300
            ORDER BY t1.bet_time desc;
        """)
        
        # Fetch all results
        results2 = cursor.fetchall()
        
        # Define column names for rendering in the template
        column_names2 = [col[0] for col in cursor.description]


    # Render the results in the template
    return render(request, 'son_oyunlar.html', {
        'results': results, 
        'column_names': column_names,
        'results2': results2, 
        'column_names2': column_names2,

    })
