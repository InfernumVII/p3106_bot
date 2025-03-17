import asyncio
import logging
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatMemberUpdated
)
from parse_group import parse_group





# Initialize MongoDB client
client = AsyncIOMotorClient(MONGOURL)
db = client['p3106']
users_collection = db['users']
queue_collection = db['queues']

SUBJECTS = {
    "ОПД": 7,
    "Программирование": 8,
    "Базы данных": 4
}

TEXTS = {
    'en': {
        'subjects': {
            'ОПД': 'OPD',
            'Программирование': 'Programming',
            'Базы данных': 'Databases'
        },
        'menu': "Your ISU number: {}\nYour full name: {}\n\n🎓 Bot for managing the queue for submitting laboratory work",
        'welcome_back': "Welcome back! Your ISU number: {}\nYour full name: {}\n\n🎓 Bot for managing laboratory work queue",
        'register_queue': "📝 Register in queue",
        'view_queue': "📋 View queue",
        'welcome_new': "Welcome to the queue management system!\nRegistration is required to use the bot.",
        'start_registration': "📝 Start registration",
        'enter_isu': "Please enter your ISU number (6 digits):",
        'try_again': "↩️ Try again",
        'invalid_isu': "❌ Invalid ISU number format. Please enter 6 digits.",
        'isu_not_found': "❌ ISU number not found in the group.",
        'confirm': "✅ Confirm",
        'enter_again': "↩️ Enter again",
        'isu_confirm': "You entered ISU number: {}\nIs this correct?",
        'registration_complete': "✅ Registration completed successfully!\nYour ISU number: {}\nYour full name: {}\n\n🎓 Now you can use the bot to manage laboratory work queue",
        'back': "↩️ Back",
        'select_subject': "Select subject:",
        'enter_lab_number': "Enter laboratory work number for {} (from 1 to {}):",
        'subject_error': '❌ You are already in the queue',
        'invalid_lab_number': "❌ Invalid laboratory work number. Enter a number from 1 to {}:",
        'send_proof': "Send a screenshot of completed work or GitHub repository link:",
        'invalid_proof': "❌ Please send a screenshot or GitHub/GitLab link",
        'queue_entry_sent': "✅ Your request has been sent for admin review.\nPlease wait for confirmation.",
        'to_main_menu': "↩️ To main menu",
        'new_queue_entry': "New queue entry!\nStudent: {}\nISU: {}\nSubject: {}\nLab: {}\n",
        'select_action': "Select action:",
        'approve': "✅ Approve",
        'reject': "❌ Reject",
        'approved': "✅ Your queue entry has been approved, lab {} for subject {}",
        'rejected': "❌ Your queue entry has been rejected, lab {} for subject {}",
        'select_subject_view': "Select subject to view queue:",
        'queue_for': "📋 Queue for {}:\n\n",
        'queue_text': "{}. {} - Lab {}\n",
        'queue_empty': "Queue is empty",
        'refresh': "🔄 Refresh",
        'remove_from_queue': "❌ Remove from queue",
        'select_student': "Select student to remove from queue:",
        'select_student_2': "Select student:",
        'removed_from_queue': "❌ You have been removed from queue for lab {} in subject {}.",
        'ended_in_queue': "❌ You have been sent to end of the queue in subject {}.",
        'ok': "🆗",
        'message_hidden': "Message hidden",
        'select_language': "🌐 Select language / Выберите язык:",
        'language_set': "✅ Language set to English",
        'chat_error': "❌ Error: Admin chat is not configured. Contact the administrator.",
        'admin_req': "You do not have administrator rights!",
        'queue_update': 'Queue updated 😊',
        'delete_me': 'Get out of the queue 😊',
        'to_end': '📋 Send yourself to the end of the queue',
        'deleted': '✅ You have removed yourself from the queue',
        'send_to_the_end': '🔄 Send student to end of the queue'
    },
    'ru': { 
        'subjects': {
            'ОПД': 'ОПД',
            'Программирование': 'Программирование',
            'Базы данных': 'Базы данных'
        },
        'menu': "Ваш номер ИСУ: {}\nВаши ФИО: {}\n\n🎓 Бот для управления очередью на сдачу лабораторных работ",
        'welcome_back': "С возвращением! Ваш номер ИСУ: {}\nВаши ФИО: {}\n\n🎓 Бот для управления очередью на сдачу лабораторных работ",
        'register_queue': "📝 Зарегистрироваться в очереди",
        'view_queue': "📋 Посмотреть очередь",
        'welcome_new': "Добро пожаловать в систему управления очередью!\nДля использования бота необходимо зарегистрироваться.",
        'start_registration': "📝 Начать регистрацию",
        'enter_isu': "Пожалуйста, введите ваш номер ИСУ (6 цифр):",
        'try_again': "↩️ Попробовать снова",
        'invalid_isu': "❌ Некорректный формат номера ИСУ. Необходимо ввести 6 цифр.",
        'isu_not_found': "❌ Номер ИСУ не найден в группе.",
        'confirm': "✅ Подтвердить",
        'enter_again': "↩️ Ввести заново",
        'isu_confirm': "Вы ввели номер ИСУ: {}\nВсё верно?",
        'registration_complete': "✅ Регистрация успешно завершена!\nВаш номер ИСУ: {}\nВаши ФИО: {}\n\n🎓 Теперь вы можете использовать бота для управления очередью на сдачу лабораторных работ",
        'back': "↩️ Назад",
        'select_subject': "Выберите предмет:",
        'enter_lab_number': "Введите номер лабораторной работы по предмету {} (от 1 до {}):",
        'subject_error': "❌ Вы уже в очереди",
        'invalid_lab_number': "❌ Некорректный номер лабораторной работы. Введите число от 1 до {}:",
        'send_proof': "Отправьте скриншот выполненной работы или ссылку на GitHub репозиторий:",
        'invalid_proof': "❌ Пожалуйста, отправьте скриншот или ссылку на GitHub/GitLab",
        'queue_entry_sent': "✅ Ваша заявка отправлена на проверку администратору.\nОжидайте подтверждения.",
        'to_main_menu': "↩️ В главное меню",
        'new_queue_entry': "Новая заявка в очередь!\nСтудент: {}\nИСУ: {}\nПредмет: {}\nЛаба: {}\n",
        'select_action': "Выберите действие:",
        'approve': "✅ Принять",
        'reject': "❌ Отклонить",
        'approved': "✅ Ваша заявка на добавление в очередь одобрена, лабораторная {} по предмету {}",
        'rejected': "❌ Ваша заявка на добавление в очередь отклонена, лабораторная {} по предмету {}",
        'select_subject_view': "Выберите предмет для просмотра очереди:",
        'queue_for': "📋 Очередь на {}:\n\n",
        'queue_text': "{}. {} - Лаба {}\n",
        'queue_empty': "Очередь пуста",
        'refresh': "🔄 Обновить",
        'remove_from_queue': "❌ Удалить из очереди",
        'select_student': "Выберите студента для удаления из очереди:",
        'select_student_2': "Выберите студента:",
        'removed_from_queue': "❌ Вы были удалены из очереди на сдачу лабораторной {} по предмету {}.",
        'ended_in_queue': "❌ Вы были отправлены в конец очереди по предмету {}.",
        'ok': "🆗",
        'message_hidden': "Сообщение скрыто",
        'select_language': "🌐 Select language / Выберите язык:",
        'language_set': "✅ Язык установлен на русский",
        'chat_error': "❌ Ошибка: админский чат не настроен. Обратитесь к администратору.",
        'admin_req': "У вас нет прав администратора!",
        'queue_update': "Очередь обновлена 😊",
        'delete_me': 'Удалиться из очереди 😊',
        'to_end': '📋 Отправить себя в конец очереди',
        'deleted': '✅ Вы удалили себя из очереди',
        'send_to_the_end': '🔄 Отправить человека в конец очереди'
    }
}
async def get_main_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['register_queue'], callback_data="register_queue")],
        [InlineKeyboardButton(text=TEXTS[lang]['view_queue'], callback_data="view_queue")]
    ])
