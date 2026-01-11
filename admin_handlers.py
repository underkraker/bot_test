import database, keyboards, vps_logic, config, os, telebot, datetime, subprocess

def register_admin(bot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
    def adm_actions(c):
        bot.answer_callback_query(c.id)
        if c.data == "adm_main":
            bot.edit_message_text("👑 **Panel Administrador**", c.message.chat.id, c.message.message_id, reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
        
        elif c.data == "adm_user_add":
            msg = bot.send_message(c.message.chat.id, "👤 **Nombre del usuario:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_name, bot)

        elif c.data == "adm_user_del":
            usuarios = vps_logic.listar_usuarios_ssh()
            if not usuarios:
                bot.edit_message_text("❌ No hay usuarios en el sistema.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm())
                return
            markup = telebot.types.InlineKeyboardMarkup()
            for u in usuarios:
                markup.add(telebot.types.InlineKeyboardButton(f"👤 {u}", callback_data=f"conf_del_{u}"))
            markup.add(telebot.types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
            bot.edit_message_text("🗑 **Selecciona para eliminar:**", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

        # ... (Demás botones: Online, Stats, Resellers se mantienen iguales) ...

    # --- LÓGICA DE ELIMINACIÓN REFORZADA ---
    @bot.callback_query_handler(func=lambda c: c.data.startswith("conf_del_"))
    def confirmar_del(c):
        user = c.data.replace("conf_del_", "")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ SÍ, ELIMINAR AHORA", callback_data=f"exec_del_{user}"))
        markup.add(telebot.types.InlineKeyboardButton("🚫 NO, VOLVER", callback_data="adm_user_del"))
        bot.edit_message_text(f"⚠️ ¿Eliminar a `{user}`?\nEsta acción es irreversible y cerrará sus conexiones.", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("exec_del_"))
    def ejecutar_del(c):
        user = c.data.replace("exec_del_", "")
        
        # 1. Forzar cierre de todos los procesos del usuario
        # 2. Borrar usuario y su directorio de forma recursiva y forzada (-rf)
        comando_limpieza = f"sudo pkill -9 -u {user} > /dev/null 2>&1"
        comando_borrado = f"sudo userdel -r -f {user} > /dev/null 2>&1"
        
        os.system(comando_limpieza)
        os.system(comando_borrado)
        
        # Verificación inmediata en el sistema
        if user not in vps_logic.listar_usuarios_ssh():
            bot.edit_message_text(f"✅ Usuario `{user}` ELIMINADO correctamente del sistema.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ No se pudo eliminar a `{user}`. Revisa permisos de administrador en el VPS.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

    # --- CREACIÓN DE USUARIO (Días/Límite - SIN TOCAR NADA) ---
    def step_name(m, bot):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        u = m.text
        msg = bot.send_message(m.chat.id, f"🔑 **Pass para {u}:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_pass, bot, u)

    def step_pass(m, bot, u):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        p = m.text
        msg = bot.send_message(m.chat.id, "📅 **Días de duración:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_days, bot, u, p)

    def step_days(m, bot, u, p):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        d = m.text
        msg = bot.send_message(m.chat.id, "🔢 **Límite de conexiones:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_final, bot, u, p, d)

    def step_final(m, bot, u, p, d):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        lim = m.text
        os.system(f"sudo useradd -M -s /bin/false {u} && echo '{u}:{p}' | sudo chpasswd")
        vence = (datetime.datetime.now() + datetime.timedelta(days=int(d))).strftime('%Y-%m-%d')
        
        res = (f"✅ **USUARIO CREADO**\n\n"
               f"🌐 **IP:** `{vps_logic.obtener_ip()}`\n"
               f"👤 **Usuario:** `{u}`\n"
               f"🔑 **Pass:** `{p}`\n"
               f"📅 **Días:** {d}\n"
               f"🗓 **Vence:** {vence}\n"
               f"🔢 **Límite:** {lim}\n"
               f"🔌 **Puertos:** `{vps_logic.obtener_puertos()}`")
        bot.send_message(m.chat.id, res, parse_mode="Markdown", reply_markup=keyboards.volver_adm())
