import database, keyboards, vps_logic, config, os, telebot, datetime

def register_admin(bot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
    def adm_actions(c):
        bot.answer_callback_query(c.id)
        if c.data == "adm_main":
            bot.edit_message_text("👑 **Panel Administrador**", c.message.chat.id, c.message.message_id, reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
        
        elif c.data == "adm_user_add":
            msg = bot.send_message(c.message.chat.id, "👤 **Nombre del nuevo usuario:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_name, bot)

        elif c.data == "adm_user_del":
            usuarios = vps_logic.listar_usuarios_ssh()
            if not usuarios:
                bot.edit_message_text("❌ No hay usuarios para eliminar.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm())
                return
            markup = telebot.types.InlineKeyboardMarkup()
            for u in usuarios: markup.add(telebot.types.InlineKeyboardButton(f"👤 {u}", callback_data=f"conf_del_{u}"))
            markup.add(telebot.types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
            bot.edit_message_text("🗑 **Selecciona para eliminar:**", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

        elif c.data == "adm_stats":
            i = vps_logic.obtener_info_vps()
            bot.edit_message_text(f"📊 **Estado:**\nCPU: `{i['cpu']}` | RAM: `{i['ram']}`\nUptime: `{i['uptime']}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        elif c.data == "adm_online":
            on = os.popen("ps -ef | grep sshd | grep -v root | grep -v grep | wc -l").read().strip()
            bot.edit_message_text(f"🟢 **Online:** `{on}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        elif c.data == "adm_res_list":
            res = database.obtener_resellers(); txt = "👥 **Resellers:**\n"
            for r in res: txt += f"ID: `{r[0]}` | Cred: `{r[1]}`\n"
            bot.edit_message_text(txt if res else "❌ Sin resellers.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        elif c.data == "adm_rec":
            msg = bot.send_message(c.message.chat.id, "🆔 **Introduce el ID del Reseller a recargar:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_id, bot)

    # --- LÓGICA DE ELIMINACIÓN ---
    @bot.callback_query_handler(func=lambda c: c.data.startswith("conf_del_"))
    def confirmar_del(c):
        user = c.data.replace("conf_del_", "")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ SÍ, ELIMINAR", callback_data=f"exec_del_{user}"))
        markup.add(telebot.types.InlineKeyboardButton("🚫 NO", callback_data="adm_user_del"))
        bot.edit_message_text(f"⚠️ ¿Eliminar a `{user}`?", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("exec_del_"))
    def ejecutar_del(c):
        user = c.data.replace("exec_del_", "")
        os.system(f"sudo pkill -9 -u {user} && sudo userdel -rf {user}")
        bot.edit_message_text(f"✅ `{user}` ELIMINADO.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

    # --- FLUJO CREAR USUARIO (CORREGIDO) ---
    def step_name(m, bot):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        u = m.text
        msg = bot.send_message(m.chat.id, f"🔑 **Contraseña para {u}:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_pass, bot, u)

    def step_pass(m, bot, u):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        p = m.text
        msg = bot.send_message(m.chat.id, "📅 **Días de duración:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_days, bot, u, p)

    def step_days(m, bot, u, p):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            d = int(m.text)
            msg = bot.send_message(m.chat.id, "🔢 **Límite de conexiones:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_final, bot, u, p, d)
        except: bot.send_message(m.chat.id, "❌ Error: Solo números.", reply_markup=keyboards.btn_cancelar()); return

    def step_final(m, bot, u, p, d):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        lim = m.text
        os.system(f"sudo useradd -M -s /bin/false {u} && echo '{u}:{p}' | sudo chpasswd")
        vence = (datetime.datetime.now() + datetime.timedelta(days=d)).strftime('%Y-%m-%d')
        res = (f"✅ **USUARIO CREADO**\n\n👤 **User:** `{u}`\n🔑 **Pass:** `{p}`\n🗓 **Vence:** {vence}\n🔢 **Límite:** {lim}")
        bot.send_message(m.chat.id, res, parse_mode="Markdown", reply_markup=keyboards.volver_adm())

    # --- FLUJO RECARGAR CRÉDITOS (CORREGIDO) ---
    def step_rec_id(m, bot):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            rid = int(m.text)
            msg = bot.send_message(m.chat.id, f"💰 **Créditos para {rid}:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_final, bot, rid)
        except: bot.send_message(m.chat.id, "❌ ID inválido.", reply_markup=keyboards.btn_cancelar()); return

    def step_rec_final(m, bot, rid):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            cred = int(m.text)
            database.agregar_o_recargar_reseller(rid, cred)
            bot.send_message(m.chat.id, f"✅ ID {rid} recargado con {cred}.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Cantidad inválida.", reply_markup=keyboards.btn_cancelar()); return
