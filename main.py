import telebot, database, admin_handlers, reseller_handlers, config, keyboards

bot = telebot.TeleBot(config.TOKEN)
database.init_db()

admin_handlers.register_admin(bot)
reseller_handlers.register_reseller(bot)

@bot.message_handler(commands=['start'])
@bot.callback_query_handler(func=lambda c: c.data == "start_menu")
def start(m):
    uid = m.from_user.id
    cid = m.chat.id if hasattr(m, 'chat') else m.message.chat.id
    if uid == config.ADMIN_ID:
        bot.send_message(cid, "👑 **Panel Administrador**", reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
    else:
        res = database.obtener_resellers()
        f = next((r for r in res if r[0] == uid), None)
        if f:
            bot.send_message(cid, f"👤 **Panel Reseller**\n💰 Créditos: `{f[1]}` ", reply_markup=keyboards.menu_reseller(f[1]), parse_mode="Markdown")
        else:
            bot.send_message(cid, "❌ Sin acceso.")

bot.infinity_polling()
