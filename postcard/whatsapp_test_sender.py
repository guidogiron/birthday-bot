from dotenv import load_dotenv
load_dotenv()

import requests
import os

# =============================================================================
# WHATSAPP BUSINESS CLOUD API - SIMPLE TEST SCRIPT
# =============================================================================

# Configuration — all values loaded from .env (see .env.example)
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
TARGET_PHONE_NUMBER = os.getenv('TARGET_PHONE_NUMBER')

def send_test_text_message():
    """Send a simple text message to test WhatsApp API"""
    
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": TARGET_PHONE_NUMBER,
        "type": "text",
        "text": {
            "body": "🎉 Hello! This is a test message from WhatsApp Business Cloud API! 🚀"
        }
    }
    
    print("=" * 70)
    print("📱 WHATSAPP API TEST")
    print("=" * 70)
    print(f"Sending message to: +{TARGET_PHONE_NUMBER}")
    print(f"Using Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")
    print("-" * 70)
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            
            print("✅ SUCCESS! Message sent successfully!")
            print(f"Message ID: {message_id}")
            print("-" * 70)
            print("Check your WhatsApp - you should receive the message! 📲")
            print("=" * 70)
            return True
            
        else:
            print(f"❌ ERROR! Status Code: {response.status_code}")
            print("-" * 70)
            print("Response:")
            print(response.text)
            print("-" * 70)
            
            # Common error explanations
            if response.status_code == 401:
                print("💡 Error 401: Invalid token. Check your WHATSAPP_API_TOKEN")
            elif response.status_code == 403:
                print("💡 Error 403: Permission denied. Make sure:")
                print("   - Your token has whatsapp_business_messaging permission")
                print("   - Your system user has access to the WhatsApp account")
            elif response.status_code == 404:
                print("💡 Error 404: Invalid Phone Number ID")
            
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        print("=" * 70)
        return False


def send_test_image_message(image_url):
    """Send an image message to test WhatsApp API
    
    Args:
        image_url: Public URL of an image (must be https)
    """
    
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": TARGET_PHONE_NUMBER,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": "🎨 Test image sent via WhatsApp Business Cloud API!"
        }
    }
    
    print("=" * 70)
    print("📱 WHATSAPP IMAGE TEST")
    print("=" * 70)
    print(f"Sending image to: +{TARGET_PHONE_NUMBER}")
    print(f"Image URL: {image_url}")
    print("-" * 70)
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'unknown')
            
            print("✅ SUCCESS! Image sent successfully!")
            print(f"Message ID: {message_id}")
            print("-" * 70)
            print("Check your WhatsApp for the image! 📸")
            print("=" * 70)
            return True
            
        else:
            print(f"❌ ERROR! Status Code: {response.status_code}")
            print("-" * 70)
            print("Response:")
            print(response.text)
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        print("=" * 70)
        return False


def verify_credentials():
    """Verify that credentials are set"""
    
    print("=" * 70)
    print("🔍 VERIFYING CREDENTIALS")
    print("=" * 70)
    
    issues = []
    
    if not WHATSAPP_API_TOKEN or WHATSAPP_API_TOKEN == 'YOUR_PERMANENT_TOKEN_HERE':
        issues.append("❌ WHATSAPP_API_TOKEN not set")
    else:
        print(f"✅ Token: {WHATSAPP_API_TOKEN[:20]}...")
    
    if not WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_PHONE_NUMBER_ID == 'YOUR_PHONE_NUMBER_ID_HERE':
        issues.append("❌ WHATSAPP_PHONE_NUMBER_ID not set")
    else:
        print(f"✅ Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")
    
    print(f"✅ Target Number: +{TARGET_PHONE_NUMBER}")
    print("=" * 70)
    
    if issues:
        print("\n⚠️  MISSING CREDENTIALS:")
        for issue in issues:
            print(f"  {issue}")
        print("\n📝 TO FIX:")
        print("Option 1: Set environment variables:")
        print("  export WHATSAPP_API_TOKEN='your_token_here'")
        print("  export WHATSAPP_PHONE_NUMBER_ID='your_phone_id_here'")
        print("\nOption 2: Edit this file and replace:")
        print("  WHATSAPP_API_TOKEN = 'your_actual_token'")
        print("  WHATSAPP_PHONE_NUMBER_ID = 'your_actual_phone_id'")
        print("=" * 70)
        return False
    
    return True


if __name__ == "__main__":
    # Verify credentials first
    if not verify_credentials():
        print("\n❌ Please set your credentials before running the test.")
        exit(1)
    
    print("\n")
    
    # Test 1: Send text message
    print("TEST 1: Sending text message...")
    text_success = send_test_text_message()
    
    print("\n")
    
    # Test 2: Send image (optional - using a public test image)
    if text_success:
        print("TEST 2: Sending image message...")
        test_image = "https://picsum.photos/800/600"  # Random test image
        image_success = send_test_image_message(test_image)
        
        if image_success:
            print("\n🎉 All tests passed! Your WhatsApp API is working perfectly!")
        else:
            print("\n⚠️  Text message worked but image failed. Check image URL accessibility.")
    else:
        print("\n⚠️  Text message test failed. Fix the issues above before testing images.")
    
    print("\n" + "=" * 70)
    print("📚 NEXT STEPS:")
    print("=" * 70)
    print("1. Check your WhatsApp (+919418791379) for the test messages")
    print("2. If successful, integrate this code into your main application")
    print("3. To send images from files, use the media upload API first")
    print("=" * 70)
