# Classification_Assignment

An assignment on data classification for Reporting with AI.

Jim Justice, governor-turned-senator of West Virginia, adopted a bulldog in 2019 named Babydog. Babydog became the face of West Virginia's COVID-19 vaccine time, and gradually showed up more and more to his press briefings as govenor.

For this project, we analyze the final 50 press briefings under Justice's governorship that were streamed to YouTube, classifying whether or not BabyDog made a visual appearance using both manual annotation and AI-assisted classification via Ollama.

## 🎯 Annotation Methodology

This project implements **annotation journalism** adapted for visual classification:
- **Visual-Only:** We examine video appearances only (no transcripts)
- **Manual Path:** Human annotators watch each video and mark Y/N for BabyDog presence
- **AI Path:** Ollama (qwen2.5:4b) processes videos programmatically for automated classification
- **Output:** Both methods produce identical CSV schema for intercoder reliability analysis

## 📋 Quick Start

### 1. Environment Setup

Activate the Python virtual environment:
```bash
source .venv/bin/activate
```

### 2. Prepare Data & Verify Setup

Run the classification notebook to verify the data is loaded correctly:
```bash
jupyter execute scripts/analysis/classification.ipynb
```

This command:
- Loads 50 press briefings from `data/import/clean/all-briefings.csv`
- Verifies all imports and dependencies work
- Sets up the analysis framework

### 3. Launch the Annotation Tool

Start a local SvelteKit development server:
```bash
npm run dev
```

Then open your browser to `http://localhost:5173` and begin annotating.

**Workflow:**
1. Enter your name at the start
2. Watch each of 50 videos in sequence
3. Mark Y/N for BabyDog presence
4. Your results are saved to `data/export/human/[YOUR_NAME].csv`

**Keyboard Shortcuts in Annotation Tool:**
- **Y** - Mark video as containing BabyDog
- **N** - Mark video as NOT containing BabyDog  
- **S** - Skip current video
- **B** - Undo previous annotation
- **I** - Mark as "interesting" for review
- **Note** - Add optional reviewer notes

### 4. Export Your Annotations

After annotating all 50 videos, click the "Download CSV" button. Your file will be named `[YOUR_NAME].csv` and should be saved to `data/export/human/[YOUR_NAME].csv`.

**CSV Schema:**
- `video_id` - YouTube video ID
- `title` - Press briefing title
- `date` - Briefing date
- `youtube_link` - Full YouTube URL
- `contains_babydog` - Your classification (true/false/null)
- `interesting` - Flagged segments requiring attention
- `reviewer` - Your name
- `note` - Any additional notes

### 5. Run Ollama AI Classification

After human annotators are finished, classify all videos using Ollama:
```bash
jupyter execute scripts/analysis/classification_ollama.ipynb
```

**Prerequisites:**
- Ollama installed and running locally: `ollama serve`
- Model pulled: `ollama pull qwen2.5:4b`

This notebook will:
- Load 50 videos from `data/import/clean/all-briefings.csv`
- Call Ollama to classify each video for BabyDog presence
- Generate `data/export/ai_cleaned-up/ollama.csv` with identical schema to human annotations
- Output summary statistics (total videos, BabyDog count)

### 6. Run Intercoder Reliability Analysis

After human annotators and Ollama classification are complete, compare results:
```bash
jupyter execute scripts/review/intercoder_reliability.ipynb
```

This notebook will:
- Load all annotator CSVs from `data/export/human/`
- Load Ollama classifications from `data/export/ai_cleaned-up/ollama.csv`
- Calculate Cohen's Kappa between all pairs (human-human, human-Ollama)
- Calculate overall agreement percentages
- Identify videos with disagreement
- Generate visualizations of agreement patterns
- Save results to `data/export/intercoder_agreement.png`

## 📊 Data Flow

**Input (Baseline Dataset):**
```
data/import/clean/all-briefings.csv
  ├─ 50 press briefings
  └─ Columns: video_id, title, date, youtube_link
```

