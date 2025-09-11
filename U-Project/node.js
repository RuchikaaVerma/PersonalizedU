const express = require('express');
const bodyParser = require('body-parser');
const app = express();

app.use(bodyParser.json());

app.post('/webhook', (req, res) => {
  const intent = req.body.queryResult.intent.displayName;
  let responseText = '';
  let customPayload = {};

  if (intent === 'start-assessment') {
    responseText = "Launching the assessment now!";
    customPayload = {
      "action": "openAssessmentModal"
    };
  }

  res.json({
    "fulfillmentText": responseText,
    "fulfillmentMessages": [
      {
        "payload": {
          "richContent": [
            [
              {
                "type": "html",
                "rawHtml": "<div>" + responseText + "</div>"
              },
              {
                "type": "custom",
                "payload": customPayload
              }
            ]
          ]
        }
      }
    ]
  });
});

app.listen(3000, () => console.log('Webhook listening on port 3000!'));