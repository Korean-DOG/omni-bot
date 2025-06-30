import trigger
from omni import OMNI


async def run_vk_bot(update, context):
    from providers.vk import VK
    vk = VK()
    b = OMNI(vk)
    return await test_bot(b, update, context)

async def run_tg_bot(update, context):
    from providers.tg import TG
    tg = TG()
    b = OMNI(tg)
    return await test_bot(b, update, context)


async def test_bot(b, update, context):
    async def you_said(update, context):
        who, what = b.get_who_what(update, context)
        return await b.send_message(f"You [{who}] said '{what}'",
                                    update, context)

    buttons = ["Самообследование", "Запись на приём"]

    async def send_default_menu(update, context):
        return await b.send_menu("Выберите меню",
                                 buttons, update, context)

    b.add(trigger.ON_MESSAGE, you_said)
    b.add(trigger.ON_MESSAGE, send_default_menu)
    return await b.act(update, context)

