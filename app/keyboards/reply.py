"""Reply keyboards (request contact, location, etc.)."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


def get_contact_keyboard(text: str = "📞 Telefon raqamni yuboring") -> ReplyKeyboardMarkup:
    """Get keyboard with contact request button.

    Args:
        text: Button text.

    Returns:
        Reply keyboard markup.
    """
    button = KeyboardButton(text=text, request_contact=True)
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)


def get_location_keyboard(text: str = "📍 Lokatsiya yuboring") -> ReplyKeyboardMarkup:
    """Get keyboard with location request button.

    Args:
        text: Button text.

    Returns:
        Reply keyboard markup.
    """
    button = KeyboardButton(text=text, request_location=True)
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)


def get_phone_or_location_keyboard() -> ReplyKeyboardMarkup:
    """Get combined phone+location keyboard.

    Returns:
        Reply keyboard markup.
    """
    keyboard = [
        [KeyboardButton(text="📞 Telefon raqam", request_contact=True)],
        [KeyboardButton(text="📍 Lokatsiya", request_location=True)],
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_remove_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard.

    Returns:
        Reply keyboard remove marker.
    """
    return ReplyKeyboardRemove()


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Get persistent main reply keyboard.

    Returns:
        Reply keyboard markup.
    """
    keyboard = [
        [KeyboardButton(text="💬 AI Chat"), KeyboardButton(text="🤒 Alomatlar")],
        [KeyboardButton(text="💊 Dorilar"), KeyboardButton(text="⏰ Eslatmalar")],
        [KeyboardButton(text="🏥 Kasalxonalar"), KeyboardButton(text="📅 Qabul")],
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="⚙️ Sozlamalar")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)