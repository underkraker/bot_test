import database, keyboards, vps_logic, config, os, telebot, datetime

def register_admin(bot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
    def adm_actions(c):
        bot.answer_callback_query(c.id)
        # --- MENÚ PRINCIPAL ---
        if c.data == "adm_main":
            bot.edit_message_text("👑 **Panel Administrador**", c.message.chat.id, c.message.message_id, reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
        
        # --- CREAR USUARIO ---
        elif c.data == "adm_user_add":
            msg = bot.send_message(c.message.chat.id, "👤 **Nombre del usuario:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_name, bot)

        # --- ELIMINAR USUARIO POR LISTA ---
        elif c.data == "adm_user_del":
            usuarios = vps_logic.listar_usuarios_ssh()
            if not usuarios:
                bot.edit_message_text("❌ No hay usuarios.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm())
                return
            markup = telebot.types.InlineKeyboardMarkup()
            for u in usuarios:
                markup.add(telebot.types.InlineKeyboardButton(f"👤 {u}", callback_data=f"conf_del_{u}"))
            markup.add(telebot.types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
            bot.edit_message_text("🗑 **Selecciona para eliminar:**", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

        # --- ONLINE Y STATS ---
        elif c.data == "adm_online":
            on = os.popen("ps -ef | grep sshd | grep -v root | grep -v grep | wc -l").read().strip()
            bot.edit_message_text(f"🟢 **Usuarios Online:** `{on}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        elif c.data == "adm_stats":
            i = vps_logic.obtener_info_vps()
            bot.edit_message_text(f"📊 **Estado:**\nCPU: `{i['cpu']}`\nRAM: `{i['ram']}`\nUptime: `{i['uptime']}`", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        # --- RESELLERS ---
        elif c.data == "adm_res_list":
            res = database.obtener_resellers(); txt = "👥 **Lista de Resellers:**\n"
            for r in res: txt += f"ID: `{r[0]}` | Créditos: `{r[1]}`\n"
            bot.edit_message_text(txt if res else "❌ No hay resellers.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

        elif c.data == "adm_res_add":
            msg = bot.send_message(c.message.chat.id, "🆔 **ID del nuevo Reseller:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_res_id, bot)

        elif c.data == "adm_rec":
            msg = bot.send_message(c.message.chat.id, "🆔 **ID del Reseller a recargar:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_id, bot)

    # --- LÓGICA DE ELIMINACIÓN ---
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
        bot.edit_message_text(f"✅ Usuario `{user}` eliminado correctamente.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm(), parse_mode="Markdown")

    # --- FLUJO CREAR USUARIO (DÍAS Y LÍMITE) ---
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
        d = m.text
        msg = bot.send_message(m.chat.id, "🔢 **Límite de conexiones:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_final, bot, u, p, d)

    def step_final(m, bot, u, p, d):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        lim = m.text
        os.system(f"useradd -M -s /bin/false {u} && echo '{u}:{p}' | chpasswd")
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

    # --- LÓGICA DE RESELLERS ---
    def step_res_id(m, bot):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            database.agregar_o_recargar_reseller(int(m.text), 0)
            bot.send_message(m.chat.id, "✅ Reseller agregado.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ ID inválido.")

    def step_rec_id(m, bot):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            rid = int(m.text)
            msg = bot.send_message(m.chat.id, "💰 **Cantidad de créditos:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_final, bot, rid)
        except: bot.send_message(m.chat.id, "❌ ID inválido.")

    def step_rec_final(m, bot, rid):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            database.agregar_o_recargar_reseller(rid, int(m.text))
            bot.send_message(m.chat.id, "✅ Créditos añadidos.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Cantidad inválida.")
