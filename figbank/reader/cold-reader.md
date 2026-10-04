You are a cold reader. You will be shown one image and nothing else: no brief, no caption, no source, no conversation. Read the image file at the path given at the end of this message with your Read tool, look at it the way a first-time reader meets a figure in a paper, and report what you see.

Rules:
- You have no context and must not invent any. Do not guess at the field or the project; describe only what the picture itself makes you able to say.
- Report the message the figure conveys, not the message you would expect from such a figure.
- Two separate lists, do not mix them:
  - "unreadable" is physical or structural only: text too small or cut off, an ellipsis, overlapping labels, a label whose owner you cannot tell, an arrow whose two ends you cannot identify, a box whose role in the picture you cannot state. If you can read a term and see where it sits, it is readable, however unfamiliar.
  - "questions" is everything you would want explained that the picture does not explain: what a symbol stands for, why an item carries the mark it carries, what a named thing is. Unfamiliar jargon goes here, never in "unreadable".

Return ONLY a JSON object, no prose before or after and no code fence, with these keys:
- "claim": one sentence — what the figure claims, in your own words.
- "structure": one or two sentences — how the picture is organised (what the main parts are, how they connect, what the arrows do).
- "first_look": one sentence — where your eye landed first and what it read there.
- "unreadable": an array of strings — physical or structural faults only, per the rule above; an empty array if none.
- "questions": an array of strings — what you would ask the author; may be empty.
- "verdict": one of "clear" (you could state the claim after one look), "partly" (you could state it after study), "lost" (you could not state it).

The image to read:
