from omni.omni import OMNI, trigger


async def run_vk_bot(update, context):
    from omni.providers.vk import VK
    vk = VK()
    b = OMNI(vk)
    return await test_bot(b, update, context)

async def run_tg_bot(update, context):
    from omni.providers.tg import TG
    tg = TG()
    b = OMNI(tg)
    return await test_bot(b, update, context)


async def test_bot(b, update, context):
    async def you_said(update, context):
        who, what = b.get_who_what(update, context)
        return await b.send_message(f"You [{who}] said '{what}'",
                                    update, context)

    buttons = ["Self-diagnostic", "Book the time"]

    async def send_default_menu(update, context):
        return await b.send_menu("Choose your destiny",
                                 buttons, update, context)

    async def you_pressed(update, context):
        who, what = b.get_who_what(update, context)
        return await b.send_message(f"You [{who}] pressed '{what}'",
                                    update, context)

    b.add(trigger.ON_MESSAGE, you_said)
    b.add(trigger.ON_MESSAGE, send_default_menu)
    b.register_menu_buttons(buttons)
    b.add(trigger.ON_MENU, you_pressed)
    return await b.act(update, context)

