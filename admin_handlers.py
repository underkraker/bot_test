import database, keyboards, vps_logic, config, os, telebot, datetime

def register_admin(bot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
    def adm_actions(c):
        bot.answer_callback_query(c.id)
        # --- NO TOCAR LO QUE YA FUNCIONA ---
        if c.data == "adm_main":
            bot.edit_message_text("👑 **Panel Administrador**", c.message.chat.id, c.message.message_id, reply_markup=keyboards.menu_admin(), parse_mode="Markdown")
        
        elif c.data == "adm_user_del":
            usuarios = vps_logic.listar_usuarios_ssh()
            if not usuarios:
                bot.edit_message_text("❌ No hay usuarios.", c.message.chat.id, c.message.message_id, reply_markup=keyboards.volver_adm())
                return
            markup = telebot.types.InlineKeyboardMarkup()
            for u in usuarios: markup.add(telebot.types.InlineKeyboardButton(f"👤 {u}", callback_data=f"conf_del_{u}"))
            markup.add(telebot.types.InlineKeyboardButton("🔙 Volver", callback_data="adm_main"))
            bot.edit_message_text("🗑 **Selecciona para eliminar:**", c.message.chat.id, c.message.message_id, reply_markup=markup, parse_mode="Markdown")

        # --- ARREGLO: CREAR USUARIO ---
        elif c.data == "adm_user_add":
            msg = bot.send_message(c.message.chat.id, "👤 **Nombre del nuevo usuario:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_name, bot)

        # --- ARREGLO: RECARGAR CRÉDITOS ---
        elif c.data == "adm_rec":
            msg = bot.send_message(c.message.chat.id, "🆔 **Introduce el ID del Reseller a recargar:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_id, bot)

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
        except: bot.send_message(m.chat.id, "❌ Error: Solo números para los días."); return

    def step_final(m, bot, u, p, d):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        lim = m.text
        # Ejecución real en el VPS
        os.system(f"sudo useradd -M -s /bin/false {u} && echo '{u}:{p}' | sudo chpasswd")
        vence = (datetime.datetime.now() + datetime.timedelta(days=d)).strftime('%Y-%m-%d')
        
        res = (f"✅ **USUARIO CREADO CON ÉXITO**\n\n"
               f"👤 **User:** `{u}`\n🔑 **Pass:** `{p}`\n🗓 **Vence:** {vence}\n🔢 **Límite:** {lim}")
        bot.send_message(m.chat.id, res, parse_mode="Markdown", reply_markup=keyboards.volver_adm())

    # --- FLUJO RECARGAR (CORREGIDO) ---
    def step_rec_id(m, bot):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            rid = int(m.text)
            msg = bot.send_message(m.chat.id, "💰 **Cantidad de créditos a añadir:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, step_rec_final, bot, rid)
        except: bot.send_message(m.chat.id, "❌ ID no válido."); return

    def step_rec_final(m, bot, rid):
        if m.text == "❌ Cancelar": bot.send_message(m.chat.id, "🚫 Cancelado.", reply_markup=keyboards.menu_admin()); return
        try:
            creditos = int(m.text)
            database.agregar_o_recargar_reseller(rid, creditos)
            bot.send_message(m.chat.id, f"✅ Se han añadido {creditos} créditos al ID {rid}.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Cantidad no válida."); return
