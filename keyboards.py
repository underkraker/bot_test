from telebot import types

def btn_cancelar():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("❌ Cancelar y Volver")
    return markup

def volver_adm():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
    return markup
