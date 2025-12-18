# Remittance Assistant - User Journey Flow

## 🎯 Complete User Journey: Check Exchange Rates

### Starting Point: Home Screen

**User sees:**
```
👋 How can I help you today?

Suggested Actions:
[💸 Check Exchange Rates]
[💰 Generate a Quote]
[📊 Check Transfer Summary]
[❓ Ask a Question (FAQs)]
[🎫 Raise a Support Ticket]
```

---

## Flow 1: Check Exchange Rates from South Africa

### Step 1: User Initiates Exchange Rate Check

**User Action:**
- Clicks "Check Exchange Rates" button
- OR types: "Check exchange rates", "Show me rates", "How much to send to Zimbabwe?"

**System Response:**
```
Bot: "You're sending money from South Africa 🇿🇦 (ZAR).
Which country would you like to send money to?"
```

**Widget Displayed: CountrySelector**
```
┌─────────────────────────────────────────┐
│  💸 Select Destination Country          │
│  Choose where you want to send money    │
│                                          │
│  Destination Country                    │
│  [Choose a country... ▼]                │
│                                          │
│  [   Check Exchange Rate   ]            │
│  (Button disabled until selection)      │
└─────────────────────────────────────────┘
```

---

### Step 2: User Opens Country Dropdown

**User Action:**
- Clicks on the dropdown

**Dropdown Shows:**
```
┌─────────────────────────────────────────┐
│  🇧🇩 Bangladesh (BDT)                    │
│  🇧🇼 Botswana (BWP)                      │
│  🇧🇮 Burundi (BIF)                       │
│  🇨🇲 Cameroon (XAF)                      │
│  🇨🇳 China (CNY)                         │
│  🇨🇩 Congo, The Democratic Republic (USD)│
│  🇪🇹 Ethiopia (ETB)                      │
│  🇬🇭 Ghana (GHS)                         │
│  🇮🇳 India (INR)                         │
│  🇰🇪 Kenya (KES)                         │
│  🇱🇸 Lesotho (LSL)                       │
│  🇲🇼 Malawi (MWK)                        │
│  🇳🇬 Nigeria (NGN)                       │
│  🇵🇰 Pakistan (PKR)                      │
│  🇵🇭 Philippines (PHP)                   │
│  🇷🇼 Rwanda (RWF)                        │
│  🇸🇳 Senegal (XOF)                       │
│  🇸🇴 Somalia (USD)                       │
│  🇹🇿 Tanzania (TZS)                      │
│  🇺🇬 Uganda (UGX)                        │
│  🇿🇲 Zambia (ZMW)                        │
│  🇿🇼 Zimbabwe (USD)                      │
└─────────────────────────────────────────┘
```

---

### Step 3: User Selects a Country

**User Action:**
- Selects "🇿🇼 Zimbabwe (USD)"

**Dropdown Updates:**
```
┌─────────────────────────────────────────┐
│  💸 Select Destination Country          │
│  Choose where you want to send money    │
│                                          │
│  Destination Country                    │
│  [🇿🇼 Zimbabwe (USD) ▼]                 │
│                                          │
│  [   Check Exchange Rate   ]            │
│  (Button now enabled - blue)            │
└─────────────────────────────────────────┘
```

---

### Step 4: User Clicks "Check Exchange Rate"

**System Action:**
- Sends message: "Show me the exchange rate for Zimbabwe (ZW) in USD"
- Bot calls `get_exchange_rate` MCP tool
- Shows loading state

**Loading State:**
```
┌─────────────────────────────────────────┐
│  ⚙️ Calculating exchange rate...        │
└─────────────────────────────────────────┘
```

---

### Step 5: Exchange Rate Card Displays

**Bot Response:**
```
"Great! Here are the current rates for sending ZAR to Zimbabwe 🇿🇼.
You can send money via EcoCash (mobile money) or cash pickup at various locations."
```

**Widget Displayed: ExchangeRateCard**
```
┌─────────────────────────────────────────────────────────────┐
│  💵 Exchange Rate: South Africa → Zimbabwe                  │
│  Current rates and fees for your transfer                   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │        You Send        →         They Receive        │  │
│  │       ZAR 100.00                   USD 6.64          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│          ⭐ Best Rate via EcoCash                           │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ 📊 Exchange Rate │  │ 💵 Transfer Fee   │               │
│  │ 1 ZAR = 0.0664   │  │ ZAR 3.65          │               │
│  │      USD         │  │                   │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ Total to Pay     │  │ Delivery Method   │               │
│  │ ZAR 214.90       │  │ Mobile money      │               │
│  │                  │  │ EcoCash           │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  💡 Transfer Limits                                         │
│  Min: ZAR 30.12              Max: ZAR 12,048.19            │
│                                                              │
│  📋 Other delivery options:                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Ecocash/Econet/BancABC/Steward Bank branches        │  │
│  │ Rate: 0.0596                   Fee: ZAR 3.76        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│  💳 Rates are indicative and may change.                   │
│     Final rate confirmed at payment.                        │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 6: Context-Aware Suggestions Appear

**After Exchange Rate Displays:**
```
Suggested Next Actions:
[💸 Send Money]
[🔢 Check Different Amount]
[🌍 View Other Countries]
[❓ Ask About Fees]
```

---

## Alternative Scenarios

### Scenario A: User Specifies Country Directly

**User Message:**
"How much to send to Kenya?"

**System Response:**
- Skips country selector
- Directly calls `get_exchange_rate` for Kenya
- Shows ExchangeRateCard immediately

---

### Scenario B: User Asks About Specific Amount

**User Message:**
"How much will it cost to send ZAR 500 to Nigeria?"

**System Response:**
```
Bot: "Let me check the rates for sending ZAR 500 to Nigeria 🇳🇬..."
```

**Exchange Rate Card Shows:**
- Amount: ZAR 500 (not default 100)
- Calculated receiving amount in NGN
- Fees for ZAR 500
- Total to pay

---

### Scenario C: Comparing Multiple Countries

**User Message:**
"Show me rates for India and Pakistan"

**System Response:**
- Shows ExchangeRateCard for India (INR)
- Shows ExchangeRateCard for Pakistan (PKR)
- Allows easy comparison

---

## Error Handling

### Error Scenario 1: No Rates Available

**Widget Displayed:**
```
┌─────────────────────────────────────────┐
│  ℹ️ No exchange rates available for     │
│     this route at the moment.           │
│                                          │
│  Please try another destination or      │
│  contact support.                       │
└─────────────────────────────────────────┘
```

### Error Scenario 2: API Error

**Widget Displayed:**
```
┌─────────────────────────────────────────┐
│  ⚠️ Error loading exchange rates.       │
│     Please try again.                   │
└─────────────────────────────────────────┘
```

---

## Multi-Language Support (Shona Example)

### Shona Language Flow

**Home Screen (Shona):**
```
👋 Ndingakubatsira sei?