'''
mainkeyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Зарегистрироваться в очереди", callback_data="register_queue")],
        [InlineKeyboardButton(text="📋 Посмотреть очередь", callback_data="view_queue")]
    ])
'''
keyboardok = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆗", callback_data="ok")],
    ])

class RegistrationStates(StatesGroup):
    waiting_for_isu = State()
    waiting_for_lab_number = State()
    waiting_for_proof = State()

dp = Dispatcher()

async def get_user_language(user_id: int) -> str:
    user = await users_collection.find_one({'user_id': user_id})
    return user.get('language', 'ru') if user else 'ru'

async def get_text(key: str, user_id: int) -> str:
    lang = await get_user_language(user_id)
    return TEXTS[lang].get(key, TEXTS['ru'][key])

@dp.message(Command("set_admin_chat"))
async def set_admin_chat(message: Message) -> None:
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора!")
        return
    
    await db.settings.update_one(
        {'setting': 'admin_chat'},
        {'$set': {'chat_id': message.chat.id}},
        upsert=True
    )
    
    await message.answer("✅ Этот чат установлен как админский чат для заявок.")

async def get_admin_chat_id() -> int:
    setting = await db.settings.find_one({'setting': 'admin_chat'})
    return setting['chat_id'] if setting else None


async def is_admin(user_id: int) -> bool:
    user = await users_collection.find_one({'user_id': user_id})
    return user and user.get('is_admin', False)

