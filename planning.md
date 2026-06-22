# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool will search through the mock dataset using the item description, size, and max price provided by the user as input.  It returns a list of matching items related to the second hand item request made by the user ordered by relevance or shows an error if not matching items are found in the dataset. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): Description of the item the user is looking for
- `size` (str): The user's preferred clothing size based on the clothing type
- `max_price` (float): The user's maximum price range for the item they are looking for

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
The tool returns a list of of matching items ordered by relevance based on the item the user is looking for. Each listing contains information about the item, which includes the id, title, description, category, style_tags, size, condition, price, colors, brand, platform. The planning loop will then look at each item in the list and use the first item in the list as the most relevant item related to what the user is looking for and stores it in a variable for the new item that will be uesed for other tools. 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
The tool will simply return an empty list. It will also let the user know no items match the  item description, size and price range they gave. It will also recommend the user to adjust the description,size, or price range to improve the search criteria and get results they are looking for. The agent will stop and will not call the tools that happen after in the workflow. 
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
It will use the variable storing the new item selected by the planning loop, which is the most relevant item, and the user's current wardrobe as input. Using these arguments, it will suggest complete outfit combinations using the new item selected by the planning loop and items from the user's current wardrobe. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): Contains the new item selected by the planning loop that is the most relevant out of the other items returned by the search_listings tool. Stores the id, title, description, category, style_tags, size, condition, price, colors, brand, platform. 
- `wardrobe` (dict): Contains the name of the wardrobe and a list of the different items in the wardrobe. Each item is stored as a dictionary containing the id, name, category, colors, style tags, and notes of that item. 

**What it returns:**
<!-- Describe the return value -->
Returns a  string containing the description for one or more outfit suggestions of complete outfits using the new item in the new_item argument and items in a user's current wardrobe. The planning loop stores this outfit suggestion in the session as outfit_suggestion, which is later passed to the create_fit_card tool

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the user's wardrobe is empty or no outfit can be suggested, the agent will let the user know the wardrobe sis currently empty or it could not find any outfit pairings between the new item it found and the items in the user's wardrobe. It would them stop the workflow without calling the create_fit_card tool

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
It will take the description of a complete outfit suggestion returned by the suggest_outfit tool and the new item selected by the planning loop that is the most relevant item from the list of items returned by search_listings tool as input. Using these arguments, it geerate a short, shareable description of the complete outfit using similar formatting to how someone would caption an Instagram post with. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): Contains the description of the complete outfit returned by the suggest_outfit tool
- `new_item` (dict): Contains the new item selected  by the planning loop, which is the most relevant item from the list of items returned by the search_listings tool

**What it returns:**
<!-- Describe the return value -->
It returns a string containing the short, shareable description of the complete outfit usiing similar styling to how a user creates a post of the outfit on social media. The planning loop stores this description in the session as a fit_card suggestion. 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If outfit data is complete, the tool should return an error message that mentions about the fit card not being generated due to a problem with the outfit data. The agent informs the user that there was insufficient outfit information available to create a shareable outfit description and stops the workflow without returning the session. 

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->
N/A

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The planning loop first calls the search_listings tool, passing the item description, size, and maximum price provided by the user as arguments. The tool returns a list of matching items ordered by relevance, which is stored in results. After search_listings runs, the planning loop checks whether results is empty. If no matching items are found, it stores an appropriate error message in session["error"], sets selected_item, outfit_suggestion, and fit_card to None, and returns the session. Otherwise, it selects the most relevant item by setting selected_item = results[0] and stores it in the session.

The planning loop then calls suggest_outfit, passing selected_item and wardrobe as arguments. The returned outfit description is stored as outfit_suggestion in the session. After the tool runs, the planning loop checks whether outfit_suggestion is empty. If it is empty, it stores an error message in session["error"], sets fit_card to None, and returns the session. Otherwise, it proceeds to call create_fit_card.

The create_fit_card tool receives outfit_suggestion and selected_item as arguments and returns a short, shareable description of the outfit. The result is stored as fit_card in the session. After the tool runs, the planning loop checks whether fit_card is empty or invalid. If it is, an error message is stored in session["error"] and the session is returned. Otherwise, the workflow is complete and the session containing the selected item, outfit suggestion, fit card, and error status is returned to the user.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The agent maintains a session dictionary that stores information generated throughout the workflow. The session contains the fields selected_item, outfit_suggestion, fit_card, and error. After search_listings runs, the returned list of matching items is stored in a temporary variable named results, and the most relevant item is selected and stored as selected_item in the session. If no matching items are found, selected_item, outfit_suggestion, and fit_card are set to None, and the error field is set to an appropriate error message.

The user's wardrobe is available throughout the workflow and is passed together with selected_item to suggest_outfit. After suggest_outfit generates an outfit description, the result is stored in the session as outfit_suggestion. If an outfit cannot be generated, outfit_suggestion and fit_card are set to None, and the error field is updated with an appropriate error message.

The create_fit_card tool then accesses both selected_item and outfit_suggestion from the session to generate the final fit card, which is stored as fit_card. If fit card generation fails, fit_card is set to None, and the error field is updated accordingly. By storing these values in the session, information produced by one tool can be reused by subsequent tools without requiring the user to provide the same information multiple times.
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | | The agent sets session["error"] to "No listings found matching '{description}', size {size}, under ${max_price}. Try adjusting your description, size, or price range.", sets selected_item, outfit_suggestion, and fit_card to None, and returns the session early without calling suggest_outfit or create_fit_card. 
| suggest_outfit | Wardrobe is empty | | The agent sets session["error"] to "Could not generate an outfit suggestion. This may be because the wardrobe is empty or the item details were insufficient. Try adding items to your wardrobe or searching for a different item.", sets selected_item, outfit_suggestion, and fit_card to None, and returns the session early without calling create_fit_card.
| create_fit_card | Outfit input is missing or incomplete | | The agent sets session["error"] to "Could not generate a fit card. The outfit information may have been incomplete. Try searching for a different item.", sets selected_item, outfit_suggestion, and fit_card to None, and returns the session early. 

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     Use ASCII art or a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html).
     Do NOT embed an image — graders need to read your diagram directly in the file;
     an embedded image or screenshot cannot be evaluated.
     You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
