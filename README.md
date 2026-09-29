Demo Link:  http://localhost:8503
## SkillPath AI 🎓🤖

**SkillPath AI** is an AI-powered personalized learning and skill recommendation system designed to create adaptive learning paths based on a learner's performance, knowledge level, and progress.

The project combines **Reinforcement Learning, recommendation techniques, quiz generation, learner simulation, and performance evaluation** to dynamically recommend suitable learning content.

---

## 🚀 Features

* 🧠 **Personalized Learning Paths**
  Dynamically recommends learning activities based on the learner's current knowledge and performance.

* 🤖 **Deep Q-Network (DQN)**
  Uses reinforcement learning to learn effective learning-path recommendations.

* 👨‍🎓 **Simulated Learner**
  Simulates learner behavior, progress, and responses to evaluate the recommendation system.

* 📝 **AI Quiz Generation**
  Generates quiz questions based on learning content and topics.

* 📊 **Performance Metrics**
  Tracks and evaluates learner performance and recommendation effectiveness.

* 🔄 **Adaptive Recommendations**
  Adjusts recommended learning activities according to learner state and previous outcomes.

* 🧪 **Offline Training & Evaluation**
  Supports training the reinforcement learning agent and evaluating its performance before deployment.

---

## 🏗️ Project Structure

```text
Skill-path-AI/
│
├── agent_utils.py              # Utility functions for the RL agent
├── data.py                     # Dataset and learning data handling
├── dqn_agent.py                # Deep Q-Network implementation
├── dqn_weights.pkl             # Trained DQN model weights
├── environment.py              # Learning environment for reinforcement learning
├── evaluate.py                 # Model evaluation
├── generate_quiz_bank.py       # Quiz/question bank generation
├── main.py                     # Main application entry point
├── recommender.py              # Personalized learning recommendation system
├── simulated_learner.py        # Simulated learner environment
├── train_offline.py            # Offline training pipeline
├── requirements.txt            # Python dependencies
│
├── qgen/                       # Question generation components
│
├── metrics/                    # Evaluation and performance metrics
│
└── README.md                   # Project documentation
```

---

## ⚙️ Technologies Used

* **Python**
* **Reinforcement Learning**
* **Deep Q-Network (DQN)**
* **Machine Learning**
* **Recommendation Systems**
* **Natural Language Processing**
* **AI-based Quiz Generation**
* **NumPy**
* **Scikit-learn**
* Other Python libraries listed in `requirements.txt`

---

## 🔄 System Workflow

```text
                 ┌─────────────────────┐
                 │     Learner Data    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Learner State      │
                 │  & Performance      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   DQN Agent         │
                 │ Reinforcement       │
                 │ Learning            │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Personalized        │
                 │ Recommendation      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Learning Activity   │
                 │ / Quiz              │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Learner Feedback    │
                 │ & Performance       │
                 └──────────┬──────────┘
                            │
                            └──────────────► Updated Learner State
```

---

## 🧠 Reinforcement Learning Approach

SkillPath AI models personalized learning as a **reinforcement learning problem**.

The system considers:

* **State:** Current learner knowledge and performance
* **Action:** Selection of the next learning activity/topic
* **Reward:** Improvement in learner performance
* **Next State:** Updated learner knowledge after completing the activity

The DQN agent learns a policy that attempts to select learning activities that maximize the learner's long-term improvement.

---

## 📋 Installation

### 1. Clone the repository

```bash
git clone https://github.com/deepikadharanikota/Skill-path-AI.git
```

### 2. Navigate to the project

```bash
cd Skill-path-AI
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

Run the main application:

```bash
python main.py
```

---

## 🏋️ Training

To train the reinforcement learning model offline:

```bash
python train_offline.py
```

The trained model weights can be stored in:

```text
dqn_weights.pkl
```

---

## 📊 Evaluation

To evaluate the trained model:

```bash
python evaluate.py
```

The evaluation components in the `metrics/` directory can be used to analyze system performance.

---

## 📝 Quiz Generation

Quiz/question generation functionality can be executed through:

```bash
python generate_quiz_bank.py
```

The `qgen/` directory contains the components responsible for question generation.

---

## 🎯 Project Goals

The main goal of SkillPath AI is to build an intelligent learning system that:

1. Understands the learner's current skill level.
2. Identifies areas that need improvement.
3. Selects appropriate learning activities.
4. Uses learner feedback to improve recommendations.
5. Continuously adapts the learning path.
6. Evaluates the effectiveness of personalized recommendations.

---

## 🔮 Future Enhancements

* 🌐 Web-based learning dashboard
* 👤 User authentication and learner profiles
* 📈 Real-time progress visualization
* 🤖 Improved AI-generated learning content
* 🎯 More advanced learner modeling
* ☁️ Cloud deployment
* 📱 Mobile-friendly interface
* 🔍 Explainable recommendations
* 🧠 Integration with additional reinforcement learning algorithms

---