Zvinoitwa:
[💸 Tarisa mari yekuchinjana]
[💰 Gadzira quote]
[📊 Tarisa pfungwa yekutumira]
[❓ Bvunza mibvunzo]
[🎫 Tumira tikiti]
```

**Country Selection (Shona):**
```
Bot: "Uri kutumira mari kubva kuSouth Africa 🇿🇦 (ZAR).
Nyika ipi yaunoda kutumira mari?"
```

**Exchange Rate Display (Shona):**
```
Bot: "Zvakanaka! Heyi mari yekuchinjana yekutumira kuZimbabwe 🇿🇼.
Unogona kutumira mari ne-EcoCash (mobile money) kana cash pickup."
```

**Suggestions (Shona):**
```
[💸 Tumira mari]
[🔢 Shandura mari yakawanda]
[🌍 Tarisa nyika dzimwe]
[❓ Bvunza nezvemitengo]
```

---

## Data Flow Diagram

```
User Input
    │
    ├─→ "Check exchange rates"
    │       │
    │       ├─→ MCP Tool: get_receiving_countries
    │       │       │
    │       │       └─→ API: GET /remittance/v1/master/country
    │       │               │
    │       │               └─→ Widget: CountrySelector
    │       │
    │       └─→ User selects country (e.g., Zimbabwe)
    │
    └─→ "Show rate for Zimbabwe"
            │
            ├─→ MCP Tool: get_exchange_rate
            │       │
            │       └─→ API: POST /remittance/v1/product/exchange/rate
            │               │
            │               └─→ Widget: ExchangeRateCard
            │
            └─→ Context-aware suggestions appear
```

---

## Widget Component Structure

### CountrySelector Widget Props
```typescript
interface CountrySelectorProps {
  countries: Country[];
  onSelect?: (
    countryCode: string,
    currencyCode: string,
    countryName: string
  ) => void;
}
```

### ExchangeRateCard Widget Props
```typescript
interface ExchangeRateCardProps {
  sendingCountry: string;
  receivingCountry: string;
  sendingCurrency: string;
  receivingCurrency: string;
  products: ExchangeProduct[];
  requestInfo?: RequestInfo;
}
```

---

## Key Features Implemented

✅ **Intelligent Country Selection**
- All 22 destination countries supported
- Flag emojis for visual identification
- Currency codes displayed

✅ **Comprehensive Rate Display**
- Exchange rate clearly shown
- All fees transparent (transfer fee, VAT, surcharges)
- Total to pay prominently displayed
- Receiving amount highlighted

✅ **Multiple Delivery Options**
- Mobile money (EcoCash, M-Pesa, etc.)
- Cash pickup at various locations
- Bank transfers (where available)

✅ **Transfer Limits**
- Minimum and maximum amounts shown
- Helps users understand constraints

✅ **Best Rate Highlighting**
- Primary option marked with ⭐
- Alternative options still visible

✅ **Context-Aware Flow**
- Skips country selector if country mentioned
- Handles custom amounts
- Allows comparison of multiple destinations

✅ **Multi-Language Support**
- English and Shona (ChiShona)
- Consistent across all touchpoints

✅ **Error Handling**
- Graceful degradation
- Clear error messages
- Recovery suggestions

---

## Next User Actions

After viewing exchange rates, users can:

1. **Send Money** (Not yet implemented)
   - Proceed to actual money transfer
   - Enter recipient details
   - Confirm and pay

2. **Generate Quote** (Not yet implemented)
   - Save rate for later
   - Share quote with recipient
   - Compare quotes

3. **Check Different Amount**
   - Modify sending amount
   - See updated rates and fees

4. **View Other Countries**
   - Go back to country selector
   - Compare rates across destinations

5. **Ask Questions**
   - Transfer requirements
   - Processing time
   - Required documents
   - FAQ lookup via RAG

6. **Raise Support Ticket**
   - If issues arise
   - Human-in-the-loop confirmation
   - Ticket tracking

---

## Technical Implementation Notes

### MCP Tool Execution
1. User action triggers Copilot chat
2. LLM decides which MCP tool to call
3. MCP server executes tool (calls Sasai API)
4. Response returned to agent
5. Agent renders appropriate widget via `useCopilotAction`

### Widget Rendering
1. `useCopilotAction` registers tool name
2. When tool completes, `render` function called
3. Widget component receives parsed result
4. React renders widget inline in chat

### State Management
- Token managed by MCP server token manager
- User language stored in React context
- Conversation state managed by LangGraph
- Widget state local to components

---

**Status:** ✅ Flow 1 (Check Exchange Rates) Fully Implemented and Ready for Testing!
