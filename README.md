# Local DeepSearch

Local DeepSearch combines local context with internet search to enhance query rewriting and Gemini calls. This approach eliminates the need for manual evaluation to determine information sufficiency. Gemini acts as an intelligent agent, dynamically deciding how much additional exploration is required to provide the best possible answer to a query.

![Project Workflow](https://pbs.twimg.com/media/Gmpt5GZXsAAqzWC?format=png&name=small)


## Getting Started

Follow these steps to set up and run the project:

### Prerequisites

- Ensure Python version 3.10 or higher is installed.
- It is recommended to use a Python virtual environment.

### Installation

```bash
# Clone the repository
git clone https://github.com/StarlightSearch/EmbedAnything.git

# Navigate to the project directory
cd deep-searcher

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Code

```bash
# Execute the main script
python fusion.py
```

## Project Overview

Local DeepSearch enhances query processing by combining local context with internet search results. It leverages two core components: `fusion.py` for query refinement and `store.py` for efficient data management.

[Watch the demo](https://youtu.be/scjNt_DKE9s)

## Components

### `fusion.py`
This script integrates local context data with internet search results. It processes input queries, refines them, and improves the accuracy and relevance of the responses.

### `store.py`
This script manages the storage and retrieval of local context data. It ensures efficient data handling, enabling quick access during query processing.

## Usage Workflow

How the Agent Sets This Flag
After each research iteration, Gemini evaluates the collected information against specific criteria: CopyBased on this observations, you have two options: 
1. Find knowledge gaps that still need to be explored and write 3 different queries that explore different perspectives of the topic. If this is the case set the done flag to False.\n
 2. If there are no more knowledge gaps and you have enough information related to the topic, you dont have to provide any more queries and you can set the done flag to True. When Gemini sets "done": false, it's essentially saying: "I've analyzed what we know so far, and there are still important aspects of this topic we haven't covered adequately." Evaluation Criteria The system uses sophisticated criteria to make this determination: CopyBefore setting the done flag to true, make sure that the following conditions are met: 1. You have explored different perspectives of the topic 2. You have collected some opposing views \n
  3. You have collected some supporting views \n
  4. You have collected some views that are not directly related to the topic but can be used to


## Contributing

We welcome contributions! Feel free to submit issues or create pull requests to improve this project.

## License

This project is open-source and available under the [Apache License](LICENSE).



