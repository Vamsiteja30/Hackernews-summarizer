# HackerNews Summarizer

This project fetches top stories from HackerNews and automatically generates AI-powered summaries of the most important posts. Instead of reading through long discussion threads, users get concise 2-sentence summaries that capture the essence of each story.

The system intelligently identifies which posts matter (high scores, lots of comments, or trending topics) and uses AI to create quick summaries. It's built with Praval agents and supports both OpenAI and Gemini for reliable summarization.

## Day 1 – HackerNews API Integration 

The project started by connecting to the official HackerNews API. The script fetches the top stories and displays basic post details:
- Title of the post
- Author (who posted it)
- Score (how many upvotes)
- Comments (how many people discussed it)
- URL (link to read the full story)

### How to Run

1. **Create a Python virtual environment**
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment**
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On Mac/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the script**
   ```bash
   python main.py
   ```

   Output:

   Running the script displays a list of top HackerNews stories with all their details.
   
<img width="605" height="695" alt="image" src="https://github.com/user-attachments/assets/e882e290-79f3-48d3-931a-55c781464e87" />


## Day 2 – Making It Smart

After Day 1, the project was showing every single story, even ones that weren't particularly interesting. Logic was added to identify which posts actually matter.

### What Was Planned
- Reviewed how data is fetched from HackerNews
- Planned logic for identifying important and trending posts
- Designed structure for preparing input for AI summarization

### What Was Built
Instead of showing all stories equally, the system now automatically labels each story:
- **NORMAL** – Regular posts that don't meet importance criteria (low scores, few comments)
- **IMPORTANT** – Posts with high scores (150+ upvotes) or lots of comments (50+ discussions)
- **TRENDING** – Important posts that were created within the last 12 hours (fresh and popular)

When running the script, clear labels show which posts are worth attention. This ensures the system only focuses on summarizing stories that actually matter.

<img width="730" height="685" alt="image" src="https://github.com/user-attachments/assets/fcd348e0-59ec-48c8-bfd6-1156080be84e" />

## Day 3,4 – Building the Agent System

This phase moved from a simple script to an agent-based system. An agent takes information, processes it, and returns a result.

### The Learning Step (agent.py)

Before integrating Praval, a simple agent was built using plain Python. This helped understand the basics:
- How data flows into an agent
- How the agent processes that data  
- How it returns results

This file remains as a reference - like training wheels. It's kept to remember how the fundamentals were learned.

### The Real Deal (praval_agent.py)

Once the basic agent concept was understood, the project moved to Praval. Praval is a framework specifically built for creating agent-based AI systems. It's like upgrading from a bicycle to a motorcycle - same basic idea, but more powerful.

What was implemented:
- Created a Praval agent using the `@agent` decorator
- Set it up to receive data through a "spore" (Praval's way of passing structured information between agents)
- Defined which type of requests the agent should respond to (in this case, "summary_request")
- Made it return structured results

The Praval agent was connected to the HackerNews pipeline. Now, whenever IMPORTANT or TRENDING posts are identified, they automatically get sent to the Praval agent for processing.

## Day 5,6 – AI Summarization Integration

The agent system was ready, but it needed real intelligence to generate summaries. This phase integrated AI models to produce actual 2-sentence summaries.

### AI Provider Setup

The system uses a dual-provider approach for reliability:
- **OpenAI (Primary)** – Uses `gpt-4o-mini` model for fast, high-quality summaries
- **Gemini (Fallback)** – Automatically switches to Google's Gemini API if OpenAI fails

This fallback mechanism ensures the system keeps working even if one AI service has issues, quota limits, or downtime.

### How It Works

When an IMPORTANT or TRENDING post is identified:
1. The post data is prepared as clean text (title, author, score, comments, URL)
2. The text is sent to the Praval agent
3. The agent tries OpenAI first
4. If OpenAI fails, it automatically tries Gemini
5. A 2-sentence summary is generated and displayed

The system handles errors gracefully. If both AI providers fail, it displays a clear error message and continues processing other posts.

### Environment Setup

To use AI summarization, you need API keys:

1. **Create a `.env` file** in the project root:
   ```
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ```

2. **Get API Keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - Gemini: https://makersuite.google.com/app/apikey

3. **Run the script:**
   ```bash
   python main.py
   ```

The script will automatically use OpenAI for summaries. If OpenAI is unavailable, it switches to Gemini seamlessly.

Output:-

<img width="1207" height="864" alt="image" src="https://github.com/user-attachments/assets/d7690dcd-4eda-401e-b426-bdec81064ef9" />
<img width="1204" height="542" alt="image" src="https://github.com/user-attachments/assets/939d12f7-0af2-461b-870b-6ec10b73e53f" />


## Todays update  – FastAPI Backend Setup

This phase adds a FastAPI backend to expose the summarization functionality via REST API endpoints.

### What Was Built

A basic FastAPI application with:
- **Health check endpoint** (`GET /`) – Returns server status
- **Stories endpoint** (`GET /stories`) – Placeholder for fetching top stories

### Installation

1. **Install FastAPI and Uvicorn:**
   ```bash
   pip install fastapi uvicorn
   ```
   
   Or install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

1. **Start the FastAPI server:**
   ```bash
   uvicorn api:app --reload
   ```

2. **Access the API:**
   - **Health Check:** http://localhost:8000
   - **Stories Endpoint:** http://localhost:8000/stories
   - **Interactive Docs (Swagger UI):** http://localhost:8000/docs
   - **Alternative Docs (ReDoc):** http://localhost:8000/redoc

### Expected Output

When you visit http://localhost:8000, you should see:
```json
{"status": "ok"}
```

When you visit http://localhost:8000/stories, you should see:
```json
{"stories": []}
```

### File Structure

- `api.py` – FastAPI application with basic endpoints

### Common Mistakes to Avoid

- **Wrong import:** Make sure to use `from fastapi import FastAPI`
- **Not running server:** Remember to run `uvicorn api:app --reload`
- **Wrong port:** Default port is 8000, use `http://localhost:8000` (not `0.0.0.0:8000`)

Output :-
<img width="1017" height="272" alt="image" src="https://github.com/user-attachments/assets/0095b980-3641-4fae-b3e8-560cf3b03ca2" />
<img width="1919" height="346" alt="image" src="https://github.com/user-attachments/assets/7a2bbaa0-a94e-4a67-8774-886f1aedba5b" />
<img width="1913" height="208" alt="image" src="https://github.com/user-attachments/assets/ef426aab-1387-4ccd-b12f-2bffd030f9c3" />



