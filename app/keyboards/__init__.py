"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.enums import Language


def get_main_menu_keyboard(language: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    """Get main menu inline keyboard.

    Args:
        language: User language for button labels.

    Returns:
        Inline keyboard markup.
    """
    if language == Language.RUSSIAN:
        buttons = [
            [InlineKeyboardButton(text="💬 Чат с ИИ", callback_data="ai_chat"),
             InlineKeyboardButton(text="🤒 Симптомы", callback_data="symptom_check")],
            [InlineKeyboardButton(text="💊 Лекарства", callback_data="medicine_search"),
             InlineKeyboardButton(text="⏰ Напоминания", callback_data="reminders")],
            [InlineKeyboardButton(text="📅 Запись к врачу", callback_data="appointments"),
             InlineKeyboardButton(text="🏥 Больницы", callback_data="hospitals")],
            [InlineKeyboardButton(text="📄 PDF анализ", callback_data="pdf_analysis"),
             InlineKeyboardButton(text="🎤 Голос", callback_data="voice")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
             InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="💎 Premium", callback_data="premium"),
             InlineKeyboardButton(text="📞 Поддержка", callback_data="support")],
        ]
    elif language == Language.ENGLISH:
        buttons = [
            [InlineKeyboardButton(text="💬 AI Chat", callback_data="ai_chat"),
             InlineKeyboardButton(text="🤒 Symptoms", callback_data="symptom_check")],
            [InlineKeyboardButton(text="💊 Medicines", callback_data="medicine_search"),
             InlineKeyboardButton(text="⏰ Reminders", callback_data="reminders")],
            [InlineKeyboardButton(text="📅 Appointments", callback_data="appointments"),
             InlineKeyboardButton(text="🏥 Hospitals", callback_data="hospitals")],
            [InlineKeyboardButton(text="📄 PDF Analysis", callback_data="pdf_analysis"),
             InlineKeyboardButton(text="🎤 Voice", callback_data="voice")],
            [InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
             InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton(text="💎 Premium", callback_data="premium"),
             InlineKeyboardButton(text="📞 Support", callback_data="support")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="💬 AI Chat", callback_data="ai_chat"),
             InlineKeyboardButton(text="🤒 Alomatlar", callback_data="symptom_check")],
            [InlineKeyboardButton(text="💊 Dorilar", callback_data="medicine_search"),
             InlineKeyboardButton(text="⏰ Eslatmalar", callback_data="reminders")],
            [InlineKeyboardButton(text="📅 Qabul", callback_data="appointments"),
             InlineKeyboardButton(text="🏥 Kasalxonalar", callback_data="hospitals")],
            [InlineKeyboardButton(text="📄 PDF tahlil", callback_data="pdf_analysis"),
             InlineKeyboardButton(text="🎤 Ovoz", callback_data="voice")],
            [InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
             InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
            [InlineKeyboardButton(text="💎 Premium", callback_data="premium"),
             InlineKeyboardButton(text="📞 Yordam", callback_data="support")],
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard.

    Returns:
        Inline keyboard with language options.
    """
    buttons = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(language: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    """Get back button keyboard.

    Args:
        language: User language.

    Returns:
        Inline keyboard with back button.
    """
    back_text = {
        Language.UZBEK: "⬅️ Orqaga",
        Language.RUSSIAN: "⬅️ Назад",
        Language.ENGLISH: "⬅️ Back",
    }
    buttons = [[InlineKeyboardButton(text=back_text.get(language, back_text[Language.UZBEK]), callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_keyboard(language: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    """Get yes/no confirmation keyboard.

    Args:
        language: User language.

    Returns:
        Confirmation keyboard.
    """
    yes_text = {
        Language.UZBEK: "✅ Ha",
        Language.RUSSIAN: "✅ Да",
        Language.ENGLISH: "✅ Yes",
    }
    no_text = {
        Language.UZBEK: "❌ Yo'q",
        Language.RUSSIAN: "❌ Нет",
        Language.ENGLISH: "❌ No",
    }
    buttons = [
        [
            InlineKeyboardButton(text=yes_text.get(language, yes_text[Language.UZBEK]), callback_data="confirm_yes"),
            InlineKeyboardButton(text=no_text.get(language, no_text[Language.UZBEK]), callback_data="confirm_no"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_premium_plans_keyboard() -> InlineKeyboardMarkup:
    """Get premium subscription plans keyboard.

    Returns:
        Premium plans keyboard.
    """
    buttons = [
        [InlineKeyboardButton(text="📅 1 oy — 25,000 so'm", callback_data="premium_1")],
        [InlineKeyboardButton(text="📅 3 oy — 65,000 so'm", callback_data="premium_3")],
        [InlineKeyboardButton(text="📅 12 oy — 200,000 so'm", callback_data="premium_12")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="premium_stars")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard(language: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    """Get settings keyboard.

    Args:
        language: User language.

    Returns:
        Settings keyboard.
    """
    if language == Language.UZBEK:
        buttons = [
            [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="change_language")],
            [InlineKeyboardButton(text="🔔 Bildirishnomalar", callback_data="toggle_notifications")],
            [InlineKeyboardButton(text="🌙 Tungi rejim", callback_data="toggle_theme")],
            [InlineKeyboardButton(text="🗑 Hisobni o'chirish", callback_data="delete_account")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")],
        ]
    elif language == Language.RUSSIAN:
        buttons = [
            [InlineKeyboardButton(text="🌐 Сменить язык", callback_data="change_language")],
            [InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")],
            [InlineKeyboardButton(text="🌙 Темная тема", callback_data="toggle_theme")],
            [InlineKeyboardButton(text="🗑 Удалить аккаунт", callback_data="delete_account")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="🌐 Change Language", callback_data="change_language")],
            [InlineKeyboardButton(text="🔔 Notifications", callback_data="toggle_notifications")],
            [InlineKeyboardButton(text="🌙 Dark Theme", callback_data="toggle_theme")],
            [InlineKeyboardButton(text="🗑 Delete Account", callback_data="delete_account")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_menu")],
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_hospital_filter_keyboard(language: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    """Get hospital filter keyboard.

    Args:
        language: User language.

    Returns:
        Hospital filter keyboard.
    """
    if language == Language.UZBEK:
        buttons = [
            [InlineKeyboardButton(text="🏥 Kasalxona", callback_data="hospital_type_hospital"),
             InlineKeyboardButton(text="🏨 Klinika", callback_data="hospital_type_clinic")],
            [InlineKeyboardButton(text="💊 Dorixona", callback_data="hospital_type_pharmacy"),
             InlineKeyboardButton(text="🔬 Laboratoriya", callback_data="hospital_type_laboratory")],
            [InlineKeyboardButton(text="🦇 Stomatologiya", callback_data="hospital_type_dental"),
             InlineKeyboardButton(text="👁 Optika", callback_data="hospital_type_optical")],
            [InlineKeyboardButton(text="📍 Yaqin atrofdagilar", callback_data="hospital_nearby")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="🏥 Hospital", callback_data="hospital_type_hospital"),
             InlineKeyboardButton(text="🏨 Clinic", callback_data="hospital_type_clinic")],
            [InlineKeyboardButton(text="💊 Pharmacy", callback_data="hospital_type_pharmacy"),
             InlineKeyboardButton(text="🔬 Laboratory", callback_data="hospital_type_laboratory")],
            [InlineKeyboardButton(text="🦇 Dental", callback_data="hospital_type_dental"),
             InlineKeyboardButton(text="👁 Optical", callback_data="hospital_type_optical")],
            [InlineKeyboardButton(text="📍 Nearby", callback_data="hospital_nearby")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_menu")],
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)