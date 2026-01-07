#!/bin/bash

# Test script for conversation endpoint
# Usage: ./test-conversation-endpoint.sh <conversation_id> <jwt_token>

CONV_ID=${1:-"7c68ae22-5399-42cd-bab3-117958a48aff"}
TOKEN=${2}

if [ -z "$TOKEN" ]; then
    echo "❌ Error: JWT token required"
    echo "Usage: $0 <conversation_id> <jwt_token>"
    echo ""
    echo "To get your token:"
    echo "1. Open browser DevTools (F12)"
    echo "2. Go to Application/Storage > Cookies"
    echo "3. Copy the value of 'access_token' cookie"
    exit 1
fi

echo "🧪 Testing Conversation Endpoint"
echo "================================"
echo "Conversation ID: $CONV_ID"
echo "Token: ${TOKEN:0:20}..."
echo ""

echo "📡 Sending request..."
curl -v "http://localhost:8000/api/v1/messages/conversations/$CONV_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  2>&1 | tee /tmp/conversation-test.log

echo ""
echo "================================"
echo "✅ Test complete. Full output saved to: /tmp/conversation-test.log"