async def register_user(user_data: dict) -> bool:
    existing_user = await users_collection.find_one({'user_id': user_data['user_id']})
    if not existing_user or 'isu_number' not in existing_user:
        await users_collection.update_one(
            {'user_id': user_data['user_id']}, 
            {'$set': {**user_data, 'created_at': datetime.utcnow()}},
            upsert=True
        )
        #user_data['created_at'] = datetime.utcnow()
        #await users_collection.insert_one(user_data)
        return True
    return False

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="English 🇬🇧", callback_data="lang:en"),
            InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang:ru")
        ]
    ])
    
    await message.answer(TEXTS['ru']['select_language'], reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, state: FSMContext) -> None:
    language = callback.data.split(':')[1]
    user_id = callback.from_user.id
    
    await users_collection.update_one(
        {'user_id': user_id},
        {'$set': {'language': language}},
        upsert=True
    )
    
    await callback.message.edit_text(TEXTS[language]['language_set'])
    
    existing_user = await users_collection.find_one({'user_id': user_id})
    
    if existing_user and existing_user.get('isu_number'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[language]['register_queue'], 
                                callback_data="register_queue")],
            [InlineKeyboardButton(text=TEXTS[language]['view_queue'], 
                                callback_data="view_queue")]
        ])
        await callback.message.edit_text(
            TEXTS[language]['welcome_back'].format(
                existing_user['isu_number'], 
                existing_user['real_name']
            ),
            reply_markup=keyboard
        )
    else:

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[language]['start_registration'], 
                                callback_data="start_registration")]
        ])
        await callback.message.edit_text(
            TEXTS[language]['welcome_new'],
            reply_markup=keyboard
        )

