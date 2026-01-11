import database, keyboards, vps_logic, config, os, telebot

def register_admin(bot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
    def adm_actions(c):
        bot.answer_callback_query(c.id)
        if c.data == "adm_main":
            bot.edit_message_text("👑 **Panel Administrador**", c.message.chat.id, c.message.message_id, reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
        
        elif c.data == "adm_stats":
            i = vps_logic.obtener_info_vps()
            bot.edit_message_text(f"📊 **Estado:**\nCPU: `{i['cpu']}`\nRAM: `{i['ram']}`\nUptime: `{i['uptime']}` ", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")
        
        elif c.data == "adm_res_list":
            res = database.obtener_resellers(); txt = "👥 **Resellers:**\n"
            for r in res: txt += f"ID: `{r[0]}` | 💰: `{r[1]}` \n"
            bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=keyboards.volver_adm())
        
        elif c.data == "adm_res_add":
            msg = bot.send_message(c.message.chat.id, "🆔 **ID del nuevo Reseller:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_add_res, bot)
        
        elif c.data == "adm_rec":
            msg = bot.send_message(c.message.chat.id, "🆔 **ID a recargar:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_id, bot)

        # Botón Online corregido [cite: 2026-01-10]
        elif c.data == "adm_online":
            on = os.popen("ps -ef | grep sshd | grep -v root | grep -v grep | wc -l").read().strip()
            bot.edit_message_text(f"🟢 **Usuarios Online:** `{on}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        # Eliminación por lista [cite: 2026-01-10]
        elif c.data == "adm_user_del":
            usuarios = vps_logic.listar_usuarios_ssh()
            if not usuarios:
                bot.edit_message_text("❌ No hay usuarios.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm())
                return
            markup = telebot.types.InlineKeyboardMarkup()
            for u in usuarios:
                markup.add(telebot.types.InlineKeyboardButton(f"👤 {u}", callback_data=f"conf_del_{u}"))
            markup.add(telebot.types.InlineKeyboardButton("❌ Cancelar", callback_data="adm_main"))
            bot.edit_message_text("🗑 **Selecciona el usuario a eliminar:**", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # Manejadores de confirmación para eliminar [cite: 2026-01-10]
    @bot.callback_query_handler(func=lambda c: c.data.startswith("conf_del_"))
    def confirmar_del(c):
        user = c.data.replace("conf_del_", "")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ SÍ, ELIMINAR", callback_data=f"exec_del_{user}"))
        markup.add(telebot.types.InlineKeyboardButton("🚫 NO, VOLVER", callback_data="adm_user_del"))
        bot.edit_message_text(f"⚠️ ¿Eliminar a `{user}`?", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("exec_del_"))
    def ejecutar_del(c):
        user = c.data.replace("exec_del_", "")
        os.system(f"pkill -u {user} && userdel -r {user}")
        bot.edit_message_text(f"✅ Usuario `{user}` eliminado.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

    # Pasos con botón cancelar [cite: 2026-01-10]
    def step_add_res(m, bot):
        if m.text == "/start" or "Cancelar" in m.text: 
            bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            database.agregar_o_recargar_reseller(int(m.text), 0)
            bot.send_message(m.chat.id, "✅ Registrado.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Error.")

    def step_rec_id(m, bot):
        if m.text == "/start" or "Cancelar" in m.text:
            bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            rid = int(m.text)
            msg = bot.send_message(m.chat.id, f"💰 **Cantidad para {rid}:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_final, bot, rid)
        except: bot.send_message(m.chat.id, "❌ ID inválido.")

    def step_rec_final(m, bot, rid):
        if m.text == "/start" or "Cancelar" in m.text:
            bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            cant = int(m.text)
            database.agregar_o_recargar_reseller(rid, cant)
            bot.send_message(m.chat.id, f"✅ Recargados {cant}.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Cantidad inválida.")
