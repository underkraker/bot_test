import database, keyboards, vps_logic, config, os, telebot, subprocess

def register_admin(bot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
    def adm_actions(c):
        bot.answer_callback_query(c.id)
        if c.data == "adm_main":
            bot.edit_message_text("👑 **Panel Administrador**", c.message.chat.id, c.message.message_id, reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
        
        elif c.data == "adm_user_add":
            msg = bot.send_message(c.message.chat.id, "👤 **Nombre del nuevo usuario:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_add_user, bot)

        elif c.data == "adm_user_del":
            usuarios = vps_logic.listar_usuarios_ssh()
            if not usuarios:
                bot.edit_message_text("❌ No hay usuarios para eliminar.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm())
                return
            markup = telebot.types.InlineKeyboardMarkup()
            for u in usuarios:
                markup.add(telebot.types.InlineKeyboardButton(f"👤 {u}", callback_data=f"conf_del_{u}"))
            markup.add(telebot.types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
            bot.edit_message_text("🗑 **Selecciona el usuario a eliminar:**", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif c.data == "adm_online":
            on = os.popen("ps -ef | grep sshd | grep -v root | grep -v grep | wc -l").read().strip()
            bot.edit_message_text(f"🟢 **Usuarios Online:** `{on}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        elif c.data == "adm_stats":
            i = vps_logic.obtener_info_vps()
            bot.edit_message_text(f"📊 **Estado:**\nCPU: `{i['cpu']}`\nRAM: `{i['ram']}`\nUptime: `{i['uptime']}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("conf_del_"))
    def confirmar_del(c):
        user = c.data.replace("conf_del_", "")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ SÍ, ELIMINAR", callback_data=f"exec_del_{user}"))
        markup.add(telebot.types.InlineKeyboardButton("🚫 NO, CANCELAR", callback_data="adm_user_del"))
        bot.edit_message_text(f"⚠️ ¿Estás seguro de eliminar a `{user}`?", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("exec_del_"))
    def ejecutar_del(c):
        user = c.data.replace("exec_del_", "")
        os.system(f"pkill -u {user} && userdel -r {user}")
        bot.edit_message_text(f"✅ Usuario `{user}` eliminado.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

    def step_add_user(m, bot):
        if m.text == "❌ Cancelar" or m.text == "/start":
            bot.send_message(m.chat.id, "🚫 Operación cancelada.", reply_markup=keyboards.menu_admin())
            return
        usuario = m.text
        msg = bot.send_message(m.chat.id, f"🔑 **Contraseña para {usuario}:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_add_user_pass, bot, usuario)

    def step_add_user_pass(m, bot, usuario):
        if m.text == "❌ Cancelar":
            bot.send_message(m.chat.id, "🚫 Operación cancelada.", reply_markup=keyboards.menu_admin())
            return
        password = m.text
        # Comando para crear usuario en Linux
        os.system(f"useradd -M -s /bin/false {usuario} && echo '{usuario}:{password}' | chpasswd")
        
        puertos = vps_logic.obtener_puertos() # Puertos limpios
        ip = vps_logic.obtener_ip()
        
        texto = (f"✅ **USUARIO CREADO**\n\n"
                 f"🌐 **IP:** `{ip}`\n"
                 f"👤 **Usuario:** `{usuario}`\n"
                 f"🔑 **Pass:** `{password}`\n"
                 f"🔌 **Puertos:** `{puertos}`")
        
        bot.send_message(m.chat.id, texto, parse_mode="Markdown", reply_markup=keyboards.volver_adm())
