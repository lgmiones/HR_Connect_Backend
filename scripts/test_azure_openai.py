"""
Test Azure OpenAI API Connection and Keys
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from openai import AzureOpenAI
from app.core.config import settings
import time


def test_azure_openai_connection():
    """Test basic connection to Azure OpenAI"""
    print("=" * 60)
    print("🧪 Testing Azure OpenAI Connection")
    print("=" * 60)
    print()
    
    # Display current configuration (hide key)
    print("📋 Current Configuration:")
    print(f"   Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    print(f"   API Key: {settings.AZURE_OPENAI_API_KEY[:8]}...{settings.AZURE_OPENAI_API_KEY[-4:]}")
    print(f"   API Version: {settings.AZURE_OPENAI_API_VERSION}")
    print(f"   Deployment (Chat): {settings.AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"   Deployment (Embeddings): {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
    print()
    
    try:
        # Initialize client
        print("🔌 Connecting to Azure OpenAI...")
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        print("✅ Client initialized successfully")
        print()
        
        return client
    except Exception as e:
        print(f"❌ Failed to initialize client: {str(e)}")
        print()
        return None


def test_chat_completion(client):
    """Test chat completion (GPT-4)"""
    print("-" * 60)
    print("🤖 Test 1: Chat Completion (GPT)")
    print("-" * 60)
    
    try:
        print("Sending test message to GPT...")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful HR assistant."},
                {"role": "user", "content": "Say 'Hello! Azure OpenAI is working!' in a friendly way."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        elapsed = time.time() - start_time
        
        print(f"✅ Chat completion successful! (took {elapsed:.2f}s)")
        print(f"\n💬 Response:")
        print(f"   {response.choices[0].message.content}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Chat completion failed: {str(e)}")
        print()
        
        # Provide helpful error messages
        if "404" in str(e):
            print("💡 Possible issues:")
            print("   - Deployment name is incorrect")
            print(f"   - Check if '{settings.AZURE_OPENAI_DEPLOYMENT_NAME}' exists in Azure")
        elif "401" in str(e) or "403" in str(e):
            print("💡 Possible issues:")
            print("   - API key is incorrect or expired")
            print("   - Check your Azure OpenAI resource keys")
        elif "429" in str(e):
            print("💡 Issue:")
            print("   - Rate limit exceeded or quota reached")
        
        print()
        return False


def test_embeddings(client):
    """Test embeddings generation"""
    print("-" * 60)
    print("📊 Test 2: Embeddings Generation")
    print("-" * 60)
    
    try:
        print("Generating embeddings for test text...")
        start_time = time.time()
        
        response = client.embeddings.create(
            model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input="This is a test sentence for embedding generation."
        )
        
        elapsed = time.time() - start_time
        embedding = response.data[0].embedding
        
        print(f"✅ Embeddings generated successfully! (took {elapsed:.2f}s)")
        print(f"\n📈 Embedding details:")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Embeddings generation failed: {str(e)}")
        print()
        
        # Provide helpful error messages
        if "404" in str(e):
            print("💡 Possible issues:")
            print("   - Embedding deployment name is incorrect")
            print(f"   - Check if '{settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}' exists")
        elif "401" in str(e) or "403" in str(e):
            print("💡 Possible issues:")
            print("   - API key is incorrect")
        
        print()
        return False


def test_rate_limits(client):
    """Test multiple rapid requests to check rate limits"""
    print("-" * 60)
    print("⚡ Test 3: Rate Limits Check (3 rapid requests)")
    print("-" * 60)
    
    try:
        success_count = 0
        
        for i in range(3):
            print(f"   Request {i+1}/3...", end=" ")
            
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "user", "content": f"Count to {i+1}"}
                ],
                max_tokens=10
            )
            
            print("✅")
            success_count += 1
        
        print(f"\n✅ All {success_count}/3 requests successful!")
        print("   Your rate limits are working fine.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Rate limit test failed: {str(e)}")
        print()
        return False


def main():
    """Run all tests"""
    print()
    
    # Test connection
    client = test_azure_openai_connection()
    
    if not client:
        print("❌ Cannot proceed with tests - connection failed")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check your .env file has correct values")
        print("   2. Verify API key in Azure Portal")
        print("   3. Ensure endpoint URL is correct")
        print("   4. Check if resource is active in Azure")
        return
    
    # Run tests
    results = {
        "Connection": True,
        "Chat Completion": test_chat_completion(client),
        "Embeddings": test_embeddings(client),
        "Rate Limits": test_rate_limits(client)
    }
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print()
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 All tests passed! Your Azure OpenAI is configured correctly!")
        print()
        print("✅ You can now:")
        print("   - Use the chatbot with Azure OpenAI")
        print("   - Switch to Azure OpenAI embeddings if desired")
        print("   - Run: uvicorn app.main:app --reload")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print()
        print("🔧 Next steps:")
        print("   1. Fix the configuration in .env")
        print("   2. Verify your Azure OpenAI resource")
        print("   3. Run this test again")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()