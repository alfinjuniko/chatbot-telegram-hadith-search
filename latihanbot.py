import telebot
import mysql.connector
import datetime

tanggal = datetime.datetime.now()
tanggal = tanggal.strftime('%d-%h-%Y %H:%M:%S')


def log(message, perintah):
    tanggal = datetime.datetime.now()
    tanggal = tanggal.strftime('%d-%h-%Y %H:%M:%S')
    firstName = message.chat.first_name
    lastName = message.chat.last_name
    text_log = '{}, {} {}, {}\n'.format(tanggal, firstName, lastName, perintah)
    log_bot = open('log_bot.txt', 'a')
    log_bot.write(text_log)
    log_bot.close()

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='database_hadits'
)

sql = mydb.cursor()

api = '6723355645:AAFALwZdwgaOOKkMMjEyH32J6p21LJDrfEw'
bot = telebot.TeleBot(api)

# Command start
@bot.message_handler(commands=['start'])
def start(message):
    log(message, 'start')
    bot.reply_to(message, 'Assalamualaikum Warahmatullahi Wabarakatuh,\nStatus bot dalam keadaan aktif.\n\nKamu bisa menggunakan bot ini untuk melakukan pencarian hadits dari kitab Riyadhus Shalihin.\n\nuntuk menjalankan bot kamu dapat menggunakan Command dibawah ini :\n\n/start  -->  memulai percakapan\n/bab --> menampilkan daftar bab\n/hadits [nomor hadits]  -->  mencari hadits (hilangkan tanda kurung siku)\n/about -- menampilkan informasi mengenai bot')

# Command pencarian bab
@bot.message_handler(commands=['bab'])
def bab(message):
    log(message, 'bab')

    try:
        # Ambil semua bab dari database
        sql.execute("SELECT bab FROM riyadhus_shalihin")
        hasil = sql.fetchall()  # Ambil semua data dari query

        # Periksa apakah hasil tidak kosong
        if hasil:
            # Gunakan set untuk menyimpan bab unik
            unique_bab = set()
            daftar_bab_list = []

            for bab in hasil:
                bab_text = bab[0]  # Ambil teks bab
                if bab_text not in unique_bab:
                    unique_bab.add(bab_text)
                    daftar_bab_list.append(bab_text)

            # Susun daftar bab dengan penomoran berbasis looping
            daftar_bab = "\n".join([f"BAB {i + 1}: {bab}" for i, bab in enumerate(daftar_bab_list)])

            # Pecah pesan jika terlalu panjang
            messages = [daftar_bab[j:j + 4096] for j in range(0, len(daftar_bab), 4096)]
            for msg in messages:
                bot.reply_to(message, msg)
        else:
            # Jika tidak ada data
            bot.reply_to(message, "Maaf, daftar bab tidak ditemukan.")

    except mysql.connector.Error as err:
        # Tangani kesalahan database
        bot.reply_to(message, f"Terjadi kesalahan database: {err}")
    except Exception as e:
        # Tangani kesalahan lainnya
        bot.reply_to(message, f"Terjadi kesalahan: {e}")

