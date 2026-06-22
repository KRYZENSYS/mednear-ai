"""Basic bot handlers: /start, /help, /menu."""

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
)

from app.config import settings
from app.database import db_manager
from app.database.enums import Language
from app.keyboards.inline import get_main_menu_keyboard
from app.keyboards.reply import get_contact_keyboard, get_remove_keyboard
from app.repositories import user_repository
from app.services.user import user_service
from app.utils.helpers import generate_referral_code
from app.utils.logger import logger

router = Router(name="start")


WELCOME_TEXTS = {
    Language.UZBEK: (
        "👋 <b>Assalomu alaykum, {name}!</b>\n\n"
        "🤖 Men <b>MedNear AI</b> — professional tibbiy yordamchi botiman.\n\n"
        "📋 Mening imkoniyatlarim:\n"
        "🔹 AI bilan tibbiy maslahat\n"
        "🔹 Alomatlarni tahlil qilish\n"
        "🔹 Dorilar haqida ma'lumot\n"
        "🔹 Eslatmalar va jadval\n"
        "🔹 Eng yaqin kasalxonalar\n"
        "🔹 Tibbiy yozuvlarni tahlil qilish (PDF)\n"
        "🔹 Ovozli xabarlarni tushunish\n\n"
        "💡 Boshlash uchun quyidagi tugmani bosing:"
    ),
    Language.RUSSIAN: (
        "👋 <b>Здравствуйте, {name}!</b>\n\n"
        "🤖 Я <b>MedNear AI</b> — профессиональный медицинский бот-помощник.\n\n"
        "📋 Мои возможности:\n"
        "🔹 Медицинские консультации с ИИ\n"
        "🔹 Анализ симптомов\n"
        "🔹 Информация о лекарствах\n"
        "🔹 Напоминания и расписание\n"
        "🔹 Ближайшие больницы\n"
        "🔹 Анализ медицинских записей (PDF)\n"
        "🔹 Понимание голосовых сообщений\n\n"
        "💡 Нажмите кнопку ниже для начала:"
    ),
    Language.ENGLISH: (
        "👋 <b>Hello, {name}!</b>\n\n"
        "🤖 I am <b>MedNear AI</b> — your professional medical assistant bot.\n\n"
        "📋 My capabilities:\n"
        "🔹 AI medical consultations\n"
        "🔹 Symptom analysis\n"
        "🔹 Medicine information\n"
        "🔹 Reminders and scheduling\n"
        "🔹 Nearby hospitals\n"
        "🔹 Medical records analysis (PDF)\n"
        "🔹 Voice message understanding\n\n"
        "💡 Press the button below to start:"
    ),
}


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_referral(
    message: Message,
    command: CommandStart.CommandObj,
    bot: Bot,
    state: FSMContext,
) -> None:
    """Handle /start with referral code.

    Args:
        message: Incoming message.
        command: Command object with args.
        bot: Bot instance.
        state: FSM context.
    """
    await cmd_start_handler(message, state, bot, command.args)


@router.message(CommandStart())
async def cmd_start_handler(
    message: Message,
    state: FSMContext,
    bot: Bot | None = None,
    referral_code: str | None = None,
) -> None:
    """Handle /start command.

    Args:
        message: Incoming message.
        state: FSM context.
        bot: Bot instance.
        referral_code: Optional referral code.
    """
    await state.clear()

    user = message.from_user
    if not user:
        await message.answer("❌ Error: Could not identify user.")
        return

    logger.info(f"Start command from telegram_id={user.id}, referral={referral_code}")

    try:
        async with db_manager.session() as session:
            db_user, created = await user_repository.get_or_create(
                session,
                telegram_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                language_code=user.language_code or "uz",
                referral_code=referral_code,
            )

            language = db_user.language if isinstance(db_user.language, Language) else Language(db_user.language)
            text = WELCOME_TEXTS.get(language, WELCOME_TEXTS[Language.UZBEK])
            text = text.format(name=user.first_name or "do'st")

        keyboard = get_main_menu_keyboard(language)

        if created:
            await message.answer(
                f"🎉 <b>Xush kelibsiz!</b>\n\n{text}",
                reply_markup=keyboard,
            )
            logger.info(f"New user registered: telegram_id={user.id}")
        else:
            await message.answer(
                f"👋 <b>Qaytib keldingiz!</b>\n\n{text}",
                reply_markup=keyboard,
            )
            logger.debug(f"Returning user: telegram_id={user.id}")

    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=get_remove_keyboard(),
        )


@router.message(Command("help"))
async def cmd_help_handler(message: Message) -> None:
    """Handle /help command.

    Args:
        message: Incoming message.
    """
    help_text = (
        "📚 <b>Yordam — MedNear AI</b>\n\n"
        "<b>Asosiy buyruqlar:</b>\n"
        "/start — Botni ishga tushirish\n"
        "/menu — Asosiy menyu\n"
        "/chat — AI bilan suhbat\n"
        "/symptom — Alomatlarni tekshirish\n"
        "/medicine — Dori qidirish\n"
        "/reminder — Eslatmalar\n"
        "/appointment — Qabulga yozilish\n"
        "/hospital — Kasalxona qidirish\n"
        "/profile — Profilim\n"
        "/settings — Sozlamalar\n"
        "/premium — Premium obuna\n"
        "/language — Tilni o'zgartirish\n"
        "/feedback — Fikr bildirish\n"
        "/cancel — Bekor qilish\n\n"
        "<b>Qo'shimcha imkoniyatlar:</b>\n"
        "🔹 Ovozli xabar yuboring — men tushunaman\n"
        "🔹 Rasm yuboring — tibbiy tahlil qilaman\n"
        "🔹 PDF yuboring — ma'lumotlarni o'qiyman\n"
        "🔹 Lokatsiya yuboring — yaqin kasalxonalarni topaman\n\n"
        "❓ Savollaringiz bo'lsa: @MedNearSupport"
    )

    await message.answer(help_text)


@router.message(Command("menu"))
async def cmd_menu_handler(message: Message, state: FSMContext) -> None:
    """Handle /menu command.

    Args:
        message: Incoming message.
        state: FSM context.
    """
    await state.clear()

    async with db_manager.session() as session:
        db_user = await user_repository.get_by_telegram_id(session, message.from_user.id)
        language = db_user.language if db_user else Language.UZBEK

    await message.answer(
        "📋 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=get_main_menu_keyboard(language),
    )


@router.message(Command("cancel"))
@router.callback_query(F.data == "cancel")
async def cmd_cancel_handler(event: Message | CallbackQuery, state: FSMContext) -> None:
    """Handle /cancel command.

    Args:
        event: Message or CallbackQuery.
        state: FSM context.
    """
    await state.clear()

    text = "❌ Bekor qilindi."
    if isinstance(event, Message):
        await event.answer(text, reply_markup=get_remove_keyboard())
    else:
        await event.answer(text, show_alert=False)
        try:
            await event.message.edit_text(text)
        except Exception:
            await event.message.answer(text, reply_markup=get_remove_keyboard())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle back to menu callback.

    Args:
        callback: Callback query.
        state: FSM context.
    """
    await state.clear()
    await callback.answer()

    async with db_manager.session() as session:
        db_user = await user_repository.get_by_telegram_id(session, callback.from_user.id)
        language = db_user.language if db_user else Language.UZBEK

    try:
        await callback.message.edit_text(
            "📋 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:",
            reply_markup=get_main_menu_keyboard(language),
        )
    except Exception:
        await callback.message.answer(
            "📋 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:",
            reply_markup=get_main_menu_keyboard(language),
        )