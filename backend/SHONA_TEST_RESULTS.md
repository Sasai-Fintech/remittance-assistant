# GPT-4o-mini Shona Language Test Results

**Test Date**: 2025-12-04 10:37:40
**Model**: gpt-4o-mini
**Total Tests**: 10

## Summary

- **Successful Tests**: 10/10
- **Average Understanding Score**: 3.00/5
- **Average Quality Score**: 3.00/5

## Basic Communication

### basic_greeting

**Prompt (Shona)**: `Mhoro`

**Expected**: Should understand greeting and respond appropriately

**Response (Basic)**:
```
Mhoro! Ungada kubatsira ne chii?
```

**Response (With System)**:
```
Mhoro! Ndingakubatsira sei nhasi?
```

**Language (Basic)**: Unknown

**Language (System)**: Unknown

**Understanding Score**: 1/5

**Quality Score**: 1/5

---

### basic_help

**Prompt (Shona)**: `Ndinoda rubatsiro`

**Expected**: Should understand request for help

**Response (Basic)**:
```
Chokwadi, ndiri pano kuti ndikubatsire! Unoda rubatsiro pane chii?
```

**Response (With System)**:
```
Zvakadini! Ndiri pano kuti ndikubatsire. Chii chiri kukunetsa?
```

**Language (Basic)**: Shona

**Language (System)**: Unknown

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

## Financial Queries

### balance_query_simple

**Prompt (Shona)**: `Ndinoda kuona mari yangu`

**Expected**: Should understand request to see balance/money

**Response (Basic)**:
```
Kuti uone mari yako, unogona kutevera matanho aya:

1. **Bvunza Banki Yako**: Kana uine account mubhengi, unogona kuenda kubhengi kana kushandisa internet banking kuti uone mari yako. 

2. **Mobile Banking**: Kana uine app ye mobile banking, unogona kuipinda uye uone balance yako.

3. **ATM**: Unogona kushandisa ATM kuti uone balance yako. Ingopinda mu ATM, uye sarudza "View Balance".

4. **Kunyora**: Kana uri kuda kuchengetedza mari yako, unogona kunyora zvese zvauri kushandisa uye mari yaunowana kuti uone kuti uri pamutemo here.

5. **Bvunza Chikwereti**: Kana uri pamutemo nezvekukwereta, unogona kubvunza kuti uwane ruzivo rwekuti uri kubhadhara sei.

Kana uine zvimwe zvawakada kuziva kana kubvunza, ndibvunze!
```

**Response (With System)**:
```
Unogona kutarisa balance yemari yako here? Ndiri pano kuti ndibatsire. Ndokumbirawo undipei chirevo chekuti ndikupe balance yako.
```

**Language (Basic)**: Mixed

**Language (System)**: Mixed

**Understanding Score**: 3/5

**Quality Score**: 4/5

---

### balance_query_formal

**Prompt (Shona)**: `Ndinoda kuona mari yemuhomwe yangu`

**Expected**: Should understand formal request for wallet balance

**Response (Basic)**:
```
Kuti uone mari yemuhomwe yako, unofanirwa kutarisa pane zvese zvauri kuchengetedza muhomwe yako, sekushandisa mari, kutenga, uye zvimwe zvinhu. Kana uchida kutarisa mari yako, unogona:

1. **Kujekesa mari irimo**: Tarisa mari yose iri muhomwe yako.
2. **Kunyora mari yawakatenga**: Ziva kuti wakashandisa marii uye pane chii.
3. **Kudzidza nezvemari**: Kana uchida kuwedzera mari yako, funga nezve nzira dzekuwana mari, sekushandira, kutengesa, kana kudyara.

Kana uri kuda rubatsiro rwakawanda kana kuti uri kutarisira chimwe chinhu, ndapota zivisa!
```

**Response (With System)**:
```
Unogona kuona mari yemuhomwe yako nekuti ndiri pano kuti ndibatsire. Ndokumbirawo undiudze kuti ndiite sei kuti ndikubatsire.
```

**Language (Basic)**: Shona

**Language (System)**: Shona

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

### transactions_query

**Prompt (Shona)**: `Ndinoda kuona zvishandiswa zvangu`

**Expected**: Should understand request to see transactions

**Response (Basic)**:
```
Zvinonzwika sekuti uri kuda kubatsira kana kutaurirana nezvezvishandiswa zvako. Unogona here kutipa rumwe ruzivo nezvazvo? Izvi zvinogona kusanganisira chii chaizvo chaunoda kuona kana kuti chii chaunoda kuziva nezvazvo. Ndiri pano kuti ndibatsire!
```

**Response (With System)**:
```
Nekuti unoda kuona zvishandiswa zvako, unogona kutarisa transaction history yako. Ndokumbira undiudze kana uchida kuti ndiite izvi, kana kuti pane chimwe chinhu chauri kuda kubatsira nacho.
```

**Language (Basic)**: Unknown

**Language (System)**: Mixed

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

### recent_transactions

**Prompt (Shona)**: `Ndinoda kuona zvishandiswa zvichangobva`

**Expected**: Should understand request for recent transactions

**Response (Basic)**:
```
Ndinokutendai! Ndokumbirawo mundipe rumwe ruzivo rwakawanda pamusoro pezvishandiswa zvauri kuda kuona. Uri kuda kuona zvishandiswa zvemhando ipi? Semuenzaniso, zvingave zvehunyanzvi, zvinhu zvemumba, kana kuti zvimwe zvigadzirwa? Ndichakubatsira nemashoko akakodzera.
```

