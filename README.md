# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├──  tests/
     └── confitest.py         # Configuration test file that adds the root directory to the search path, which is needd to access the tools
                                since the test fiels are in a inner directory of the project directory. 
     └── test_tools.py         # pyTest function testing each failure mode case for each tool
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here  #NOTE: This is included in my env file instead. 
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Your README submission must document each tool's name, inputs, and return value. **These must exactly match your actual function signatures in `tools.py`.** Your documented interfaces will be checked against your actual function signatures in `tools.py` — if the parameter count or types contradict what's in the code, you may not receive full credit for that tool.

---

## Interaction Walkthrough

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**User query:**

**Step 1 — Tool called:**
- Tool: search_listings
- Input:
     - `description` (str): Description of the item the user is looking for
     - `size` (str): The user's preferred clothing size based on the clothing type
     - `max_price` (float): The user's maximum price range for the item they are looking for
- Why this tool: Searches the mock listings dataset and returns the most relevant secondhand items matching the user's request.
- Output: The tool returns a list of of matching items ordered by relevance based on the item the user is looking for. Each listing contains information about the item, which includes the id, title, description, category, style_tags, size, condition, price, colors, brand, platform. The planning loop will then look at each item in the list and use the first item in the list as the most relevant item related to what the user is looking for and stores it in a variable for the new item that will be uesed for other tools. 

If there are no listings, The tool will simply return an empty list. It will also let the user know no items match the  item description, size and price range they gave. It will also recommend the user to adjust the description,size, or price range to improve the search criteria and get results they are looking for. The agent will stop and will not call the tools that happen after in the workflow. 

**Step 2 — Tool called:**
- Tool: suggest_outfit
- Input:
     - `new_item` (dict): Contains the new item selected by the planning loop that is the most relevant out of the other items returned by the search_listings tool. Stores the id, title, description, category, style_tags, size, condition, price, colors, brand, platform. 
     - `wardrobe` (dict): Contains the name of the wardrobe and a list of the different items in the wardrobe. Each item is stored as a dictionary containing the id, name, category, colors, style tags, and notes of that item. 
- Why this tool: Uses the LLM to suggest complete outfit combinations pairing the new item with pieces from the user's existing wardrobe.
- Output: Returns a  string containing the description for one or more outfit suggestions of complete outfits using the new item in the new_item argument and items in a user's current wardrobe. The planning loop stores this outfit suggestion in the session as outfit_suggestion, which is later passed to the create_fit_card tool. 

If the user's wardrobe is empty or no outfit can be suggested, the agent will let the user know the wardrobe sis currently empty or it could not find any outfit pairings between the new item it found and the items in the user's wardrobe. It would them stop the workflow without calling the create_fit_card tool

**Step 3 — Tool called:**
- Tool: create_fit_card
- Input:
     - `outfit` (str): Contains the description of the complete outfit returned by the suggest_outfit tool
     - `new_item` (dict): Contains the new item selected  by the planning loop, which is the most relevant item from the list of items returned by the search_listings tool
- Why this tool: Uses the LLM to generate a short, shareable social media caption describing the complete outfit.
- Output: It returns a string containing the short, shareable description of the complete outfit usiing similar styling to how a user creates a post of the outfit on social media. The planning loop stores this description in the session as a fit_card suggestion. 

If outfit data is complete, the tool should return an error message that mentions about the fit card not being generated due to a problem with the outfit data. The agent informs the user that there was insufficient outfit information available to create a shareable outfit description and stops the workflow without returning the session. 

**Final output to user:**
The user sees the selected new secondhand item, which is the most relevant item from the list of matching items ordered by relevance returned by search_listings tool, oufit suggestion generated using the new item suggestion and items from the user's wardrobe returned by new_item tool, and a shareable description describing the complete outfit returned by the create_fit_card tool. 
---
## Planning Loop
The planning loop first calls the search_listings tool, passing the item description, size, and maximum price provided by the user as arguments. The tool returns a list of matching items ordered by relevance, which is stored in results. After search_listings runs, the planning loop checks whether results is empty. If no matching items are found, it stores an appropriate error message in session["error"], sets selected_item, outfit_suggestion, and fit_card to None, and returns the session. Otherwise, it selects the most relevant item by setting selected_item = results[0] and stores it in the session.

The planning loop then calls suggest_outfit, passing selected_item and wardrobe as arguments. The returned outfit description is stored as outfit_suggestion in the session. After the tool runs, the planning loop checks whether outfit_suggestion is empty. If it is empty, it stores an error message in session["error"], sets fit_card to None, and returns the session. Otherwise, it proceeds to call create_fit_card.

