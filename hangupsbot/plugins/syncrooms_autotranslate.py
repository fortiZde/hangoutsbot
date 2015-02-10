import hangups
import goslate

from hangups.ui.utils import get_conv_name

gs = goslate.Goslate()


def _initialise(Handlers, bot=None):
    Handlers.register_handler(_translate_message, type="sending")
    return ['roomlanguage']


def _translate_message(bot, broadcast_list, context):
    if context and "autotranslate" in context:
        print(len(broadcast_list))
        _autotranslate = context["autotranslate"]
        origin_language = _get_room_language(bot, _autotranslate["conv_id"])
        for send in broadcast_list:
            target_conversation_id = send[0]
            response = send[1]
            target_language = _get_room_language(bot, target_conversation_id)
            if origin_language != target_language:
                print("AUTOTRANSLATE(): translating {} to {}".format(origin_language, target_language))
                translated = gs.translate(_autotranslate["event_text"], target_language)
                if _autotranslate["event_text"] != translated:
                    # mutate the original response by reference
                    response.extend([
                        hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                        hangups.ChatMessageSegment('(' + translated + ')')])


def _get_room_language(bot, conversation_id, default="en"):
    syncroom_language = bot.conversation_memory_get(conversation_id, 'syncroom_language')
    if syncroom_language is None:
        return default
    else:
        return syncroom_language


def roomlanguage(bot, event, *args):
    language_map = gs.get_languages()

    language = " ".join(args)

    if not language:
        try:
            bot.send_message_parsed(
                event.conv,
                '<i>syncroom "{}" language is {}</i>'.format(
                    get_conv_name(event.conv),
                    language_map[_get_room_language(bot, event.conv_id)]))
        except KeyError:
            pass
        return

    for iso_language in language_map:
        text_language = language_map[iso_language]
        if language.lower() in text_language.lower() or language == iso_language.upper():
            bot.conversation_memory_set(event.conv_id, 'syncroom_language', iso_language)
            bot.send_message_parsed(
                event.conv,
                '<i>syncroom "{}" language set to {}</i>'.format(
                    get_conv_name(event.conv),
                    text_language))
            break