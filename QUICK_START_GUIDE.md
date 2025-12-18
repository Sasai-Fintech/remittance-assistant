# 🚀 Remittance Assistant - Quick Start Guide

## 📁 Project Structure

```
remittance-assistant/
├── backend/
│   ├── agent/
│   │   └── graph.py                    # LangGraph workflow (to be updated)
│   └── engine/
│       └── chat.py                     # ✅ UPDATED: Remittance system instructions
│
├── mcp-remittance/
│   └── src/
│       ├── remittance/                 # ✅ NEW MODULE
│       │   ├── __init__.py
│       │   └── countries.py            # ✅ NEW: get_receiving_countries, get_exchange_rate
│       ├── core/
│       │   └── server.py               # ✅ UPDATED: Register remittance tools
│       └── config/
│           └── settings.py             # ✅ UPDATED: Remittance endpoints
│
└── frontend/
    ├── components/
    │   ├── RemittanceWidgets.tsx       # ✅ UPDATED: New widget actions
    │   └── widgets/
    │       ├── CountrySelector.tsx     # ✅ NEW WIDGET
    │       └── ExchangeRateCard.tsx    # ✅ NEW WIDGET
    └── app/
        └── page.tsx                    # ✅ UPDATED: Remittance suggestions
```

## 🔧 Configuration Required

### 1. Environment Variables (.env)
```bash
# Sasai API Credentials
SASAI_ENVIRONMENT=sandbox
SASAI_USERNAME=64543532-3dee-43bc-b42e-d6b503f7fbdb
SASAI_PASSWORD=iW8I*0bZ
SASAI_PIN=OcXNch0pf3OKT+SD9xpM3qVoL6sDV2boAVWQjPj4H1+9VJhg4GyBsqC8Hu/x06YA50wxknXQqlIF5BFnd98zALxZOCX1i+xoPHuXdNn2Xqai/rBBeQf4N5Bq3r0JoOoyWUO954T4/3Ax2K57flYn0vntFglo8gJGfSSvPk8PJaCaVHDWir3VFfGJ2/vR59gqt7C+QeMkEMIhba89KGdHmSybdzZ7DjW7T4IjIkVIcpOTD/KhWGLovRuO7ptMI8u5gXp9ut/ZK+4PnD17N0XNxYXZXVk4SHbp784Sl3lKbpAwE5YZEP79rmAt723xJuz/KEPatOocyFN7sV2j/C+WVg==
SASAI_USER_REFERENCE_ID=eb89baad-302c-4a56-84b4-13607cfda5af

# API Configuration
BASE_URL=https://sandbox.sasaipaymentgateway.com

# RAG Service
RAG_SERVICE_URL=https://sandbox.sasaipaymentgateway.com/rag/api/retriever
RAG_TENANT_ID=sasai
RAG_TENANT_SUB_ID=sasai-sub
RAG_KNOWLEDGE_BASE_ID=remittance-faq-kb
RAG_PROVIDER_CONFIG_ID=azure-openai-llm-gpt-4o-mini

# MongoDB
MONGODB_URI=mongodb+srv://sasairagengine:j3ugUjql4I60TY52@sandbox.detzo.mongodb.net/?retryWrites=true&w=majority&appName=sandbox
MONGODB_DB_NAME=remittance-assistant-dev

# Token Manager
USE_TOKEN_MANAGER=true

# MCP Server
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_TRANSPORT=http
MCP_HTTP_TRANSPORT=sse
```

### 2. Kubernetes ConfigMap
Already configured in:
`azure-ecocash-assistant/config-repo/k8s/configmaps/remittance-assistant-mcp-remittance.dev.yaml`

## 🏃‍♂️ Running the Project

### Terminal 1: Start MCP Server
```bash
cd remittance-assistant/mcp-remittance
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

Expected output:
```
🚀 MCP Server started on http://0.0.0.0:8001
📡 Transport: SSE (Server-Sent Events)
🔧 Registered tools:
  - generate_authentication_token
  - get_receiving_countries
  - get_exchange_rate
  - retrieve_remittance_faq
  - create_support_ticket
  ...
```

### Terminal 2: Start Backend (LangGraph Agent)
```bash
cd remittance-assistant/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.api:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 3: Start Frontend (Next.js)
```bash
cd remittance-assistant/frontend
npm install  # or pnpm install
npm run dev  # or pnpm dev
```