**Response (With System)**:
```
Unogona kutarisa nhoroondo yako ye transactions kuti uone zvishandiswa zvichangobva. Ndokumbira undidze kuti ndeipi transaction yaunoda kuona kana kuti unoda kutarisa nhoroondo yese here?
```

**Language (Basic)**: Unknown

**Language (System)**: Mixed

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

## Complex Requests

### transaction_help

**Prompt (Shona)**: `Ndinoda rubatsiro nezve chishandiso changu`

**Expected**: Should understand request for transaction help

**Response (Basic)**:
```
Zvakajeka! Ndingakubatsira sei nezve chishandiso chako? Unoda rubatsiro pakugadzirisa, kushandisa, kana chimwe chinhu? Ndapota taura zvimwe kuti ndikupe rubatsiro rwakakodzera.
```

**Response (With System)**:
```
Ndinokugamuchirai! Ndikubatsirei nezve chishandiso chenyu? Munoda kuziva nezve wallet balance, kutarisa transaction history, kana pane chimwe chinhu chiri kunetsa?
```

**Language (Basic)**: Unknown

**Language (System)**: English

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

### transaction_issue

**Prompt (Shona)**: `Mari yangu yakabviswa asi mutengesi haana kugamuchira`

**Expected**: Should understand complex issue: money deducted but merchant didn't receive

**Response (Basic)**:
```
Zvinonzwika sekunge uri kusangana nematambudziko akakosha. Kana mari yako yakabviswa asi mutengesi haana kugamuchira, pane zvinhu zvishoma zvaungaita:

1. **Tsvaga Chikonzero**: Edza kubata mutengesi kuti uwane chikonzero nei vasina kugamuchira mari yako. Pamwe pane kukanganisika kwekuverenga kana kuti pane chimwe chinhu chiri kutadza.

2. **Ramba Uchitora Magwaro**: Chengeta zvinyorwa zvose zvine chekuita nekutenga kwako, kusanganisira mainvoice, maemail, uye mamwe magwaro anoratidza kuti wakaita kutenga.

3. **Bata Bhanga**: Kana mari yako yakabviswa kubva kubhanga rako, ungada kubata bhanga rako kuti uwane rubatsiro. Vangakwanisa kukubatsira kuongorora nyaya iyi.

4. **Tarisa Mutemo**: Kana zvinhu zvisina kufamba zvakanaka, unogona kufunga kutora matanho epamutemo. Zvinogona kutora nguva, asi kune dzimwe nguva zvichidikanwa.

5. **Tsvaga Rubatsiro**: Kana uchinzwa sokuti hazvina kumira zvakanaka, ungada kutsvaga rubatsiro kubva kune vamwe vanokwanisa, sekutengesa kana masangano anobatsira vatengi.

Nekudaro, zvakakosha kubata nyaya iyi nekukurumidza uye nemazvo. Good luck!
```

**Response (With System)**:
```
Ndinonzwisisa kuti uri kutambura nematambudziko aya. Zvakakosha kuti udzore nyaya iyi nekukurumidza. Ndokumbira undipe ruzivo rwakawanda nezvemutengesi, saizvozvo nemari yakabviswa uye zuva rawakatenga. Ndichakubatsira kubuditsa tiket yekutsigira kuti nyaya iyi igadziriswe.
```

**Language (Basic)**: Shona

**Language (System)**: Unknown

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

### transaction_with_merchant

**Prompt (Shona)**: `Ndinoda rubatsiro nezve chishandiso changu kuna Coffee Shop`

**Expected**: Should understand request for help with specific merchant transaction

**Response (Basic)**:
```
Zvakadini! Ndakagadzirira kukubatsira nezve chishandiso chako cheCoffee Shop. Unoda rubatsiro papi? Kuti ndiwane zano rakanaka, ndapota ndiudze kuti chishandiso chako chiri kutarisirwa kuita chii, uye chii chaunoda kubatsira nacho?
```

**Response (With System)**:
```
Ndingakubatsirei nezvipi chaizvo pamusoro pechishandiso chako? Unoda kutarisa wallet balance yako, kana kuti pane imwe nyaya yaunoda kugadzirisa? Ndiri pano kuti ndibatsire!
```

**Language (Basic)**: Unknown

**Language (System)**: Shona

**Understanding Score**: 3/5

**Quality Score**: 3/5

---

## Mixed Language

### mixed_language

**Prompt (Shona)**: `Mhoro, I need help with my balance`

**Expected**: Should handle mixed Shona-English input

**Response (Basic)**:
```
Mhoro! I’m here to help. Could you please provide more details about the balance you need assistance with? Are you referring to financial balance, work-life balance, or something else?
```

**Response (With System)**:
```
Mhoro! Ndokumbirawo undipeiwo nguva kuti ndiongorore chiyero chako. Ndokumbirawo undipe nhamba yako yeEcocash wallet kuti ndikubatsire.
```

**Language (Basic)**: English

**Language (System)**: Mixed

**Understanding Score**: 5/5

**Quality Score**: 4/5

---

## Recommendations

⚠️ **GPT-4o-mini shows moderate understanding of Shona prompts**

⚠️ **Model sometimes responds in Shona** - May need prompting to encourage Shona responses

### Implementation Options

1. **If understanding is good (≥4)**: Implement Shona language support with LLM responding in Shona
2. **If understanding is moderate (3-4)**: Use frontend translations + prompt LLM to respond in Shona
3. **If understanding is poor (<3)**: Use frontend-only translations, keep LLM in English

