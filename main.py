import os
import logging
from keep_alive import keep_alive

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
        ConversationHandler, filters, CallbackQueryHandler
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure python-telegram-bot is properly installed.")
    exit(1)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SELECT_SERVICE, GET_LINK, GET_QUANTITY, CONFIRM_ORDER, WAIT_PAYMENT = range(5)

# Service list with proper pricing
service_list = {
    "1": {"name": "Facebook Likes + Followers", "price": 400},  # ₹400 per 1K
    "2": {"name": "Facebook PROFILE FOLLOWER", "price": 300},  # ₹300 per 1K
    "3": {"name": "Facebook Post Likes", "price": 99},         # ₹99 per 1K
    "4": {"name": "Facebook Reels Views", "price": 29},        # ₹29 per 1K
    "5": {"name": "Facebook Comments", "price": 350},          # ₹350 per 1K
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler - shows service menu with inline buttons"""
    try:
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        # Create inline keyboard buttons for service selection
        keyboard = [
            [InlineKeyboardButton("📱 Facebook Likes + Followers (₹400/1K)", callback_data="service_1")],
            [InlineKeyboardButton("👥 Facebook Profile Followers (₹300/1K)", callback_data="service_2")],
            [InlineKeyboardButton("👍 Facebook Post Likes (₹99/1K)", callback_data="service_3")],
            [InlineKeyboardButton("📹 Facebook Reels Views (₹29/1K)", callback_data="service_4")],
            [InlineKeyboardButton("💬 Facebook Comments (₹350/1K)", callback_data="service_5")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "🤖 Welcome to *PUREGRAPHICS GROW* — your trusted SMM Service Bot! 🚀\n\n"
            "📋 Please choose a service by clicking a button below:\n\n"
            "🎯 All services are high-quality and delivered within 0-6 hours\n"
            "💎 Professional SMM solutions at competitive prices\n"
            "🔒 Secure payment process with UPI\n\n"
            "👇 Select your service:"
        )
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return SELECT_SERVICE
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again with /start")
        return ConversationHandler.END

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        callback_data = query.data
        
        if callback_data == "help":
            help_text = (
                "🤖 *PUREGRAPHICS GROW - Quick Help*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "📋 *HOW TO ORDER*\n"
                "1️⃣ Click on a service above\n"
                "2️⃣ Provide Facebook link\n"
                "3️⃣ Enter quantity needed\n"
                "4️⃣ Confirm and pay via UPI\n\n"
                "💰 *PRICING*\n"
                "• All prices shown per 1,000 units\n"
                "• Minimum order: 1,000 units\n"
                "• Maximum order: 100,000 units\n\n"
                "🚀 *DELIVERY*\n"
                "• Processing starts immediately\n"
                "• Delivery within 0-6 hours\n"
                "• High-quality engagement guaranteed\n\n"
                "📞 Contact support for assistance!"
            )
            await query.edit_message_text(help_text, parse_mode='Markdown')
            
            # Add back button
            keyboard = [[InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            return SELECT_SERVICE
            
        elif callback_data == "back_to_start":
            # Show service menu again
            keyboard = [
                [InlineKeyboardButton("📱 Facebook Likes + Followers (₹400/1K)", callback_data="service_1")],
                [InlineKeyboardButton("👥 Facebook Profile Followers (₹300/1K)", callback_data="service_2")],
                [InlineKeyboardButton("👍 Facebook Post Likes (₹99/1K)", callback_data="service_3")],
                [InlineKeyboardButton("📹 Facebook Reels Views (₹29/1K)", callback_data="service_4")],
                [InlineKeyboardButton("💬 Facebook Comments (₹350/1K)", callback_data="service_5")],
                [InlineKeyboardButton("❓ Help", callback_data="help")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = (
                "🤖 Welcome to *PUREGRAPHICS GROW* — your trusted SMM Service Bot! 🚀\n\n"
                "📋 Please choose a service by clicking a button below:\n\n"
                "🎯 All services are high-quality and delivered within 0-6 hours\n"
                "💎 Professional SMM solutions at competitive prices\n"
                "🔒 Secure payment process with UPI\n\n"
                "👇 Select your service:"
            )
            await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            return SELECT_SERVICE
            
        elif callback_data.startswith("service_"):
            # Extract service number
            service_num = callback_data.split("_")[1]
            
            if service_num not in service_list:
                await query.edit_message_text("❌ Invalid service selection. Please try again.")
                return SELECT_SERVICE

            context.user_data['service'] = service_list[service_num]
            service_name = service_list[service_num]['name']
            service_price = service_list[service_num]['price']
            
            logger.info(f"User {user.id} selected service: {service_name}")
            
            await query.edit_message_text(
                f"✅ You selected: *{service_name}*\n"
                f"💰 Price: ₹{service_price} per 1,000\n\n"
                "📎 Please send the link to your Facebook page/post:\n\n"
                "⚠️ Make sure the link is valid and accessible!\n"
                "💡 Send the link as a message (not a button click)",
                parse_mode='Markdown'
            )
            return GET_LINK
            
        elif callback_data == "confirm_yes":
            # User confirmed order via button
            return await process_payment_screen(update, context, user)
            
        elif callback_data == "confirm_no":
            # User cancelled order via button
            logger.info(f"User {user.id} cancelled order via button")
            await query.edit_message_text(
                "❌ Order cancelled successfully.\n\n"
                "🔄 Type /start to place a new order\n"
                "📞 Contact support if you need assistance"
            )
            return ConversationHandler.END
            
        elif callback_data == "payment_done":
            # User claims to have paid
            service_name = context.user_data['service']['name']
            quantity = context.user_data['quantity']
            total_price = context.user_data['total_price']
            
            logger.info(f"User {user.id} reported payment completed for {service_name}")
            
            # Create support button
            keyboard = [
                [InlineKeyboardButton("📞 Contact Support", url="https://t.me/PURE_GRAPHICS")],
                [InlineKeyboardButton("🆕 New Order", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            completion_message = (
                "✅ ORDER CONFIRMED!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🎊 Amazing! Your order is confirmed and processing\n\n"
                "📋 ORDER SUMMARY\n"
                f"🆔 Service: {service_name}\n"
                f"📈 Quantity: {quantity:,}\n"
                f"💰 Investment: ₹{total_price}\n\n"
                "🚀 WHAT HAPPENS NEXT\n"
                "• Order processing starts immediately\n"
                "• Professional team handles your request\n"
                "• Completion timeline: 24-48 hours maximum\n"
                "• Results will appear on your profile!\n\n"
                "💎 PREMIUM SERVICE GUARANTEE\n"
                "• 100% organic engagement delivery\n"
                "• Zero risk to your account safety\n"
                "• Quality results that last longer\n\n"
                "📞 NEED ASSISTANCE\n"
                "Contact @PURE_GRAPHICS for instant support!\n\n"
                "🌟 Thank you for choosing PUREGRAPHICS GROW!\n"
                "💪 Your social media growth begins NOW!"
            )
            await query.edit_message_text(completion_message, reply_markup=reply_markup)
            return ConversationHandler.END
            
        elif callback_data == "payment_cancel":
            # User cancelled payment
            logger.info(f"User {user.id} cancelled payment")
            await query.edit_message_text(
                "❌ Payment cancelled.\n\n"
                "🔄 Type /start to place a new order\n"
                "📞 Contact support if you need assistance"
            )
            return ConversationHandler.END
            
        elif callback_data == "contact_support":
            # Show support information
            support_message = (
                "📞 *CUSTOMER SUPPORT*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "🕐 *Available 24/7*\n"
                "📱 WhatsApp: Contact via Telegram\n"
                "✉️ Email: puregraphics.grow@support\n"
                "⚡ Response time: Within 1 hour\n\n"
                "💡 *Common Issues*\n"
                "• Payment verification: Usually takes 2-5 minutes\n"
                "• Order processing: Starts immediately after payment\n"
                "• Delivery time: 0-6 hours maximum\n\n"
                "🔄 Type /start to place a new order"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Payment", callback_data="back_to_payment")],
                [InlineKeyboardButton("🆕 New Order", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(support_message, parse_mode='Markdown', reply_markup=reply_markup)
            return WAIT_PAYMENT
            
        elif callback_data == "back_to_payment":
            # Return to payment screen
            return await process_payment_screen(update, context, user)
            
        return SELECT_SERVICE
    except Exception as e:
        logger.error(f"Error in button_callback: {e}")
        await query.edit_message_text("❌ Something went wrong. Please try again with /start")
        return ConversationHandler.END

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle legacy text service selection (fallback)"""
    try:
        choice = update.message.text.strip()
        user = update.effective_user
        
        if choice not in service_list:
            await update.message.reply_text(
                "❌ Invalid option. Please use the buttons above or type /start to see the menu again."
            )
            return SELECT_SERVICE

        context.user_data['service'] = service_list[choice]
        service_name = service_list[choice]['name']
        service_price = service_list[choice]['price']
        
        logger.info(f"User {user.id} selected service: {service_name}")
        
        await update.message.reply_text(
            f"✅ You selected: *{service_name}*\n"
            f"💰 Price: ₹{service_price} per 1,000\n\n"
            "📎 Please send the link to your Facebook page/post:\n\n"
            "⚠️ Make sure the link is valid and accessible!",
            parse_mode='Markdown'
        )
        return GET_LINK
    except Exception as e:
        logger.error(f"Error in select_service: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again or type /start")
        return ConversationHandler.END

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Facebook link input"""
    try:
        link = update.message.text.strip()
        user = update.effective_user
        
        # Basic URL validation
        if not (link.startswith('http://') or link.startswith('https://')):
            await update.message.reply_text(
                "❌ Please enter a valid URL starting with http:// or https://\n"
                "Example: https://facebook.com/yourpage"
            )
            return GET_LINK
        
        if 'facebook.com' not in link and 'fb.com' not in link:
            await update.message.reply_text(
                "❌ Please enter a valid Facebook URL\n"
                "The link should contain 'facebook.com' or 'fb.com'"
            )
            return GET_LINK
        
        context.user_data['link'] = link
        logger.info(f"User {user.id} provided link: {link}")
        
        await update.message.reply_text(
            "✅ Link received successfully!\n\n"
            "📊 Now enter the *quantity* you want:\n"
            "• Minimum: 1,000\n"
            "• Maximum: 100,000\n"
            "• Examples: 1000, 2500, 5000\n\n"
            "💡 Enter numbers only (like 1000):",
            parse_mode='Markdown'
        )
        return GET_QUANTITY
    except Exception as e:
        logger.error(f"Error in get_link: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again or type /start")
        return ConversationHandler.END

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quantity input and calculate pricing"""
    try:
        user = update.effective_user
        quantity_text = update.message.text.strip().replace(',', '')
        
        try:
            quantity = int(quantity_text)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid input. Please enter numbers only.\n"
                "Examples: 1000, 2500, 5000"
            )
            return GET_QUANTITY
        
        if quantity < 1000:
            await update.message.reply_text(
                "❗ Minimum order quantity is 1000.\n"
                "Please enter a higher number."
            )
            return GET_QUANTITY
        
        if quantity > 100000:
            await update.message.reply_text(
                "❗ Maximum order quantity is 100,000.\n"
                "Please enter a lower number or contact support for bulk orders."
            )
            return GET_QUANTITY

        context.user_data['quantity'] = quantity
        service = context.user_data['service']
        price_per_1k = service['price']
        total_price = max(1, int((quantity / 1000) * price_per_1k))
        context.user_data['total_price'] = total_price
        
        logger.info(f"User {user.id} ordered {quantity} of {service['name']} for ₹{total_price}")

        # Create confirmation buttons
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ Cancel Order", callback_data="confirm_no")],
            [InlineKeyboardButton("🔄 Start Over", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        summary = (
            "📋 *ORDER SUMMARY*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 Service: {service['name']}\n"
            f"🔗 Link: {context.user_data['link']}\n"
            f"📈 Quantity: {quantity:,}\n"
            f"💰 Rate: ₹{price_per_1k}/1K\n"
            f"💵 *Total Price: ₹{total_price}*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Please confirm your order:"
        )
        await update.message.reply_text(summary, parse_mode='Markdown', reply_markup=reply_markup)
        return CONFIRM_ORDER
    except Exception as e:
        logger.error(f"Error in get_quantity: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again or type /start")
        return ConversationHandler.END

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle order confirmation (legacy text method)"""
    try:
        response = update.message.text.strip().lower()
        user = update.effective_user
        
        if response == "confirm":
            return await process_payment_screen(update, context, user)
            
        elif response == "cancel":
            logger.info(f"User {user.id} cancelled order")
            await update.message.reply_text(
                "❌ Order cancelled successfully.\n\n"
                "🔄 Type /start to place a new order\n"
                "📞 Contact support if you need assistance"
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "❓ Please use the buttons above or type:\n"
                "✅ *Confirm* - to proceed with payment\n"
                "❌ *Cancel* - to cancel the order",
                parse_mode='Markdown'
            )
            return CONFIRM_ORDER
    except Exception as e:
        logger.error(f"Error in confirm_order: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again or type /start")
        return ConversationHandler.END

async def process_payment_screen(update, context, user):
    """Generate payment screen with UPI details and barcode"""
    try:
        total_price = context.user_data['total_price']
        service_name = context.user_data['service']['name']
        
        logger.info(f"User {user.id} confirmed order for {service_name}")
        
        # First send the payment details
        payment_message = (
            "🧾 *INVOICE GENERATED*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 Amount to Pay: *₹{total_price}*\n\n"
            "💰 *PAYMENT DETAILS*\n"
            "🔗 UPI ID: `7261012584@fam`\n"
            "📱 PhonePe/Google Pay/Paytm/BHIM supported\n"
            "💳 All UPI apps accepted\n\n"
            "📋 *PAYMENT INSTRUCTIONS*\n"
            "1️⃣ Copy the UPI ID: `7261012584@fam`\n"
            "2️⃣ Open your UPI app (PhonePe/GPay/Paytm)\n"
            "3️⃣ Send exactly ₹{} to the UPI ID\n".format(total_price) +
            "4️⃣ OR scan the QR code below\n"
            "5️⃣ Click 'I Have Paid' after payment\n\n"
            "⏰ Payment validity: 30 minutes\n"
            "🔒 Secure UPI payment gateway\n"
            "📞 24/7 support available"
        )
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(payment_message, parse_mode='Markdown')
        else:
            await update.message.reply_text(payment_message, parse_mode='Markdown')
        
        # Send the barcode image
        try:
            barcode_path = "attached_assets/IMG_3381_1751810377603.jpeg"
            if hasattr(update, 'callback_query') and update.callback_query:
                chat_id = update.callback_query.message.chat_id
                context_obj = update.callback_query
            else:
                chat_id = update.message.chat_id  
                context_obj = update.message
                
            with open(barcode_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption="📱 *QR CODE FOR PAYMENT*\n\nScan this QR code with any UPI app to pay ₹{}".format(total_price),
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.warning(f"Could not send barcode image: {e}")
            
        # Create payment confirmation buttons and send them
        keyboard = [
            [InlineKeyboardButton("✅ I Have Paid", callback_data="payment_done")],
            [InlineKeyboardButton("❌ Cancel Payment", callback_data="payment_cancel")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        button_message = "👇 *Click below after completing payment:*"
        
        if hasattr(update, 'callback_query') and update.callback_query:
            chat_id = update.callback_query.message.chat_id
            await context.bot.send_message(
                chat_id=chat_id,
                text=button_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(button_message, parse_mode='Markdown', reply_markup=reply_markup)
        
        return WAIT_PAYMENT
    except Exception as e:
        logger.error(f"Error in process_payment_screen: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again or type /start")
        return ConversationHandler.END

async def wait_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment confirmation"""
    try:
        user = update.effective_user
        message_text = update.message.text.strip().lower()
        
        if message_text == "paid":
            service_name = context.user_data['service']['name']
            quantity = context.user_data['quantity']
            total_price = context.user_data['total_price']
            
            logger.info(f"User {user.id} reported payment completed for {service_name}")
            
            completion_message = (
                "🎊 *ORDER RECEIVED SUCCESSFULLY!*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "✨ *Amazing! Your order is now in our premium queue*\n\n"
                "📋 *ORDER SUMMARY*\n"
                f"🆔 Service: {service_name}\n"
                f"📈 Quantity: {quantity:,}\n"
                f"💰 Investment: ₹{total_price}\n\n"
                "🚀 *WHAT HAPPENS NEXT?*\n"
                "• Your order will be processed immediately\n"
                "• Professional team will handle your request\n"
                "• Completion timeline: 24-48 hours maximum\n"
                "• Results will start appearing on your profile!\n\n"
                "💎 *PREMIUM SERVICE GUARANTEE*\n"
                "• 100% organic engagement delivery\n"
                "• Zero risk to your account safety\n"
                "• Quality results that last longer\n\n"
                "📞 *NEED ASSISTANCE?*\n"
                "Contact: @PURE_GRAPHICS\n"
                "Available 24/7 for instant support!\n\n"
                "🆕 Ready for more growth? Type /start\n\n"
                "🌟 Thank you for choosing PUREGRAPHICS GROW!\n"
                "💪 Your social media transformation begins NOW!"
            )
            await update.message.reply_text(completion_message, parse_mode='Markdown')
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "💳 Waiting for payment confirmation...\n\n"
                "❗ Please type *Paid* only after you've completed the payment\n"
                "🔄 If you need to restart, type /start\n"
                "❌ To cancel, type /cancel",
                parse_mode='Markdown'
            )
            return WAIT_PAYMENT
    except Exception as e:
        logger.error(f"Error in wait_payment: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again or type /start")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation handler"""
    try:
        user = update.effective_user
        logger.info(f"User {user.id} cancelled conversation")
        
        await update.message.reply_text(
            "❌ Operation cancelled successfully.\n\n"
            "🔄 Type /start to begin a new order\n"
            "📞 Need help? Contact @PURE_GRAPHICS\n\n"
            "Thank you for using PUREGRAPHICS GROW! 🚀"
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel: {e}")
        await update.message.reply_text("❌ Operation cancelled. Type /start to begin again.")
        return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = (
        "🤖 *PUREGRAPHICS GROW - Help*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 *AVAILABLE COMMANDS*\n"
        "• /start - Begin new order\n"
        "• /help - Show this help\n"
        "• /cancel - Cancel current operation\n\n"
        "💡 *HOW TO ORDER*\n"
        "1️⃣ Type /start\n"
        "2️⃣ Choose a service (1-5)\n"
        "3️⃣ Provide Facebook link\n"
        "4️⃣ Enter quantity\n"
        "5️⃣ Confirm and pay\n\n"
        "💰 *PAYMENT*\n"
        "• UPI payments only\n"
        "• Instant processing\n"
        "• Secure transactions\n\n"
        "📞 *SUPPORT*\n"
        "Contact @PURE_GRAPHICS for any assistance!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "❓ Unknown command.\n\n"
        "🔄 Type /start to place an order\n"
        "❓ Type /help for assistance\n"
        "❌ Type /cancel to stop current operation"
    )

def main():
    """Main function to run the bot"""
    # Start keep-alive server
    keep_alive()
    
    # Get bot token from environment variable
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'REPLACE_WITH_YOUR_BOT_TOKEN')
    
    if BOT_TOKEN == 'REPLACE_WITH_YOUR_BOT_TOKEN':
        logger.error("Bot token not found! Please set BOT_TOKEN environment variable.")
        print("❌ Error: Bot token not configured!")
        print("Please set BOT_TOKEN in your environment variables.")
        print("To get a bot token:")
        print("1. Message @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the token and add it to your environment variables")
        return
    
    try:
        # Create application
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Create conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SELECT_SERVICE: [
                    CallbackQueryHandler(button_callback),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, select_service)
                ],
                GET_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
                GET_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
                CONFIRM_ORDER: [
                    CallbackQueryHandler(button_callback),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)
                ],
                WAIT_PAYMENT: [
                    CallbackQueryHandler(button_callback),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, wait_payment)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )
        
        # Add handlers
        app.add_handler(conv_handler)
        app.add_handler(CommandHandler('help', help_command))
        app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        logger.info("🤖 PUREGRAPHICS GROW bot is starting...")
        print("🤖 PUREGRAPHICS GROW bot is running...")
        print("✅ Bot is ready to accept orders!")
        
        # Run the bot
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Failed to start bot: {e}")

if __name__ == '__main__':
    main()
