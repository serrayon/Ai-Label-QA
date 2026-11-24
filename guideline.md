# Spanish Tweet Sentiment Labeling Guideline (v1)

Label each tweet with exactly one label: **positive**, **negative**, or **neutral**.
Judge the sentiment the author expresses, not the topic.

## Labels

**positive**: the author expresses approval, happiness, gratitude, excitement, love, or praise.
- "¡Qué buen partido! Orgulloso de mi equipo": positive

**negative**: the author expresses anger, sadness, frustration, disgust, fear, criticism, or complaint.
- "Otra vez sin luz en el barrio, qué desastre": negative

**neutral**: no clear sentiment, or the tweet only shares facts, news, questions, or announcements.
- "Mañana a las 10 empieza la conferencia en Madrid": neutral

## Edge cases

1. **Sarcasm and irony**: label the real meaning, not the literal words.
   "Genial, otra vez el metro tarde. Me encanta": negative
2. **Mixed sentiment**: choose the sentiment that dominates the tweet. If both are equally strong, choose neutral.
3. **Questions**: neutral, unless the question clearly carries emotion ("¿En serio nadie va a hacer nada?": negative).
4. **News and headlines**: neutral, unless the author adds their own opinion.
5. **Emojis and slang**: count them. A crying-laughing emoji after a joke is positive; "qué mala onda" is negative.
6. **Regional Spanish**: treat regional expressions by their local meaning (for example, "chido" and "chévere" are positive).
7. **Insults aimed at someone**: negative, even if the author seems to be joking, unless it is clearly friendly teasing.
8. **Unclear or too short to judge**: neutral.
