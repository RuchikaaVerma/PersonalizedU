// index.js
const express = require('express');
const app = express();
app.use(express.json());

// The function that handles requests from Dialogflow
app.post('/', (request, response) => {
    const intentName = request.body.queryResult.intent.displayName;
    let responseText = '';
    let customPayload = {};

    // Use a switch statement or if/else to handle different intents
    switch (intentName) {
        case 'start-assessment':
            responseText = "Launching the assessment now!";
            customPayload = { "action": "openAssessmentModal" };
            break;
        case 'show-features':
            responseText = "Our key features are personalized profiles, skill assessments, and AI recommendations.";
            break;
        // Add more cases for other intents
        default:
            responseText = "I'm sorry, I can't do that right now.";
    }

    // Respond to Dialogflow with a JSON object
    response.json({
        "fulfillmentText": responseText,
        "payload": {
            "richContent": [[
                {
                    "type": "info",
                    "title": responseText
                },
                {
                    "type": "custom",
                    "payload": customPayload
                }
            ]]
        }
    });
});

// Listen on the port provided by Google Cloud Functions
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});