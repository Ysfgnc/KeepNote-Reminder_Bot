from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
import asyncio
import re

notes = {} # Kullanıcı notları için bir sözlük

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def note(update:Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    # Kullanıcının notunu kayıt eder.
    user_id = update.effective_user.id
    note_content = ''.join(context.args)

    if user_id not in notes:
        notes[user_id] = [] # Kullanıcı için yeni bir liste oluşturur.

    notes[user_id].append(note_content)
    await update.message.reply_text('Not Eklendi.')


async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    # Kullacının kayıt edilmiş notlarını listeler.
    user_id = update.effective_user.id
    if user_id in notes and notes[user_id]:
        note_list = '\n'.join(f" -{note}" for note in notes[user_id])
        await update.message.reply_text(f"Notlar --> \t{note_list}")
    # Not bulunmuyorsa mesaj gönderir.
    else:
        await update.message.reply_text("Not Bulunamadı.")

async def reminder(update:Update, context: ContextTypes.DEFAULT_TYPE)-> None:
    #Hatırlatma görevini yapan fonksiyon
    try:
        # Kullanıcıdan girilen süreyi ve mesajı alır.
        time_unit = {'gün': 86400 , 'saat': 3600, 'dk': 60}
        # Girilen mesajı ve süreyi ayrıştırır.
        time_pattern = re.compile(r'(\d+)\s*(gün|saat|dk)')
        matches = time_pattern.findall(''.join(context.args))
        reminder_text = ''.join([arg for arg in context.args if not time_pattern.match(arg)])

        if not matches:
            await update.message.reply_text('Süre Formatı -- x gün x saat x dk ')
            return
        # Toplam süreyi hesaplar.
        total_seconds = 0
        for value, unit in matches:
            total_seconds += int(value)*time_unit[unit]

        await update.message.reply_text(f"{''.join(context.args)} hatırlatma ayarlandı: {reminder_text}")
        # Toplam süre kadar bekler.
        await asyncio.sleep(total_seconds)
        # Süre dolduğunda mesajı gönderir.
        await update.message.reply_text(f"hatırlatma --> {reminder_text}")
        
    except (IndexError, ValueError):
        await update.message.reply_text(": /remind <hatırlatma mesajı>  <x gün x saat x dk")


async def group_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Grup içinde hatırlatma görevini yapan fonksiyon
    try:
        # Kullanıcıdan girilen süreyi al
        time_units = {'gün': 86400, 'saat': 3600, 'dk': 60}

        # Hatırlatma süresini ayrıştır
        time_pattern = re.compile(r'(\d+)\s*(gün|saat|dk)')
        matches = time_pattern.findall(' '.join(context.args))

        if not matches:
            await update.message.reply_text("Lütfen geçerli bir zaman birimi girin: x gün x saat x dk.")
            return

        # Toplam süreyi hesapla
        total_seconds = 0
        for value, unit in matches:
            total_seconds += int(value) * time_units[unit]

        # Mesajı ve kullanıcıyı sakla
        original_message = update.message.reply_to_message
        user_to_tag = update.effective_user.mention_html()

        if not original_message:
            await update.message.reply_text("Lütfen hatırlatılacak bir mesajı yanıtlayarak bu komutu kullanın.")
            return

        # Onay mesajı gönder
        await update.message.reply_text(
            f"{' '.join(context.args)} sonra bu mesajı hatırlatacağım: {original_message.text}")

        # Belirtilen süre kadar bekle
        await asyncio.sleep(total_seconds)

        # Süre dolduğunda mesajı kopyalayıp gruba gönder
        reminder_text = f"{user_to_tag} hatırlatma --> {original_message.text}"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=reminder_text,
            parse_mode='HTML'
        )

    except (IndexError, ValueError):
        await update.message.reply_text("Lütfen şu formatta bir komut girin: /grremind <süre> <x gün x saat x dk>")



app = ApplicationBuilder().token('** Telegram Bot Token ** ').build()
app.add_handler(CommandHandler('not', note))
app.add_handler(CommandHandler('notes',list_notes))
app.add_handler(CommandHandler('remind', reminder))
app.add_handler(CommandHandler('grremind', group_reminder))

if __name__ == '__main__':
    app.run_polling()