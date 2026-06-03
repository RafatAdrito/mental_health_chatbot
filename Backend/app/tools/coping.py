from langchain_core.tools import tool

_COPING_STRATEGIES: dict[str, dict[str, list[dict[str, str]]]] = {
    "anxiety": {
        "mild": [
            {
                "name": "Box Breathing",
                "steps": "1. Breathe in slowly for 4 seconds\n2. Hold your breath for 4 seconds\n3. Breathe out slowly for 4 seconds\n4. Hold for 4 seconds\n5. Repeat 4-6 times",
            },
            {
                "name": "Progressive Muscle Relaxation",
                "steps": "1. Start with your toes — tense them for 5 seconds, then release\n2. Move to your calves, thighs, stomach, chest, hands, arms, shoulders, and face\n3. Notice the difference between tension and relaxation\n4. Take slow, deep breaths throughout",
            },
        ],
        "moderate": [
            {
                "name": "5-4-3-2-1 Grounding",
                "steps": "Notice and name:\n- 5 things you can SEE\n- 4 things you can TOUCH\n- 3 things you can HEAR\n- 2 things you can SMELL\n- 1 thing you can TASTE\nThis brings your focus to the present moment.",
            },
            {
                "name": "Thought Challenging",
                "steps": "1. Write down the anxious thought\n2. Ask: What evidence supports this thought?\n3. Ask: What evidence contradicts it?\n4. Ask: What would I tell a friend in this situation?\n5. Write a more balanced thought",
            },
        ],
        "severe": [
            {
                "name": "Cold Water Reset",
                "steps": "1. Hold ice cubes in your hands or splash cold water on your face\n2. Focus entirely on the physical sensation\n3. This activates the dive reflex, which can help calm your nervous system\n4. Follow with slow, deep breathing",
            },
        ],
    },
    "depression": {
        "mild": [
            {
                "name": "Gratitude Journaling",
                "steps": "1. Write down 3 things you're grateful for today (they can be small)\n2. For each one, describe why it matters to you\n3. Try to do this daily, ideally at the same time\n4. Review past entries when you need a boost",
            },
            {
                "name": "Behavioral Activation",
                "steps": "1. Choose ONE small activity you used to enjoy (a short walk, listening to music, etc.)\n2. Set a specific time to do it today\n3. Do it for just 5-10 minutes — no pressure to enjoy it\n4. Notice how you feel before and after\n5. Gradually increase activities over time",
            },
        ],
        "moderate": [
            {
                "name": "Social Connection",
                "steps": "1. Think of one person you trust\n2. Send them a simple message — even 'Hi, thinking of you'\n3. If possible, schedule a brief call or meetup\n4. You don't have to talk about how you're feeling — just connecting helps",
            },
            {
                "name": "Physical Movement",
                "steps": "1. Start with just standing up and stretching\n2. Take a 10-minute walk outside if possible\n3. Even gentle movement releases endorphins\n4. No need for intense exercise — consistency matters more than intensity",
            },
        ],
        "severe": [
            {
                "name": "Self-Compassion Break",
                "steps": "1. Place your hand on your heart\n2. Say to yourself: 'This is a moment of suffering'\n3. Say: 'Suffering is a part of being human'\n4. Say: 'May I give myself the compassion I need'\n5. Breathe gently and let yourself feel whatever comes up",
            },
        ],
    },
    "stress": {
        "mild": [
            {
                "name": "Mindful Breathing",
                "steps": "1. Sit comfortably and close your eyes\n2. Breathe naturally — don't try to control it\n3. Focus your attention on each breath in and out\n4. When your mind wanders, gently return focus to breathing\n5. Continue for 3-5 minutes",
            },
            {
                "name": "Brain Dump",
                "steps": "1. Get a piece of paper or open a notes app\n2. Write down EVERYTHING on your mind — no filtering\n3. Don't organize or judge — just dump it all out\n4. Once done, circle the 1-2 things you can address today\n5. Let the rest wait",
            },
        ],
        "moderate": [
            {
                "name": "Time Blocking",
                "steps": "1. List your top 3 priorities for today\n2. Assign a specific time block for each (e.g., 9-10am)\n3. Include short breaks between blocks\n4. Focus on one thing per block — no multitasking\n5. If something isn't done, reschedule it — don't stress",
            },
        ],
        "severe": [
            {
                "name": "Body Scan Meditation",
                "steps": "1. Lie down or sit comfortably\n2. Close your eyes and take 3 deep breaths\n3. Slowly bring attention to each body part, starting from your toes\n4. Notice any tension, pain, or sensation without judgment\n5. Spend 10-15 minutes moving attention up through your whole body",
            },
        ],
    },
    "anger": {
        "mild": [
            {
                "name": "Cool-Down Timer",
                "steps": "1. Step away from the situation if possible\n2. Count slowly to 10 (or 20 if needed)\n3. Take deep breaths with each count\n4. Ask yourself: Will this matter in a week? A month?\n5. Return to the situation when you feel calmer",
            },
        ],
        "moderate": [
            {
                "name": "Cognitive Reframing",
                "steps": "1. Identify the thought driving your anger (e.g., 'They did that on purpose')\n2. Consider alternative explanations\n3. Ask: 'What if they didn't mean it that way?'\n4. Choose a response based on the most likely explanation\n5. This doesn't excuse bad behavior — it helps you respond wisely",
            },
        ],
        "severe": [
            {
                "name": "Physical Release",
                "steps": "1. Go for a brisk walk or jog\n2. Do jumping jacks, push-ups, or squeeze a stress ball\n3. Let the physical intensity match your emotional intensity\n4. Follow with slow breathing to cool down\n5. Then revisit the situation with a clearer mind",
            },
        ],
    },
    "general": {
        "mild": [
            {
                "name": "Sleep Hygiene",
                "steps": "1. Set a consistent bedtime and wake time\n2. Avoid screens 30 minutes before bed\n3. Keep your room cool, dark, and quiet\n4. Avoid caffeine after 2 PM\n5. Try a relaxing pre-sleep routine (reading, gentle stretching)",
            },
        ],
        "moderate": [
            {
                "name": "Journaling",
                "steps": "1. Set a timer for 10 minutes\n2. Write freely about what's on your mind\n3. Don't worry about grammar or structure\n4. Let thoughts flow without censoring\n5. Read back and notice patterns or insights",
            },
        ],
        "severe": [
            {
                "name": "Reach Out",
                "steps": "1. You don't have to go through this alone\n2. Consider calling a trusted friend, family member, or counselor\n3. If you're in crisis, contact 988 Suicide & Crisis Lifeline\n4. Asking for help is a sign of strength, not weakness",
            },
        ],
    },
}


@tool
def get_coping_strategies(mood: str, intensity: str = "moderate") -> str:
    """Get evidence-based coping strategies based on mood and intensity level.

    Args:
        mood: The mood to get strategies for — "anxiety", "depression", "stress", "anger", or "general".
        intensity: The intensity level — "mild", "moderate", or "severe".
    """
    mood_key = mood.lower() if mood.lower() in _COPING_STRATEGIES else "general"
    intensity_key = intensity.lower() if intensity.lower() in ("mild", "moderate", "severe") else "moderate"

    strategies = _COPING_STRATEGIES[mood_key].get(intensity_key, [])
    if not strategies:
        strategies = _COPING_STRATEGIES["general"].get(intensity_key, [])

    lines = [f"Here are some coping strategies for {mood_key} ({intensity_key} level):\n"]
    for i, s in enumerate(strategies, 1):
        lines.append(f"**{i}. {s['name']}**")
        lines.append(s["steps"])
        lines.append("")

    lines.append("Remember: these techniques work best with practice. Be patient with yourself.")
    return "\n".join(lines)