@dp.callback_query(F.data == "start_registration")
async def start_registration(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    await state.set_state(RegistrationStates.waiting_for_isu)
    await state.update_data(message_id=callback.message.message_id)
    
    await callback.message.edit_text(
        TEXTS[lang]['enter_isu']
    )
    await callback.answer()

@dp.message(StateFilter(RegistrationStates.waiting_for_isu))
async def process_isu_number(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    isu_number = message.text.strip()
    state_data = await state.get_data()
    original_message_id = state_data.get('message_id')
    

    try:
        await message.delete()
    except:
        pass
    

    if not isu_number.isdigit() or len(isu_number) != 6:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]['try_again'], callback_data="start_registration")]
        ])
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=original_message_id,
            text=TEXTS[lang]['invalid_isu'],
            reply_markup=keyboard
        )
        return
    if isu_number not in parse_group().keys():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]['try_again'], callback_data="start_registration")]
        ])
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=original_message_id,
            text=TEXTS[lang]['isu_not_found'],
            reply_markup=keyboard
        )
        return
    

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=TEXTS[lang]['confirm'], callback_data=f"confirm_isu:{isu_number}"),
            InlineKeyboardButton(text=TEXTS[lang]['enter_again'], callback_data="start_registration")
        ]
    ])
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=original_message_id,
        text=TEXTS[lang]['isu_confirm'].format(isu_number),
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("confirm_isu:"))
async def confirm_registration(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    isu_number = callback.data.split(':')[1]
    

    user_data = {
        'user_id': callback.from_user.id,
        'username': callback.from_user.username,
        'full_name': callback.from_user.full_name,
        'isu_number': isu_number,
        'real_name': parse_group()[isu_number],
        'is_admin': False,
        'groups': []
    }
    

    await register_user(user_data)
    

    keyboard = await get_main_keyboard(lang)
    
    await callback.message.edit_text(
        TEXTS[lang]['registration_complete'].format(isu_number, user_data['real_name']),
        reply_markup=keyboard
    )
    

    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "register_queue")
async def register_queue_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[[InlineKeyboardButton(text=TEXTS[lang]['subjects'][subject], callback_data=f"subject:{subject}")] 
          for subject in SUBJECTS.keys()],
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(
        TEXTS[lang]['select_subject'],
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("subject:"))
async def select_lab_number(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    """Handle subject selection"""
    subject = callback.data.split(':')[1]
    count = await queue_collection.count_documents(
        {'subject': subject, 'status': 'approved', 'user_id':user_id})
    if count != 0:
        await callback.message.edit_text(
        TEXTS[lang]['subject_error'],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data="register_queue")]
        ])
        )
        return
    await state.update_data(subject=subject)
    await state.update_data(message_id=callback.message.message_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data="register_queue")]
    ])
    
    await state.set_state(RegistrationStates.waiting_for_lab_number)
    await callback.message.edit_text(
        TEXTS[lang]['enter_lab_number'].format(TEXTS[lang]['subjects'][subject], SUBJECTS[subject]),
        reply_markup=keyboard
    )
    await callback.answer()


@dp.message(StateFilter(RegistrationStates.waiting_for_lab_number))
async def process_lab_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    """Process manual lab number input"""
    try:
        await message.delete()
    except:
        pass

    state_data = await state.get_data()
    subject = state_data['subject']
    
    try:
        lab_number = int(message.text.strip())
        if lab_number < 1 or lab_number > SUBJECTS[subject]:
            raise ValueError
    except ValueError:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data=f"subject:{subject}")]
        ])
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=state_data['message_id'],
            text=TEXTS[lang]['invalid_lab_number'].format(SUBJECTS[subject]),
            reply_markup=keyboard
        )
        return

    await state.update_data(lab_number=lab_number)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data=f"subject:{subject}")]
    ])
    
    await state.set_state(RegistrationStates.waiting_for_proof)
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=state_data['message_id'],
        text=TEXTS[lang]['send_proof'],
        reply_markup=keyboard
    )

