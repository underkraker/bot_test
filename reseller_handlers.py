import subprocess, database, config, keyboards, vps_logic
from datetime import datetime, timedelta

def register_reseller(bot):
    @bot.callback_query_handler(func=lambda c: c.data == "res_req")
    def req(c):
        bot.answer_callback_query(c.id)
        bot.send_message(config.ADMIN_ID, f"🆘 **SOLICITUD CRÉDITOS**\nID: `{c.from_user.id}`", 
                         reply_markup=keyboards.btn_aprobar_solicitud(c.from_user.id), parse_mode="Markdown")
        bot.send_message(c.message.chat.id, "✅ Solicitud enviada.")

    @bot.callback_query_handler(func=lambda c: c.data == "create_user")
    def start_crea(c):
        bot.answer_callback_query(c.id)
        bot.clear_step_handler_by_chat_id(c.message.chat.id)
        msg = bot.send_message(c.message.chat.id, "👤 **Usuario:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, p1, bot)

    def p1(m, bot):
        if m.text == "/start": return
        u = m.text.strip()
        msg = bot.send_message(m.chat.id, "🔑 **Pass:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, p2, bot, u)

    def p2(m, bot, u):
        if m.text == "/start": return
        p = m.text.strip()
        msg = bot.send_message(m.chat.id, "📅 **Días:**", reply_markup=keyboards.btn_cancelar())
        bot.register_next_step_handler(msg, p3, bot, u, p)

    def p3(m, bot, u, p):
        if m.text == "/start": return
        try:
            d = int(m.text)
            msg = bot.send_message(m.chat.id, "🔢 **Límite:**", reply_markup=keyboards.btn_cancelar())
            bot.register_next_step_handler(msg, p4, bot, u, p, d)
        except: bot.send_message(m.chat.id, "❌ Solo números.")

    def p4(m, bot, u, p, d):
        if m.text == "/start": return
        try:
            lim = int(m.text)
            f = (datetime.now() + timedelta(days=d)).strftime('%Y-%m-%d')
            cmd = f"sudo useradd -M -s /bin/false -e {f} -c '{f} - LIM {lim}' {u} && echo '{u}:{p}' | sudo chpasswd"
            if subprocess.run(cmd, shell=True).returncode == 0:
                database.registrar_usuario_ssh(u, p, f, m.from_user.id, lim)
                if m.from_user.id != config.ADMIN_ID: database.restar_credito(m.from_user.id)
                ip = vps_logic.obtener_ip(); pts = vps_logic.obtener_puertos()
                ticket = (f"✅ **USUARIO CREADO**\n\n🌐 **IP:** `{ip}`\n👤 **Usuario:** `{u}`\n🔑 **Pass:** `{p}`\n📅 **Días:** `{d}`\n🗓 **Vence:** `{f}`\n🔢 **Límite:** `{lim}`\n🔌 **Puertos:** `{pts}` ")
                bot.send_message(m.chat.id, ticket, parse_mode="Markdown", reply_markup=keyboards.volver_adm())
        except: bot.send_message(m.chat.id, "❌ Error.")
