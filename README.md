# BTech Python

## Prerequisites

- [Cloudflare 1.1.1.1](https://one.one.one.one/)

- Python >= 3.7

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

To scrape data, please make sure [1.1.1.1](https://one.one.one.one/) is on, then run

```bash
python 00_scrape.py
```
After that run cleaning 
Now the Results Were Achieved
Data Collection:
JSON files were generated using a scraping script (00_scrape.py), creating the transactions folder with files like 292977191.json.
Data Cleaning:
The cleaning.py script reads all JSON files in the transactions folder using UTF-8 encoding to handle special characters.
It extracts features: fee (transaction fee in lamports), sol_value (converted to float), num_instructions (count of parsed instructions), and status (1 for Success, 0 for Fail).
Error handling skips transactions with missing or invalid data.
Model Training:
A Random Forest Classifier (RandomForestClassifier) with 100 trees is trained on 80% of the data.
Features are split into training and testing sets (80/20 split) for evaluation.
Evaluation:
The model predicts transaction success and outputs accuracy and a classification report, achieving 0.989398104344751 accuracy.