@dp.message(StateFilter(RegistrationStates.waiting_for_proof))
async def process_proof(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    user = await users_collection.find_one({'user_id': user_id})
    
    if not (message.photo or (message.text and ('github.com' in message.text.lower() or 'gitlab.com' in message.text.lower()))):
        try:
            await message.delete()
        except:
            pass
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data=f"subject:{state_data['subject']}")]
        ])
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=state_data['message_id'],
            text=TEXTS[lang]['invalid_proof'],
            reply_markup=keyboard
        )
        return


    queue_entry = {
        'user_id': user_id,
        'isu_number': user['isu_number'],
        'real_name': user['real_name'],
        'subject': state_data['subject'],
        'lab_number': state_data['lab_number'],
        'proof_message_id': message.message_id,
        'proof_chat_id': message.chat.id,
        'status': 'pending',
        'created_at': datetime.utcnow()
    }
    

    admin_chat_id = await get_admin_chat_id()
    if not admin_chat_id:
        await message.answer(TEXTS[lang]['chat_error'])
        return
    

    notification_text = (
        f"Новая заявка в очередь!\n"
        f"Студент: {user['real_name']}\n"
        f"ИСУ: {user['isu_number']}\n"
        f"Предмет: {state_data['subject']}\n"
        f"Лабораторная: {state_data['lab_number']}\n"
    )
    

    notification_message = await message.bot.send_message(
        admin_chat_id,
        notification_text,
    )
    

    forwarded_message = await message.forward(admin_chat_id)
    
    try:

        await message.delete()
    except:
        pass
    

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", 
                               callback_data=f"approve:{user_id}:{state_data['subject']}:{state_data['lab_number']}"),
            InlineKeyboardButton(text="❌ Отклонить", 
                               callback_data=f"reject:{user_id}:{state_data['subject']}:{state_data['lab_number']}")
        ]
    ])
    
    await message.bot.send_message(
        admin_chat_id,
        "Выберите действие:",
        reply_markup=keyboard
    )
    

    await queue_collection.insert_one(queue_entry)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['view_queue'], callback_data="view_queue")],
        [InlineKeyboardButton(text=TEXTS[lang]['to_main_menu'], callback_data="back_to_main")]
    ])
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=state_data['message_id'],
        text=TEXTS[lang]['queue_entry_sent'],
        reply_markup=keyboard
    )
    await state.clear()



@dp.callback_query(F.data.startswith("approve:"))
async def approve_queue_entry(callback: CallbackQuery):
    _, user_id, subject, lab_number = callback.data.split(':')
    user_id = int(user_id)
    lab_number = int(lab_number)
    lang = await get_user_language(user_id)
    if not await is_admin(callback.from_user.id):
        await callback.answer('У вас нет прав администратора!')
        return
    
    
    
    await queue_collection.update_one(
        {'user_id': user_id, 'subject': subject, 'lab_number': lab_number},
        {'$set': {'status': 'approved'}}
    )
    
    await callback.bot.send_message(
        user_id,
        TEXTS[lang]['approved'].format(lab_number, TEXTS[lang]['subjects'][subject]),
        reply_markup=keyboardok
    )
    
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ Заявка одобрена"
    )
    await callback.answer("Заявка одобрена")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_queue_entry(callback: CallbackQuery):
    _, user_id, subject, lab_number = callback.data.split(':')
    user_id = int(user_id)
    lab_number = int(lab_number)
    lang = await get_user_language(user_id)
    if not await is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора!")
        return
    
    
    
    await queue_collection.delete_one(
        {'user_id': user_id, 'subject': subject, 'lab_number': lab_number}
    )
    
    await callback.bot.send_message(
        user_id,
        TEXTS[lang]['rejected'].format(lab_number, TEXTS[lang]['subjects'][subject]),
        reply_markup=keyboardok
    )
    
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ Заявка отклонена"
    )
    await callback.answer("Заявка отклонена")

