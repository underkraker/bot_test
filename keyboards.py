from telebot import types

def menu_admin():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👤 Crear Usuario", callback_data="adm_user_add"),
        types.InlineKeyboardButton("🗑 Eliminar SSH", callback_data="adm_user_del"),
        types.InlineKeyboardButton("📊 Stats", callback_data="adm_stats"),
        types.InlineKeyboardButton("🟢 Online", callback_data="adm_online"),
        types.InlineKeyboardButton("👥 Resellers", callback_data="adm_res_list"),
        types.InlineKeyboardButton("➕ Add Reseller", callback_data="adm_res_add"),
        types.InlineKeyboardButton("💰 Recargar", callback_data="adm_rec")
    )
    return markup

def btn_cancelar():
    # Teclado físico para cancelar durante la escritura de datos
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("❌ Cancelar"))
    return markup

def volver_adm():
    # Botón inline para regresar al menú principal
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Volver al Menú", callback_data="adm_main"))
    return markup