#command pencarian hadits
@bot.message_handler(commands=['hadits'])
def hadits(message):
    texts=message.text.split(' ')
     # Jika pengguna tidak menyertakan nomor ID hadits
    if len(texts) < 2:
        log(message, 'missing hadits ID')
        bot.reply_to(message, 'Harap sertakan nomor hadits yang ingin dicari setelah perintah /hadits.\nContoh: /hadits 1')
        return
    id = texts[1]
       
    log(message, 'cari hadits ' + id)
    limit = int(id)

    try:
        if (limit <= 1899 ) :

        #ambil data dari mysql
            sql.execute("select bab from riyadhus_shalihin where id='{}'".format(id))
            hasil_sql1 = sql.fetchall()
            print(hasil_sql1)

            sql.execute("select id from riyadhus_shalihin where id='{}'".format(id))
            hasil_sql2 = sql.fetchall()
            print(hasil_sql2)

            sql.execute("select arab from riyadhus_shalihin where id='{}'".format(id))
            hasil_sql3 = sql.fetchall() 
            print(hasil_sql3)

            sql.execute("select terjemah from riyadhus_shalihin where id='{}'".format(id))
            hasil_sql4 = sql.fetchall()
            print(hasil_sql4)


        #output di bot telegram
            b1 = ''
            b2 = ''
            b3 = '' 
            b4 = ''
            for x in hasil_sql1 :
                b1 = b1 + str(x) + '\n\n'
            for x in hasil_sql2 :
                b2 = b2 + str(x)
            for x in hasil_sql3 :
                b3 = b3 + str(x) + '\n\n'
            for x in hasil_sql4 :
                b4 = b4 + str(x)

        # menghapus tanda baca yang tidak diperlukan
            b1,b2,b3,b4 = b1.replace("'",""), b2.replace("'",""), b3.replace("'",""), b4.replace("'","")
            b1,b2,b3,b4 = b1.replace("(",""), b2.replace("(",""), b3.replace("(",""), b4.replace("(","")
            b1,b2,b3,b4 = b1.replace(")",""), b2.replace(")",""), b3.replace(")",""), b4.replace(")","")
            b3,b4= b3.replace("<br>","\n"), b4.replace("<br>","\n")
            b1,b2,b3 = b1.replace(",",""), b2.replace(",",""), b3.replace(",","")

        
        # Periksa panjang pesan
            if len(b4) <= 4096: 
                bot.reply_to(message,'Kitab : Riyadhus Shalihin\nKarya : Imam Abu Zakariya Yahya bin Syaraf An-Nawawi (Imam Nawawi)\n\nBAB : ' + b1 + 'Hadits ke-' + b2 + ' :\n\n' + b3 + 'Artinya :\n' + b4)
            else:              
            # membagi pesan yang terlalu panjang
                Arab = [b3[i:i+4096] for i in range(0, len(b3), 4096)]
                for arab in Arab:
                    c = 'Kitab : Riyadhus Shalihin \nKarya : Imam Abu Zakariya Yahya bin Syaraf An-Nawawi (Imam Nawawi)\n\nBAB : ' + b1 + 'Hadits ke-' + b2 + ' :\n\n' + arab
                    
                    if len(c) <= 4096:
                        bot.reply_to(message, c)
                    else:
                        d = [c[i:i+4096] for i in range(0, len(c), 4096)]
                        for d1 in d:
                            bot.reply_to(message, d1)

                Latin = [b4[i:i+4096] for i in range(0, len(b4), 4096)]
                for latin in Latin:
                    bot.reply_to(message, latin)

        else :
            bot.reply_to(message, 'Hadits tidak ditemukan')

    except mysql.connector.Error as err:
        # Tangani error database
        bot.reply_to(message, f"Terjadi kesalahan database: {err}")
    except Exception as e:
        # Tangani error umum
        bot.reply_to(message, f"Terjadi kesalahan: {e}")

# Command about
@bot.message_handler(commands=['about'])
def start(message):
    log(message, 'menampilkan informasi bot')
    bot.reply_to(message, 'Tentang Bot\n\nBot ini dirancang untuk membantu Anda dalam mencari dan mempelajari hadits-hadits dari kitab Riyadhus Shalihin karya Imam Abu Zakariya Yahya bin Syaraf An-Nawawi (Imam Nawawi) secara mudah dan cepat. Bot ini dapat diakses kapan saja dan di mana saja melalui aplikasi Telegram.\n\nBot ini dikembangkan oleh mahasiswa magang UIN Sultan Syarif Kasim Riau di Laboratorium Inkubator Bisnis.\n\nPanduan pengguna:\nuntuk menjalankan bot kamu dapat menggunakan Command dibawah ini\n\n/start  -->  memulai percakapan\n/bab --> menampilkan daftar bab\n/hadits [nomor hadits]  -->  mencari hadits (hilangkan tanda kurung siku)\n/about -- menampilkan informasi mengenai bot')

# Handler untuk command yang tidak dikenali
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    log(message, 'unknown command')
    bot.reply_to(message, 'Maaf, format yang anda masukkan salah.\nSilakan gunakan perintah berikut:\n\n'
                          '/start - Memulai bot\n'
                          '/bab - Menampilkan daftar bab\n'
                          '/hadits [nomor] - Mencari hadits\n'
                          '/about - Informasi tentang bot')

print('bot start running...')
bot.polling() 