@dp.callback_query(F.data == "view_queue")
async def view_queue(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[[InlineKeyboardButton(text=TEXTS[lang]['subjects'][subject], callback_data=f"view_queue:{subject}")] 
          for subject in SUBJECTS.keys()],
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(
        TEXTS[lang]['select_subject_view'],
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("view_queue:"))
async def view_subject_queue(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)

    if len(callback.data.split(':')) > 2:
        subject = callback.data.split(':')[2]
    else:
        subject = callback.data.split(':')[1]
    
    queue = queue_collection.find(
        {'subject': subject, 'status': 'approved'}
    ).sort('created_at', 1)
    
    in_queue = False
    queue_text = TEXTS[lang]['queue_for'].format(TEXTS[lang]['subjects'][subject])
    i = 1
    async for entry in queue:
        queue_text += TEXTS[lang]['queue_text'].format(i, entry['real_name'], entry['lab_number'])
        if entry['user_id'] == user_id:
            in_queue = True
        i += 1
        
    if queue_text == TEXTS[lang]['queue_for'].format(TEXTS[lang]['subjects'][subject]):
        queue_text = TEXTS[lang]['queue_empty']
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['refresh'], callback_data=f"view_queue:{subject}")],
        [InlineKeyboardButton(text=TEXTS[lang]['back'], callback_data="view_queue")]
    ])

    if in_queue:
        keyboard.inline_keyboard.insert(1, [
            InlineKeyboardButton(text=TEXTS[lang]['delete_me'], callback_data=f"delete_me:{subject}")
        ])
        keyboard.inline_keyboard.insert(2, [
            InlineKeyboardButton(text=TEXTS[lang]['to_end'], callback_data=f"to_end:{subject}")
        ])
    
    if await is_admin(callback.from_user.id):
        keyboard.inline_keyboard.insert(0, [
            InlineKeyboardButton(text=TEXTS[lang]['remove_from_queue'], 
                               callback_data=f"remove_from_queue:{subject}")
        ])
        keyboard.inline_keyboard.insert(0, [
            InlineKeyboardButton(text=TEXTS[lang]['send_to_the_end'], 
                               callback_data=f"send_to_the_end:{subject}")
        ])
    
    if callback.message.text != queue_text.strip():
        await callback.message.edit_text(queue_text, reply_markup=keyboard)
    await callback.answer(TEXTS[lang]['queue_update'])


