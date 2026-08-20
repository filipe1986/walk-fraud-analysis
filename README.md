# Fraud Detection & Risk Scoring Engine 🕵️‍♂️📊

A robust, Python-based data analysis engine designed to identify fraudulent transactions by analyzing behavioral patterns, velocity, and device identifiers. This script processes transaction datasets, flags suspicious activity using pandas, and automatically assigns a cumulative risk score to isolate the most dangerous transactions.

## 🚀 Key Features & Fraud Signals

This engine evaluates transactions against several distinct fraud vectors:

*   **Velocity Tracking (Card Testing/Bots):** Identifies impossibly fast transactions (under 60 seconds) indicating automated scripts or rapid-fire card testing.
*   **Ghost Device Detection:** Flags transactions missing critical identifiers (e.g., `NaN` device IDs) which often point to API-level spam bypassing standard web/app interfaces.
*   **High-Value Cashouts:** Dynamically calculates the top 5% of transaction amounts to catch fraudsters attempting to extract maximum value before a card is blocked.
*   **Behavioral Spikes:** Compares transaction amounts against a user's historical average to detect account takeovers (spikes >3x the user's norm).

## 🧮 Risk Scoring Algorithm

Rather than relying on rigid "block/allow" rules that cause high false positives, this system uses a weighted risk scoring matrix. 

Transactions start at a score of `0`. Points are added based on triggered rules:
*   **+100 Points:** Velocity trigger (under 60s from last transaction).
*   **+30 Points:** Missing/Ghost Device ID.
*   **+20 Points:** Global High Amount (Top 5%).

**Action Thresholds:**
*   **Score >= 130:** High probability of fraud (Automated Block).
*   **Score >= 100:** Suspicious activity (Send to manual review queue).
*   **Score < 100:** Standard activity (Approve).

## 🛠️ Tech Stack & Setup

*   **Language:** Python 3.x
*   **Libraries:** Pandas (Data manipulation & vectorized operations)
*   **Environment:** Linux (Ubuntu) / standard Python virtual environment