User query
    │
    ▼
Planning Loop
    │
    ├─► search_listings(description, size, max_price)
    │       │
    │       ├──► results=[]
    │       │       │
    │       │       ▼
    │       │   Session: {selected_item=None, outfit_suggestion=None, fit_card = None,  error="No listings found..." } 
    │       │       │
    │       │       └────► return session
    │       │
    │       └──► results=[item, ...]
    │               │
    │               ▼
    │           Session: selected_item=results[0]
    │               │
    ├─► suggest_outfit(selected_item, wardrobe)
    │       │
    │       ├── outfit_suggestion=""
    │       │       │
    │       │       ▼
    │       │   Session: {  selected_item=None, outfit_suggestion=None, fit_card = None, error="Could not generate outfit suggestion..." }
    │       │       │
    │       │       └────► return session
    │       │
    │       └── outfit_suggestion="..."
    │               │
    │           Session: { outfit_suggestion="...", error=None }
    │               │
    └─► create_fit_card(outfit_suggestion, selected_item)
            │
            ├── fit_card=""
            │       │
            │       ▼
            │   Session: { selected_item=None, outfit_suggestion=None, fit_card = None
            │               error="Could not generate fit card..." }
            │       │
            │       └─────► return session
            │
            └── fit_card="..."
                    │
                    ▼
                Session: { selected_item=results[0], outfit_suggestion="...",
                            fit_card="...", error=None }
                    │
                    ▼
                return session
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

     For implementing search_listings, I used Claude and provided it with the Tool 1 spec block from planning.md, which included the input parameters, return value description, and failure mode, along with the function stub from tools.py containing the docstring and TODO steps. I asked Claude to implement the function using load_listings() from the data loader. Before using the output, I verified that it filtered by all three parameters, handled None values for size and max_price, scored listings by keyword overlap across the relevant fields, and returned an empty list rather than raising an exception when nothing matched. I then tested it against three queries: a realistic query to confirm it returned results, an impossible query to confirm it returned an empty list, and a price-filtered query to confirm all results were under the ceiling.

     For implementing suggest_outfit, I provided Claude with the Tool 2 spec block from planning.md, which described the two input parameters, the expected return value, and the empty wardrobe failure mode, along with the function stub from tools.py. I asked Claude to implement the function using the Groq client helper _get_groq_client() and the llama-3.3-70b-versatile model. Before using the output, I verified that it handled the empty wardrobe case by switching to a general styling prompt rather than crashing or returning an empty string, that it referenced wardrobe items by name in the populated wardrobe path, and that the LLM call was wrapped in a try/except block that returned an empty string on failure.

     For implementing create_fit_card, I provided Claude with the Tool 3 spec block from planning.md, which described the outfit and new_item parameters, the Instagram-style caption requirements, and the failure mode for empty outfit input, along with the function stub from tools.py. I asked Claude to implement the function using _get_groq_client() with a higher temperature than the other tools to ensure caption variety. Before using the output, I verified that the guard clause caught both empty and whitespace-only outfit strings and returned a descriptive error message rather than raising an exception, that the prompt instructed the LLM to write only the caption with no preamble, and that running it twice on the same input produced different results.
     
     For implementing run_agent, I provided Claude with the Planning Loop and State Management sections from planning.md, the agent architecture diagram, and the function stub from agent.py containing the TODO steps. I asked Claude to implement the planning loop following the conditional branching described in the diagram. Before using the output, I verified that it parsed the user query using the LLM at temperature 0.0 with a fallback for failed parsing, that it branched correctly on empty results from search_listings without calling subsequent tools, that session state flowed correctly between all three tool calls, and that each error branch set the appropriate session fields to None and returned early.

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

Fitfindr helps users find their desired secondhand clothing items by using a item description, size, and price range provided by the user to search through the mock listings dataset. It finds item listings closely related to the user's item request and uses the top result to compare it to the user's current wardrobe to find fits between the new item and items in the wardobe. Finally, it will create shareable descriptions of the complete outfit, and through this entire process, it handles cases where there are no matching results returned and empty wardrobes. 
**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent will analyze the item description size, and price range and searches through the mock dataset and finds matching items. The search_listings tool is called with the item description, size, and max price as input to it. If there are not matching listings returned by the search_listings tool, Findfitr tells user what to try differently and stops. 

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
The tool called in step 1 returns a list of matching items ordered by relevance based on the user's new secondhand item request. It takes the top result from that as the new item and compares it to the items in the user's current wardrobe to generate outfit suggestion using the new item and wardrobe items. The suggest_outfit tool is called with the new_item, the top result from the 3 most relevant matching listings, and wardrobe as input to it. 


**Step 3:**
<!-- Continue until the full interaction is complete -->
It will call the tool create_fit_card with the outfit returned as output from the suggest_outfit tool and the new_item, the top outfit from the most relevant matching listings returned by the search_listings tool as input. It returns aa shareable description of a complete outfit. 

**Final output to user:**
<!-- What does the user actually see at the end? -->
The user sees the selected new secondhand item, which is the most relevant item from the list of matching items ordered by relevance returned by search_listings tool, oufit suggestion generated using the new item suggestion and items from the user's wardrobe returned by new_item tool, and a shareable description describing the complete outfit returned by the create_fit_card tool. 