@dp.callback_query(F.data.startswith("send_to_the_end:"))
async def send_to_the_end_select(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    if not await is_admin(callback.from_user.id):
        await callback.answer(TEXTS[lang]['admin_req'])
        return
    
    subject = callback.data.split(':')[1]
    queue = queue_collection.find(
        {'subject': subject, 'status': 'approved'}
    ).sort('created_at', 1)
    
    keyboard = []
    i = 1
    async for entry in queue:
        keyboard.append([
            InlineKeyboardButton(
                text=TEXTS[lang]['queue_text'].format(i, entry['real_name'], entry['lab_number']), 
                callback_data=f"end_entry:{entry['user_id']}:{subject}:{entry['lab_number']}"
            )
        ])
        i += 1
    
    keyboard.append([InlineKeyboardButton(text=TEXTS[lang]['back'], 
                                        callback_data=f"view_queue:{subject}")])
    
    await callback.message.edit_text(
        TEXTS[lang]['select_student_2'],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("end_entry:"))
async def end_entry(callback: CallbackQuery):
    lang1 = await get_user_language(callback.from_user.id)
    if not await is_admin(callback.from_user.id):
        await callback.answer(TEXTS[lang1]['admin_req'])
        return
    
    _, user_id, subject, lab_number = callback.data.split(':')
    user_id = int(user_id)
    lang = await get_user_language(user_id)
    lab_number = int(lab_number)
    

    await queue_collection.update_one(
        {'user_id': user_id, 'subject': subject}, {'$set': { 'created_at': datetime.utcnow()}}
    )
    

    
    await callback.bot.send_message(
        user_id,
        TEXTS[lang]['ended_in_queue'].format(TEXTS[lang]['subjects'][subject]),
        reply_markup=keyboardok
    )
    

    await view_subject_queue(callback)

    #Добавить англ
    await callback.answer("Студент отправлен в конец очереди")

@dp.callback_query(F.data.startswith("to_end:"))
async def delete_me_from_queue(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)

    subject = callback.data.split(':')[1]
    
    await queue_collection.update_one(
        {'user_id': user_id, 'subject': subject},
        {'$set': {'created_at': datetime.utcnow()}}
    )
    

    await view_subject_queue(callback)

@dp.callback_query(F.data.startswith("delete_me:"))
async def delete_me_from_queue(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)

    subject = callback.data.split(':')[1]
    
    await queue_collection.delete_one(
        {'user_id': user_id, 'subject': subject}
    )

    await view_subject_queue(callback)
    await callback.answer()


@dp.callback_query(F.data.startswith("remove_from_queue:"))
async def remove_from_queue_select(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    if not await is_admin(callback.from_user.id):
        await callback.answer(TEXTS[lang]['admin_req'])
        return
    
    subject = callback.data.split(':')[1]
    queue = queue_collection.find(
        {'subject': subject, 'status': 'approved'}
    ).sort('created_at', 1)
    
    keyboard = []
    i = 1
    async for entry in queue:
        keyboard.append([
            InlineKeyboardButton(
                text=TEXTS[lang]['queue_text'].format(i, entry['real_name'], entry['lab_number']), 
                callback_data=f"remove_entry:{entry['user_id']}:{subject}:{entry['lab_number']}"
            )
        ])
        i += 1
    
    keyboard.append([InlineKeyboardButton(text=TEXTS[lang]['back'], 
                                        callback_data=f"view_queue:{subject}")])
    
    await callback.message.edit_text(
        TEXTS[lang]['select_student'],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@dp.callback_query(F.data == 'ok')
async def process_ok(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    try:
        await callback.message.delete()
    except:
        pass
    #Никогда не отработает
    await callback.answer(TEXTS[lang]['message_hidden'])

@dp.callback_query(F.data.startswith("remove_entry:"))
async def remove_queue_entry(callback: CallbackQuery):
    lang1 = await get_user_language(callback.from_user.id)
    if not await is_admin(callback.from_user.id):
        await callback.answer(TEXTS[lang1]['admin_req'])
        return
    
    _, user_id, subject, lab_number = callback.data.split(':')
    user_id = int(user_id)
    lang = await get_user_language(user_id)
    lab_number = int(lab_number)
    

    await queue_collection.delete_one(
        {'user_id': user_id, 'subject': subject, 'lab_number': lab_number}
    )
    

    await callback.bot.send_message(
        user_id,
        TEXTS[lang]['removed_from_queue'].format(lab_number, TEXTS[lang]['subjects'][subject]),
        reply_markup=keyboardok
    )
    

    await view_subject_queue(callback)

    #Добавить англ
    await callback.answer("Студент удален из очереди")


@dp.message(Command("make_admin"))
async def make_admin(message: Message) -> None:
    """Make user an admin by ISU number"""
  
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора!")
        return
    

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Использование: /make_admin <номер_ису>")
        return
    
    isu_number = args[1]
    user = await users_collection.find_one({'isu_number': isu_number})
    if not user:
        await message.answer("Пользователь с таким номером ИСУ не найден")
        return
    
  
    await users_collection.update_one(
        {'isu_number': isu_number},
        {'$set': {'is_admin': True}}
    )
    
    await message.answer(f"Пользователь {user['real_name']} назначен администратором")


@dp.message(Command("pardon_admin"))
async def make_admin(message: Message) -> None:
    """Make user an admin by ISU number"""
  
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора!")
        return
    

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Использование: /pardon_admin <номер_ису>")
        return
    
    isu_number = args[1]
    user = await users_collection.find_one({'isu_number': isu_number})
    if not user:
        await message.answer("Пользователь с таким номером ИСУ не найден")
        return
    
  
    await users_collection.update_one(
        {'isu_number': isu_number},
        {'$set': {'is_admin': False}}
    )
    
    await message.answer(f"У пользователя {user['real_name']} украли администратора")

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    user = await users_collection.find_one({'user_id': callback.from_user.id})
    lang = await get_user_language(callback.from_user.id)
    keyboard = await get_main_keyboard(lang)
    
    await callback.message.edit_text(
        TEXTS[lang]['menu'].format(user['isu_number'], user['real_name']),
        reply_markup=keyboard
    )
    await callback.answer()

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    try:
  
        await client.admin.command('ping')
        logging.info("Successfully connected to MongoDB!")
        
        logging.info("Starting bot...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            skip_updates=True
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        logging.info("Bot stopped!")
        await bot.session.close()
        client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user!")
        sys.exit(0)
