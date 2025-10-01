from chatbot import Chatbot
from config import GROQ_API_KEY, PDF_FOLDER, DATA_FOLDER

def print_header():
    print("\n" + "="*60)
    print("           CUSTOMER SERVICE CHATBOT v2.0")
    print("           (Now with Conversation Memory)")
    print("="*60)


def print_main_menu():
    print("\n" + "─"*60)
    print("MAIN MENU")
    print("─"*60)
    print("1. Chat with AI Assistant (Contextual)")
    print("2. Order Management")
    print("3. Clear Conversation Context")
    print("4. View Context Stats")
    print("5. Exit")
    print("─"*60)

def print_order_menu():
    print("\n" + "─"*60)
    print("ORDER MANAGEMENT")
    print("─"*60)
    print("1. View Order Details")
    print("2. Process Refund")
    print("3. Back to Main Menu")
    print("─"*60)

def chat_mode(bot: Chatbot):
    print("\n" + "="*60)
    print("CHAT MODE - AI Assistant (Contextual)")
    print("="*60)
    print("I'll remember our conversation for better assistance!")
    print("Ask me anything! I can help with:")
    print("  • Privacy policy questions")
    print("  • Terms of service inquiries")
    print("  • General customer service")
    print("\nType 'back' to return to main menu")
    print("Type 'stats' to see conversation statistics")
    print("─"*60 + "\n")
    
    while True:
        user_input = input("You: ").strip()        
        if not user_input:
            continue
        
        if user_input.lower() in ['back', 'menu', 'exit']:
            print("\nReturning to main menu...\n")
            break
        
        if user_input.lower() == 'stats':
            stats = bot.get_context_stats()
            print(f"\n📊 Conversation Statistics:")
            print(f"  • Messages in memory: {stats['messages_in_memory']}")
            print(f"  • Total messages: {stats['total_messages']}")
            print(f"  • Has summary: {'Yes' if stats['has_summary'] else 'No'}")
            print(f"  • Started at: {stats['created_at']}\n")
            continue
        
        print(f"\nBot: {bot.chat(user_input)}\n")

def order_details_mode(bot: Chatbot):
    print("\n" + "─"*60)
    print("ORDER DETAILS LOOKUP")
    print("─"*60)    
    order_id = input("\nEnter Order ID (or 'back' to return): ").strip()    
    if order_id.lower() in ['back', 'menu']:
        return
    if not order_id:
        print("Order ID cannot be empty!")
        return
    order_id = order_id.lstrip('#')
    print(bot.orders.format_order_response(order_id))
    input("\nPress Enter to continue...")

def refund_mode(bot: Chatbot):
    print("\n" + "─"*60)
    print("REFUND PROCESSING")
    print("─"*60)
    order_id = input("\nEnter Order ID for refund (or 'back' to return): ").strip()
    if order_id.lower() in ['back', 'menu']:
        return
    if not order_id:
        print("Order ID cannot be empty!")
        return
    order_id = order_id.lstrip('#')
    print(f"\nYou are about to process a refund for order #{order_id}")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm == 'yes':
        print(bot.orders.process_refund(order_id))
    else:
        print("Refund cancelled.")    
    input("\nPress Enter to continue...")

def order_management_mode(bot: Chatbot):
    while True:
        print_order_menu()
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            order_details_mode(bot)
        elif choice == '2':
            refund_mode(bot)
        elif choice == '3':
            print("\nReturning to main menu...\n")
            break
        else:
            print("Invalid choice! Please select 1-3.")

def clear_context(bot: Chatbot):
    """Clear conversation context"""
    print("\n" + "─"*60)
    print("CLEAR CONVERSATION CONTEXT")
    print("─"*60)
    confirm = input("\nAre you sure you want to clear the conversation memory? (yes/no): ").strip().lower()
    if confirm == 'yes':
        bot.clear_context()
        print("✓ Conversation context cleared successfully!")
    else:
        print("Operation cancelled.")
    input("\nPress Enter to continue...")

def view_context_stats(bot: Chatbot):
    """Display conversation statistics"""
    print("\n" + "="*60)
    print("CONVERSATION STATISTICS")
    print("="*60)
    
    stats = bot.get_context_stats()
    
    print(f"\n📊 Current Conversation:")
    print(f"  • Messages in memory: {stats['messages_in_memory']}")
    print(f"  • Total messages exchanged: {stats['total_messages']}")
    print(f"  • Conversation summary: {'Active' if stats['has_summary'] else 'None'}")
    print(f"  • Session started: {stats['created_at']}")
    
    print("\n💡 How it works:")
    print("  • I keep the last 10 message exchanges in full detail")
    print("  • Older messages are summarized to maintain context")
    print("  • This helps me understand your questions better!")
    
    input("\nPress Enter to continue...")


def main():
    print_header()
    bot = Chatbot(GROQ_API_KEY, PDF_FOLDER, DATA_FOLDER)
    
    print("\n✨ New Feature: I now remember our conversation!")
    print("This helps me provide more relevant and personalized responses.\n")
    
    while True:
        print_main_menu()
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            chat_mode(bot)
        elif choice == '2':
            order_management_mode(bot)
        elif choice == '3':
            clear_context(bot)
        elif choice == '4':
            view_context_stats(bot)
        elif choice == '5':
            print("\n" + "="*60)
            print("Thank you for using our service! Goodbye!")
            print("="*60 + "\n")
            break
        else:
            print("Invalid choice! Please select 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please check your configuration and try again.")