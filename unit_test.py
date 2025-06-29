import send
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
        who, what = b.provider.get_who_what(update, context)
        destination = b.provider.get_destination(update, context)
        return await b.provider.send(destination,
                                     send.MESSAGE,
                                     f"You [{who}] said '{what}'")

    b.add(trigger.ON_MESSAGE, you_said)
    return await b.act(update, context)