Expected output:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in 2.3s
```

### Open Browser
Navigate to: `http://localhost:3000`

## 🧪 Testing the Flow

### Test 1: Basic Exchange Rate Check

1. **Start Conversation**
   - Click "Check Exchange Rates" button
   - OR type: "Check exchange rates"

2. **Expected Result:**
   ```
   Bot: "You're sending money from South Africa 🇿🇦 (ZAR).
   Which country would you like to send money to?"
   
   [Country Selector Widget appears]
   ```

3. **Select Country**
   - Choose "🇿🇼 Zimbabwe (USD)"
   - Click "Check Exchange Rate"

4. **Expected Result:**
   ```
   Bot: "Great! Here are the current rates for sending ZAR to Zimbabwe 🇿🇼..."
   
   [Exchange Rate Card Widget displays with all details]
   ```

### Test 2: Direct Country Specification

1. **Type Message:**
   ```
   "How much to send 500 ZAR to Kenya?"
   ```

2. **Expected Result:**
   - Skips country selector
   - Directly shows Exchange Rate Card for Kenya
   - Amount: ZAR 500 (not default 100)

### Test 3: Multiple Countries

1. **Type Message:**
   ```
   "Compare rates for Nigeria and India"
   ```

2. **Expected Result:**
   - Shows Exchange Rate Card for Nigeria (NGN)
   - Shows Exchange Rate Card for India (INR)

### Test 4: Shona Language

1. **Switch Language:**
   - Click language switcher
   - Select "Shona (sn)"

2. **Expected Result:**
   - Suggestions appear in Shona:
     - "Tarisa mari yekuchinjana"
     - "Tumira mari kuZimbabwe"
     - "Bvunza nezvekutumira mari"
     - "Wana rubatsiro"

3. **Type Message (Shona):**
   ```
   "Ndiri kuda kutumira mari kuZimbabwe"
   ```

4. **Expected Result:**
   - Bot responds in Shona
   - Shows country selector or exchange rate

## 🔍 Debugging

### Check MCP Server Logs
```bash
# In MCP server terminal
# Look for:
[GET_RECEIVING_COUNTRIES] Tool called
[GET_RECEIVING_COUNTRIES] Fetching countries from: https://sandbox...
[GET_RECEIVING_COUNTRIES] Found 22 receiving countries from South Africa

[GET_EXCHANGE_RATE] Tool called: ZW (USD), amount=100.0
[GET_EXCHANGE_RATE] Getting rate: ZA->'ZW' (100.0 ZAR)
[GET_EXCHANGE_RATE] Found 2 product options
```

### Check Backend Logs
```bash
# In backend terminal
# Look for:
[CHAT_NODE] Executing with thread_id: ...
[CHAT_NODE] Detected language: en
[CHAT_NODE] Loaded 8 tools from MCP server
🟡 [3/4] TOOL(S) DECIDED BY AGENT: get_receiving_countries
```

### Check Frontend Console
```bash
# In browser DevTools Console
# Look for:
[RemittanceWidgets] Rendering country selector with 22 countries
[RemittanceWidgets] Rendering exchange rate card with 2 products
```

### Common Issues

#### Issue 1: "No tools loaded from MCP server"
**Solution:**
- Check MCP server is running on port 8001
- Verify `MCP_SERVER_URL=http://localhost:8001/mcp` in .env
- Restart backend server

#### Issue 2: "Failed to generate authentication token"
**Solution:**
- Verify Sasai credentials in .env
- Check `SASAI_USERNAME`, `SASAI_PASSWORD`, `SASAI_PIN`, `SASAI_USER_REFERENCE_ID`
- Test manually: `curl https://sandbox.sasaipaymentgateway.com/bff/v2/auth/token`

#### Issue 3: Widget not displaying
**Solution:**
- Check browser console for errors
- Verify tool name matches: `get_receiving_countries`, `get_exchange_rate`
- Check `useCopilotAction` registration in `RemittanceWidgets.tsx`
- Ensure widget imports are correct

#### Issue 4: "Cannot parse result"
**Solution:**
- Check MCP tool return format
- Verify API response structure
- Add console.log in widget render function
- Check for JSON parsing errors

## 📊 API Endpoints to Test Manually

