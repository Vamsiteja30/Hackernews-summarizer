# HackerNews Summarizer

This project fetches top stories from HackerNews and prepares them for summarization. Instead of reading through long discussion threads, users get quick summaries of the most important posts.

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

## Day 3 – Building the Agent System

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

Output:

<img width="730" height="784" alt="image" src="https://github.com/user-attachments/assets/519a215b-a39d-4258-8821-7f4696257bb1" />

Currently, the agent returns a placeholder message like "Processing completed by Praval agent." .
