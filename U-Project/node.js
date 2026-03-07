const express    = require('express');
const bodyParser = require('body-parser');
const axios      = require('axios');

const app = express();
app.use(bodyParser.json());

// ── Ollama Config ─────────────────────────────────────
const OLLAMA_URL   = 'http://localhost:11434/v1/chat/completions';
const OLLAMA_MODEL = 'tinyllama';  // match whatever you pulled

const SYSTEM_PROMPT = `You are a cheerful, encouraging AI learning assistant 
for an e-learning platform called PersonalizedU. 
Help users with course questions, study tips, and learning guidance. 
Keep answers concise (2-3 sentences max). Always be friendly and motivating.`;

// ── Ollama Helper ─────────────────────────────────────
async function askOllama(userMessage) {
    const response = await axios.post(OLLAMA_URL, {
        model:       OLLAMA_MODEL,
        messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user',   content: userMessage   }
        ],
        max_tokens:  300,
        temperature: 0.7,
        stream:      false,
    }, { timeout: 60000 });

    return response.data.choices[0].message.content;
}

// ── Build Dialogflow Response ─────────────────────────
function buildResponse(text, customPayload = null) {
    const richContent = [
        {
            type:    'html',
            rawHtml: `<div>${text}</div>`
        }
    ];

    if (customPayload) {
        richContent.push({
            type:    'custom',
            payload: customPayload
        });
    }

    return {
        fulfillmentText: text,
        fulfillmentMessages: [
            {
                payload: {
                    richContent: [richContent]
                }
            }
        ]
    };
}

// ── Webhook ───────────────────────────────────────────
app.post('/webhook', async (req, res) => {
    const intent    = req.body.queryResult.intent.displayName;
    const queryText = req.body.queryResult.queryText || '';

    // ── Intent: Start Assessment ──
    if (intent === 'start-assessment') {
        return res.json(buildResponse(
            'Launching your assessment now! Good luck! 🚀',
            { action: 'openAssessmentModal' }
        ));
    }

    // ── Intent: Open AI Chat ──
    if (intent === 'open-chat') {
        return res.json(buildResponse(
            'Opening the AI chat for you!',
            { action: 'openAiModal' }
        ));
    }

    // ── Intent: Show Recommendations ──
    if (intent === 'show-recommendations') {
        return res.json(buildResponse(
            'Here are your personalised course recommendations!',
            { action: 'scrollToRecommendations' }
        ));
    }

    // ── All other intents — ask Ollama ────────────────
    try {
        const reply = await askOllama(queryText);
        return res.json(buildResponse(reply));

    } catch (err) {

        // Ollama not running
        if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET') {
            console.error('Ollama is not running:', err.message);
            return res.json(buildResponse(
                "I'm having trouble thinking right now. Please make sure Ollama is running and try again! 🔧"
            ));
        }

        // Timeout
        if (err.code === 'ECONNABORTED') {
            console.error('Ollama timed out:', err.message);
            return res.json(buildResponse(
                "That took too long — please try a simpler question! ⏳"
            ));
        }

        // Anything else
        console.error('Webhook error:', err.message);
        return res.json(buildResponse(
            "Something went wrong on my end. Please try again! 😅"
        ));
    }
});

// ── Health Check ──────────────────────────────────────
app.get('/health', (req, res) => {
    res.json({ status: 'ok', model: OLLAMA_MODEL });
});

// ── Start ─────────────────────────────────────────────
app.listen(3000, () => {
    console.log('✦ Webhook listening on port 3000');
    console.log(`✦ Using Ollama model: ${OLLAMA_MODEL}`);
    console.log('✦ Health check: http://localhost:3000/health');
});