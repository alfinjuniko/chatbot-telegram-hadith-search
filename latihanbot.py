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

#command start
@bot.message_handler(commands=['start'])
def start(message):
    log(message, 'start')
    bot.reply_to(message, 'Assalamualaikum,\nStatus bot dalam keadaan aktif.\n\nKamu bisa menggunakan bot ini untuk melakukan pencarian hadits dari kitab Riyadhus Shalihin.\n\nuntuk menjalankan bot kamu dapat menggunakan Command dibawah ini :\n\n/start  -->  memulai percakapan\n/hadits [nomor hadits]  -->  mencari hadits (hilangkan tanda kurung siku)')

#command pencarian hadits
@bot.message_handler(commands=['hadits'])
def hadits(message):
    texts=message.text.split(' ')
    id = texts[1]
       
    log(message, 'cari hadits ' + id)
    limit = int(id)

    if (limit <= 800 ) :

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

        b1,b2,b3,b4 = b1.replace("'",""), b2.replace("'",""), b3.replace("'",""), b4.replace("'","")
        b1,b2,b3,b4 = b1.replace("(",""), b2.replace("(",""), b3.replace("(",""), b4.replace("(","")
        b1,b2,b3,b4 = b1.replace(")",""), b2.replace(")",""), b3.replace(")",""), b4.replace(")","")
        b3,b4= b3.replace("<br>","\n"), b4.replace("<br>","\n")
        b1,b2,b3 = b1.replace(",",""), b2.replace(",",""), b3.replace(",","")

    
    # Periksa panjang pesan
        if len(b4) <= 4096: 
            bot.reply_to(message,'Kitab : Riyadhus Shalihin\nPengarang : Imam Abu Zakariya Yahya bin Syaraf An-Nawawi (Imam Nawawi)\n\nBAB : ' + b1 + 'Hadits ke-' + b2 + ' :\n\n' + b3 + b4)
        else:              
        # membagi pesan yang terlalu panjang
            Arab = [b3[i:i+4096] for i in range(0, len(b3), 4096)]
            for arab in Arab:
                c = 'Kitab : Riyadhus Shalihin \nPengarang : Imam Abu Zakariya Yahya bin Syaraf An-Nawawi (Imam Nawawi)\n\nBAB : ' + b1 + 'Hadits ke-' + b2 + ' :\n\n' + arab
                
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


print('bot start running...')
bot.polling() 