### 1. Get Auth Token
```bash
curl --location 'https://sandbox.sasaipaymentgateway.com/bff/v2/auth/token' \
--header 'Content-Type: application/json' \
--data '{
    "username": "64543532-3dee-43bc-b42e-d6b503f7fbdb",
    "password": "iW8I*0bZ"
}'
```

### 2. Get Countries (with token)
```bash
curl --location 'https://sandbox.sasaipaymentgateway.com/remittance/v1/master/country?currentUpdatedAt=0' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer YOUR_TOKEN_HERE'
```

### 3. Get Exchange Rate (with token)
```bash
curl --location 'https://sandbox.sasaipaymentgateway.com/remittance/v1/product/exchange/rate' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer YOUR_TOKEN_HERE' \
--data '{
    "sendingCountry": "ZA",
    "receivingCountry": "ZW",
    "sendingCurrency": "ZAR",
    "receivingCurrency": "USD",
    "amount": 100.0,
    "receive": false
}'
```

## 📱 Supported Destination Countries

From South Africa (ZAR), you can send to:

1. 🇧🇩 Bangladesh (BDT)
2. 🇧🇼 Botswana (BWP)
3. 🇧🇮 Burundi (BIF)
4. 🇨🇲 Cameroon (XAF)
5. 🇨🇳 China (CNY)
6. 🇨🇩 Congo, DR (USD)
7. 🇪🇹 Ethiopia (ETB)
8. 🇬🇭 Ghana (GHS)
9. 🇮🇳 India (INR)
10. 🇰🇪 Kenya (KES)
11. 🇱🇸 Lesotho (LSL)
12. 🇲🇼 Malawi (MWK)
13. 🇳🇬 Nigeria (NGN)
14. 🇵🇰 Pakistan (PKR)
15. 🇵🇭 Philippines (PHP)
16. 🇷🇼 Rwanda (RWF)
17. 🇸🇳 Senegal (XOF)
18. 🇸🇴 Somalia (USD)
19. 🇹🇿 Tanzania (TZS)
20. 🇺🇬 Uganda (UGX)
21. 🇿🇲 Zambia (ZMW)
22. 🇿🇼 Zimbabwe (USD)

## 🎯 Key Features Status

| Feature | Status | Notes |
|---------|--------|-------|
| **Get Receiving Countries** | ✅ Complete | MCP tool + Widget |
| **Get Exchange Rate** | ✅ Complete | MCP tool + Widget |
| **Country Selector Widget** | ✅ Complete | With flags & currencies |
| **Exchange Rate Card** | ✅ Complete | Shows all details |
| **Multi-language Support** | ✅ Complete | English & Shona |
| **Context-aware Suggestions** | ✅ Complete | Remittance-focused |
| **Token Management** | ✅ Complete | Auto-generate & refresh |
| **Support Tickets** | ✅ Complete | Human-in-the-loop |
| **RAG FAQ Service** | ⚠️ Partial | Config ready, needs KB content |
| **Generate Quote** | ❌ Pending | Future implementation |
| **Transfer Summary** | ❌ Pending | Future implementation |

## 🚦 Success Criteria

Your implementation is successful when:

✅ User can click "Check Exchange Rates"
✅ Country selector widget appears with 22 countries
✅ User can select a country
✅ Exchange rate card displays with accurate data
✅ Multiple delivery options shown
✅ Transfer limits displayed
✅ All fees transparent (transfer fee, VAT, total)
✅ Suggestions update based on context
✅ Shona language switch works
✅ No console errors in browser
✅ No errors in MCP server logs
✅ No errors in backend logs

## 📞 Support

For issues or questions:
1. Check logs (MCP server, backend, frontend)
2. Review API responses with curl
3. Verify environment variables
4. Check widget registration
5. Test with different countries/amounts

## 🎉 Next Steps

After successful testing:

1. **Deploy to Dev Environment**
   - Update Kubernetes configs
   - Deploy MCP server
   - Deploy backend
   - Deploy frontend

2. **Implement Remaining Flows**
   - Generate Quote (Flow 2)
   - Transfer Summary (Flow 3)
   - Enhanced FAQ (Flow 4)

3. **Add More Features**
   - Save favorite destinations
   - Rate alerts/notifications
   - Transfer history tracking
   - Receipt generation

4. **Optimize Performance**
   - Cache country list
   - Optimize API calls
   - Add loading states
   - Error recovery

---

**Status:** ✅ Ready for testing!
**Version:** 1.0.0
**Last Updated:** December 16, 2025