The create_fit_card tool receives outfit_suggestion and selected_item as arguments and returns a short, shareable description of the outfit. The result is stored as fit_card in the session. After the tool runs, the planning loop checks whether fit_card is empty or invalid. If it is, an error message is stored in session["error"] and the session is returned. Otherwise, the workflow is complete and the session containing the selected item, outfit suggestion, fit card, and error status is returned to the user.

## State Management
The agent maintains a session dictionary that stores information generated throughout the workflow. The session contains the fields selected_item, outfit_suggestion, fit_card, and error. After search_listings runs, the returned list of matching items is stored in a temporary variable named results, and the most relevant item is selected and stored as selected_item in the session. If no matching items are found, selected_item, outfit_suggestion, and fit_card are set to None, and the error field is set to an appropriate error message.

The user's wardrobe is available throughout the workflow and is passed together with selected_item to suggest_outfit. After suggest_outfit generates an outfit description, the result is stored in the session as outfit_suggestion. If an outfit cannot be generated, outfit_suggestion and fit_card are set to None, and the error field is updated with an appropriate error message.

The create_fit_card tool then accesses both selected_item and outfit_suggestion from the session to generate the final fit card, which is stored as fit_card. If fit card generation fails, fit_card is set to None, and the error field is updated accordingly. By storing these values in the session, information produced by one tool can be reused by subsequent tools without requiring the user to provide the same information multiple times.



## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` |No results match the query|The agent sets session["error"] to "No listings found matching '{description}', size {size}, under ${max_price}. Try adjusting your description, size, or price range.", sets selected_item, outfit_suggestion, and fit_card to None, and returns the session early without calling suggest_outfit or create_fit_card. |
| `suggest_outfit` |Wardrobe is empty|The agent sets session["error"] to "Could not generate an outfit suggestion. This may be because the wardrobe is empty or the item details were insufficient. Try adding items to your wardrobe or searching for a different item.", sets selected_item, outfit_suggestion, and fit_card to None, and returns the session early without calling create_fit_card.|
| `create_fit_card` |Outfit input is missing or incomplete |The agent sets session["error"] to "Could not generate a fit card. The outfit information may have been incomplete. Try searching for a different item.", sets selected_item, outfit_suggestion, and fit_card to None, and returns the session early.|

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**
Having the agent diagram committed in planning.md before writing any code made implementing run_agent significantly easier. The diagram spelled out the exact conditional branches — what to check after each tool call, which session fields to set on each error path, and where to return early — so the planning loop implementation was essentially a direct translation of the diagram into code. Without it, the branching logic and session field management across three tools would have been easy to get wrong or inconsistent.

**One divergence from your spec, and why:**
The original spec described the suggest_outfit failure mode as handling an empty wardrobe by stopping the workflow, but the implementation diverged from this by treating an empty wardrobe as a valid input that triggers a different prompt path rather than an error. This change was made because stopping the workflow entirely when a new user has no wardrobe would make the agent unusable for the exact group of people most likely to need it — someone just getting started with thrifting. Returning general styling advice instead keeps the workflow complete and still gives the user something useful, while the true failure mode for suggest_outfit remains an empty string returned by the LLM call itself.

---
**AI Usage**
For `search_listings`, I provided Claude with the Tool 1 spec block from planning.md including the input parameters, return value description, and failure mode, along with
the function stub from tools.py. Claude produced a function that filtered listings by price and size and scored them by keyword overlap across title, description, category, brand, style tags, and colors. I verified it handled all three filter parameters and returned an empty list rather than raising an exception. I also revised the listing text formatting to include additional item fields — specifically the price, description, and brand — so the top result displayed to the user contained enough detail to make an informed purchase decision rather than just the item title.

For `run_agent`, I provided Claude with the Planning Loop and State Management sections from planning.md, the agent architecture diagram, and the function stub from agent.py. Claude produced a planning loop that used the LLM to parse the user query and branched conditionally on the result of each tool call. I verified that the loop branched correctly on empty results and that session fields were set on each error path. I revised the error path behavior so that rather than setting session fields to None inside run_agent for every failure case, the empty state is handled in handle_query instead — which maps a populated session["error"] to the first output panel and returns empty strings for the outfit and fit card panels, keeping the error handling responsibility at the display layer rather than inside the planning loop itself.
## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
