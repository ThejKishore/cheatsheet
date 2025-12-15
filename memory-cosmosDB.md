Traditional RAG vs. Agentic Memory
Traditional RAG (Retrieval-Augmented Generation):

Retrieves documents or chunks based on semantic similarity
Static knowledge base that doesn't learn from interactions
Same results for all users querying similar topics
No concept of "importance" or "recency" - just similarity scores
Agentic Memory:

Stores personalized facts learned from conversations
Dynamic knowledge that grows with each interaction
User-specific preferences and history
Salience scoring based on importance, confidence, and recency
Cross-session persistence that creates continuity
Three Types of Memory
Our memory system implements three distinct types inspired by cognitive psychology:

1. Declarative Memory (Semantic Facts)
Long-term, stable facts about the user that rarely change.

Examples:

Dietary restrictions: "User is vegetarian"
Accessibility needs: "User requires wheelchair access"
Language preferences: "User speaks Spanish"
Travel companions: "User travels with two children"
Characteristics:

High confidence scores (0.9-1.0)
Long TTL (never expire)
Rarely updated once established
Critical for filtering search results
2. Procedural Memory (Behavioral Patterns)
Patterns in user behavior and preferences learned over time.

Examples:

Budget preferences: "User typically books moderate-tier hotels"
Style preferences: "User prefers boutique hotels over chains"
Activity patterns: "User enjoys museums and cultural sites"
Timing preferences: "User prefers morning activities"
Characteristics:

Confidence scores that increase with repeated observations
Medium TTL (90-180 days)
Updated with each confirming interaction
Used to personalize recommendations
3. Episodic Memory (Trip-Specific Context)
Specific events and experiences from past trips.

Examples:

Places visited: "User visited Sagrada Familia in Barcelona 2024"
Hotels stayed: "User stayed at Hotel Arts Barcelona"
Restaurants tried: "User loved Cal Pep for seafood"
Trip feedback: "User found Barcelona too crowded in August"
Characteristics:

Tied to specific trips and dates
Short to medium TTL (30-90 days)
Prevents duplicate recommendations
Provides context for follow-up trips
When to Store vs. When to Recall
Store Memories When:

✅ User explicitly states a preference or restriction
✅ User makes a choice (selects a hotel, books a restaurant)
✅ User provides feedback (positive or negative)
✅ Clear behavioral pattern emerges (3+ similar choices)
✅ User shares context about travel companions or needs
Recall Memories When:

✅ Starting a search operation (filter by restrictions)
✅ Making recommendations (boost matching preferences)
✅ User returns after time gap (restore context)
✅ Generating itineraries (incorporate past learnings)
✅ User asks "what did I..." questions
Don't Store:

❌ Ambiguous statements without clear intent
❌ Contradictory information (resolve conflict first)
❌ Sensitive personal information beyond travel preferences
❌ Transient conversation context (use state instead)
Cross-Session Persistence
Memory enables continuity across sessions:

Session 1 (January):
User: "I'm vegetarian and love art museums"
Agent: [Stores declarative + procedural memories]

Session 2 (March):
User: "Plan a trip to Rome"
Agent: [Recalls memories, filters for vegetarian restaurants, prioritizes art museums]
"Based on your preferences, I'll focus on vegetarian dining and Rome's incredible art scene..."
