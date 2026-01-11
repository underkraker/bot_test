from telebot import types

def menu_admin():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Estado", callback_data="adm_stats"),
        types.InlineKeyboardButton("👥 Lista Resellers", callback_data="adm_res_list"),
        types.InlineKeyboardButton("➕ Nuevo Reseller", callback_data="adm_res_add"),
        types.InlineKeyboardButton("💰 Recargar Saldo", callback_data="adm_rec"),
        types.InlineKeyboardButton("➕ Crear SSH", callback_data="create_user"),
        types.InlineKeyboardButton("❌ Eliminar SSH", callback_data="adm_del"),
        types.InlineKeyboardButton("🟢 Online", callback_data="adm_on"),
        types.InlineKeyboardButton("🔙 Volver Inicio", callback_data="start_menu")
    )
    return markup

def menu_reseller(creds):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"➕ Crear SSH (💰 {creds})", callback_data="create_user"),
        types.InlineKeyboardButton("🆘 Pedir Créditos", callback_data="res_req"),
        types.InlineKeyboardButton("🔙 Volver Inicio", callback_data="start_menu")
    )
    return markup

def btn_cancelar():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancelar y Volver", callback_data="start_menu"))
    return markup

def volver_adm():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
    return m

def btn_aprobar_solicitud(rid):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Dar 10", callback_data=f"aprob_10_{rid}"),
        types.InlineKeyboardButton("✅ Dar 50", callback_data=f"aprob_50_{rid}"),
        types.InlineKeyboardButton("✅ Dar 100", callback_data=f"aprob_100_{rid}")
    )
    markup.add(types.InlineKeyboardButton("❌ Denegar", callback_data=f"denegar_{rid}"))
    return markup
