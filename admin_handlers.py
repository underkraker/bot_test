import database, keyboards, vps_logic, config

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

    def step_add_res(m, bot):
        if m.text == "/start": return
        try:
            database.agregar_o_recargar_reseller(int(m.text), 0)
            bot.send_message(m.chat.id, "✅ Registrado.", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Error.")

    def step_rec_id(m, bot):
        if m.text == "/start": return
        rid = int(m.text)
        msg = bot.send_message(m.chat.id, f"💰 **Cantidad para {rid}:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, step_rec_final, bot, rid)

    def step_rec_final(m, bot, rid):
        if m.text == "/start": return
        cant = int(m.text)
        database.agregar_o_recargar_reseller(rid, cant)
        bot.send_message(m.chat.id, f"✅ Recargados {cant}.", reply_markup=keyboards.volver_adm())
