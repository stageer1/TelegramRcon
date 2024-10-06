import asyncio
from mcrcon import MCRcon
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command as cmd
import json
from functions import *

config = json.load(open("config.json"))

token = config["token"] # Вставьте токен своего Telegram-бота

check_empty_users()

host = config["host"] # IP вашего сервера (без порта)
port = config["port"] # Порт сервера
password = config["password"] # Пароль Rcon

bot = Bot(token=token)
dp = Dispatcher()

@dp.message(cmd("register"))
async def register_user(message: types.message):
    meta = message.text.split()[1:]
    if len(meta) < 2: return await message.reply("❗️Использование: */register <tgid> <group>*", parse_mode="Markdown")

    tgid = int(meta[0])
    level = meta[1]

    data = check_user_in_db(message.from_user.id, "data.db")[1]
    groups = json.load(open("groups.json"))
    data_weight = groups[data]["weight"] if data != "super" else 10 ** 5
    groups_list = list(groups.keys())
    if data not in groups_list and data != "super":
        return await message.reply("❌ *Не удалось получить вашу группу.*", parse_mode="Markdown")

    if tgid == message.from_user.id: return message.reply("❌ *Вы не можете использовать это на себе!*", parse_mode="Markdown")

    if  data == "super" or message.text.split()[0][1:] in groups[data]["allowed_super_commands"]:
        if check_user_in_db(tgid, "data.db"):
            return await message.reply("⚠️ *Этот пользователь уже зарегистрирован.*", parse_mode="Markdown")
        if level not in groups_list:
            return await message.reply("❌ *Такой группы не существует!*", parse_mode="Markdown")
        if data_weight <= groups[level]["weight"] or level == "super":
            return await message.reply("⚠️ *Вы не можете зарегистрировать пользователя с этой группой!*", parse_mode="Markdown")
        register(tgid, level, "data.db")
        await message.reply(f"✅ *Вы зарегистрировали пользователя TG-{tgid} с группой {level.upper()}!*", parse_mode="Markdown")
    else:
        return await message.reply("⚠️ *Эта команда Вам не разрешена.*", parse_mode="Markdown")

@dp.message(cmd("unregister"))
async def unregister_user(message: types.message):
    meta = message.text.split()[1:]
    if len(meta) < 1: return await message.reply("❗️*Использование: /unregister <tgid>*", parse_mode="Markdown")

    tgid = int(meta[0])

    data = check_user_in_db(message.from_user.id)[1]
    data2 = check_user_in_db(tgid)[1]
    groups = json.load(open("groups.json"))
    groups_list = list(groups.keys())
    data_weight = groups[data]["weight"] if data != "super" else 10**5
    data_weight2 = groups[data]["weight"] if data2 in groups_list else 0
    if data not in groups_list and data != "super":
        return await message.reply("❌ *Не удалось получить вашу группу.*", parse_mode="Markdown")

    if tgid == message.from_user.id: return message.reply("❌ *Вы не можете использовать это на себе!*", parse_mode="Markdown")

    if  data == "super" or message.text.split()[0][1:] in groups[data]["allowed_super_commands"]:
        if not check_user_in_db(tgid):
            return await message.reply("⚠️ *Этот пользователь не зарегистрирован.*", parse_mode="Markdown")
        if data2 == "super" or data_weight <= data_weight2:
            return await message.reply("⚠️ *Вы не можете удалить этого пользователя!*", parse_mode="Markdown")
        unregister(tgid)
        await message.reply(f"✅ *Вы удалили пользователя TG-{tgid}!*", parse_mode="Markdown")
    else:
        return await message.reply("⚠️ *Эта команда Вам не разрешена.*", parse_mode="Markdown")

@dp.message(cmd("group"))
async def setGroup_user(message: types.message):
    meta = message.text.split()[1:]
    if len(meta) < 2: return await message.reply("❗️*Использование: /group <tgid> <group>*", parse_mode="Markdown")

    tgid = int(meta[0])
    level = meta[1]

    data = check_user_in_db(message.from_user.id)[1]
    data2 = check_user_in_db(tgid)[1]
    groups = json.load(open("groups.json"))
    groups_list = list(groups.keys())
    data_weight = groups[data]["weight"] if data != "super" else 10 ** 5
    if data not in groups_list and data != "super":
        return await message.reply("❌ *Не удалось получить вашу группу.*", parse_mode="Markdown")

    if tgid == message.from_user.id: return message.reply("❌ *Вы не можете использовать это на себе!*", parse_mode="Markdown")

    if data == "super" or message.text.split()[0][1:] in groups[data]["allowed_super_commands"]:
        if not check_user_in_db(tgid):
            return await message.reply("⚠️ *Этот пользователь не зарегистрирован.*", parse_mode="Markdown")
        if level not in groups_list:
            return await message.reply("❌ *Такой группы не существует!*", parse_mode="Markdown")
        if data2 == "super" or groups[level]["weight"] >= data_weight:
            return await message.reply("⚠️ *Вы не можете установить пользователю эту группу!*", parse_mode="Markdown")
        set_group(tgid, level)
        await message.reply(f"✅ *Вы установили пользователю TG-{tgid} группу {level.upper()}!*", parse_mode="Markdown")
    else:
        return await message.reply("⚠️ *Эта команда Вам не разрешена.*", parse_mode="Markdown")

@dp.message(cmd("profile"))
async def check_profile(message: types.message):
    if not check_user_in_db(message.from_user.id): return
    msg = "🔥 *Ваш профиль*\n"
    msg += f"Группа: `{check_user_in_db(message.from_user.id)[1]}`\n\n"
    msg += "Доступные команды:\n"

    group = check_user_in_db(message.from_user.id)[1]

    if group != "super":
        groups = json.load(open("groups.json"))
        allowed_commands = groups[group]["allowed_commands"]
    else:
        allowed_commands = ['*']
    for i in allowed_commands:
        msg += f"— {i}\n".replace("*", "\\*")

    await message.reply(msg, parse_mode="Markdown")

@dp.message()
async def rconCommand(message: types.message):
    if message.text[:2].lower() != "r ": return await message.reply(f"⚠️ *Неизвестная команда!*", parse_mode="Markdown")

    tgid = message.from_user.id
    data = check_user_in_db(tgid)

    if not data: return await message.reply(f"❌ *Вам нельзя использовать эти команды*!", parse_mode="Markdown")

    try:
        with MCRcon(host, password, port) as mcr:
            command = message.text[2:]

            if is_command_allowed(command, tgid, "data.db") == Exception:
                return await message.reply("❌ *Не удалось получить вашу группу.*", parse_mode="Markdown")
            elif not is_command_allowed(command, tgid, "data.db"):
                return await message.reply("⚠️ *Эта команда Вам не разрешена.*", parse_mode="Markdown")

            response = mcr.command(command)

            formatted_resp = remove_minecraft_color_codes(response)
            await message.reply(f"✉️ Ответ от сервера:\n\n{formatted_resp.strip('\n')}")
    except Exception as e:
        print(e)
        return await message.reply("⚠️ *Rcon недоступен!*", parse_mode="Markdown")

async def main():
    print("Клиент Rcon запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