**Output (4 Annotated CSV Files):**
```
data/export/
├─ human/
│   ├─ [USERNAME1].csv           (Human annotator 1)
│   ├─ [USERNAME2].csv           (Human annotator 2 - optional)
│   └─ [etc].csv                 (Additional human annotators)
├─ ai_cleaned-up/
│   └─ ollama.csv                (Ollama AI-generated annotations)
└─ intercoder_agreement.png      (Comparison visualization)
```

**All CSV files have identical schema:**
- `video_id` - YouTube video ID
- `title` - Press briefing title
- `date` - Briefing date
- `youtube_link` - Full YouTube URL
- `contains_babydog` - Classification: "True", "False", or empty (skipped)
- `interesting` - Flagged segments requiring attention
- `reviewer` - Annotator name (human name or "Ollama")
- `note` - Additional notes

## 📂 Project Structure

```
├── components/                 # SvelteKit annotation component
│   ├── +page.svelte           # Route entry point
│   ├── AnnotationTool.svelte   # Main annotation interface
│   ├── styles.css             # Component styling
│   └── stores.js              # State management
├── data/
│   ├── import/
│   │   ├── raw/               # Original YouTube URLs
│   │   └── clean/             # all-briefings.csv (50 videos - baseline dataset)
│   └── export/
│       ├── human/             # Human annotator results (USERNAME.csv)
│       └── ai_cleaned-up/     # Ollama AI-generated annotations (ollama.csv)
├── scripts/
│   ├── analysis/
│   │   └── classification.ipynb       # Load & verify baseline dataset
│   ├── review/
│   │   └── intercoder_reliability.ipynb  # Compare multiple annotators & calculate agreement
│   ├── setup/
│   │   └── txt_to_csv.ipynb              # Data cleaning utilities
│   └── data/
│       └── import/                       # Data loading scripts
├── notes/
│   └── codebook.md            # Annotation guidelines
└── README.md
```

## 🔧 Commands Reference

| Task | Command |
|------|---------|
| Activate environment | `source .venv/bin/activate` |
| Prep baseline data | `jupyter execute scripts/analysis/classification.ipynb` |
| Start annotation UI | `npm run dev` |
| View UI in browser | Open `http://localhost:5173` |
| Export human annotations | Click "Download CSV" in browser → save to `data/export/human/[NAME].csv` |
| Run Ollama AI | `jupyter execute scripts/analysis/classification_ollama.ipynb` |
| Compare annotations | `jupyter execute scripts/review/intercoder_reliability.ipynb` |

## 📊 Annotation Dataset

**File:** `data/export/ai_original/babydog-sightings.csv`

**Contents:**
- 50 press briefings from December 2021 to January 2025
- Video titles, YouTube links, and dates
- Ready for annotation

**Columns:**
```
video_id,title,date,youtube_link
```

## ✅ Annotation Workflow

1. **Setup** → Activate environment and run data prep notebook
2. **Annotate** → Launch SvelteKit tool and classify each video
3. **Export** → Download your labeled CSV
4. **Analyze** → Compare multiple annotator results with reliability metrics
5. **Report** → Document findings and disagreement patterns

## 📖 Annotation Guidelines

Refer to [codebook.md](notes/codebook.md) for detailed annotation instructions and BabyDog identification criteria.

## 🤖 AI Classification with Ollama

**Step 1: Set up Ollama locally**
```bash
brew install ollama           # macOS
ollama serve                  # Start the Ollama server
ollama pull qwen2.5:4b        # Download the qwen model
```

**Step 2: Run AI classification notebook**
```bash
jupyter execute scripts/analysis/classification_ollama.ipynb
```

This processes all 50 videos through Ollama and outputs to `data/export/ai_cleaned-up/ollama.csv`.

## 📈 Reliability Analysis

After running human annotations and Ollama classification, compare results:

```bash
jupyter execute scripts/review/intercoder_reliability.ipynb
```

Outputs:
- **Cohen's Kappa** (κ) for all annotator pairs
- **Agreement rates** between reviewers
- **Disagreement analysis** showing which videos have split decisions
- **Heatmaps & charts** in `data/export/intercoder_agreement.png`

---

**Last Updated:** November 2026