
# WIRE: Web3 Integrated Reputation Engine

This project presents **WIRE**, a modular trust scoring engine for Ethereum wallets using on-chain behavioral features. It uses a Gradient Boosting model trained on diverse Ethereum transaction datasets to generate trust scores ranging from 0 to 100.

Please note that you might not need to run anything in data folder its just there to show how we collected the data using APIs and WebScraping and file were manually transferred to different folder.
Moreover the file "Generic_WIRE_Data.ipynb" is just for trail and error. The final file we merge data from different sources and merge those is in "Generic_WIRE_Data_2.ipynb" and the feature engineering exists in "Generic_WIRE_Data_3.ipynb" file.

Over that since we fetch data from Etherscan API, we call the Etherscan for 1 wallet each second hence with 35000 valid wallets, it would take 9 hours to run to collect data.

To test the results, you can run "model/Generic_WIRE_Model.ipynb" notebook to train the model on the data and get the results for AUC, Confusion Matrix and export the models. To test that in real scenario, you can test it in "pipeline/Generic_WIRE_Pipeline.ipynb" file or run the frontend or backend to test a wallet visually.

---

## 📁 Folder Structure

```
WIRE_CSCE665_Submission/
├── app/
│   ├── backend/                 # FastAPI backend for model inference
│   └── frontend/                # ReactJS-based front-end
│
├── data/                        # Raw wallet datasets and feature engineering notebooks
│   ├── eth_addresses.csv
│   ├── ethereum_addresses.csv
│   ├── wallets_only.csv
│   ├── Generic_WIRE_Data.ipynb
│   ├── Generic_WIRE_Data_2.ipynb
│   └── Generic_WIRE_Data_3.ipynb
│
├── models/                      # ML model and visualization
│   ├── combined_wallets_with_transactions_and_balances_3.csv
│   ├── Generic_WIRE_Model.ipynb
│   └── Generic_WIRE_Visualisation.ipynb
│
├── notebooks/                   # Python Notebooks
│   ├── data_preprocessing
│   │   ├── Generic_WIRE_Data_2.ipynb
│   │   ├── Generic_WIRE_Data_3.ipynb
│   │   └── Generic_WIRE_Data.ipynb
│   ├── modeling
│   │   └── Generic_WIRE_Model.ipynb
│   └── visualization
│       └── Generic_WIRE_Visualisation.ipynb
│
├── pipeline/                   # Model pipeline and saved artifacts
│   └── Generic_WIRE_Pipeline.ipynb
│
├── scripts/scraping/           # NodeJS scripts for scraping Etherscan
│   ├── index.js
│   ├── ethereum_addresses.json
│   ├── package.json
│   └── node_modules/
│
└── visualization/              # Output plots and visuals (if any)
```

---

## ⚙️ Setup Instructions

### 1. Clone and Open Repository
```bash
cd WIRE_CSCE665_Submission
```

### 2. Create and Activate Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ If `requirements.txt` is missing, install manually:
```bash
pip install pandas scikit-learn matplotlib seaborn jupyter fastapi uvicorn
```

---

## 🚀 How to Run the Project

### A. Model Training / Pipeline
Run from Jupyter Notebook:
- `pipeline/Generic_WIRE_Pipeline.ipynb` trains and saves model artifacts (`.pkl` files)
- `model/Generic_WIRE_Model.ipynb` visualizes training results and get training results

### B. Launch Backend Server
```bash
cd app/backend
uvicorn main:app --reload
```

### C. Launch Frontend (Optional)
```bash
cd app/wire-wallet-ui
npm install
npm run dev
```
Open the frontend URL at `localhost:3000` for the UI to function.
Make sure backend is running at `localhost:8000` for the backend to function.

---

## 🧪 Test Dataset
- Use files like `test_wallet_trust_scores.csv` to run predictions or visualize accuracy in `Generic_WIRE_Visualisation.ipynb`

---

## 🧩 Additional Notes
- The model is explainable and lightweight
- Planned improvements include phishing detection via threat intelligence integration
- UI and API are modular and easy to extend
