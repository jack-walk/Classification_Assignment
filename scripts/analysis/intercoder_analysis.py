#!/usr/bin/env python
"""
Intercoder Reliability Analysis
Compare annotations from Camila, Jack, and Ollama (transcript analysis)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import cohen_kappa_score
import matplotlib.pyplot as plt
import seaborn as sns

base_dir = Path(__file__).parent.parent.parent

print("📋 Loading all annotators' data...\n")

# Load human annotations
human_dir = base_dir / 'data' / 'export' / 'human'
camila_df = pd.read_csv(human_dir / 'Camila.csv', dtype=str, keep_default_na=False)
jack_df = pd.read_csv(human_dir / 'Jack.csv', dtype=str, keep_default_na=False)

# Load AI annotation
ai_df = pd.read_csv(base_dir / 'data' / 'export' / 'ai' / 'ollama.csv', dtype=str, keep_default_na=False)

print(f"✅ Camila: {len(camila_df)} videos")
print(f"✅ Jack: {len(jack_df)} videos")
print(f"✅ Ollama: {len(ai_df)} videos")

# Combine all annotations
all_data = pd.concat([camila_df, jack_df, ai_df], ignore_index=True)

print(f"\n📊 Total annotations: {len(all_data)}")
print(f"Unique reviewers: {all_data['reviewer'].nunique()}")
print(f"Reviewers: {', '.join(all_data['reviewer'].unique())}\n")

# Pivot: rows = video_id, columns = reviewer, values = contains_babydog
df_wide = all_data.pivot_table(
    index='video_id',
    columns='reviewer',
    values='contains_babydog',
    aggfunc='first'
)

col_reviewers = df_wide.columns.tolist()
print(f"Videos in comparison: {len(df_wide)}\n")

# Calculate raw agreement
has_answer = df_wide[col_reviewers].isin(['True', 'False'])
has_same_answer = df_wide[col_reviewers].nunique(axis=1) == 1
df_wide['unanimous'] = has_same_answer & has_answer.all(axis=1)

print(f"--- Raw Agreement ---")
print(f"Unanimous agreement: {df_wide['unanimous'].mean():.1%}")
print(f"Videos with disagreement: {(~df_wide['unanimous']).sum()}\n")

# Calculate pairwise Cohen's Kappa
print(f"--- Pairwise Cohen's Kappa ---")
kappa_scores = {}
for i, rev1 in enumerate(col_reviewers):
    for rev2 in col_reviewers[i+1:]:
        # Only compare videos where both made a True/False annotation
        mask = (df_wide[rev1].isin(['True', 'False'])) & (df_wide[rev2].isin(['True', 'False']))
        if mask.sum() > 0:
            # Convert to binary (True=1, False=0)
            y1 = (df_wide.loc[mask, rev1] == 'True').astype(int)
            y2 = (df_wide.loc[mask, rev2] == 'True').astype(int)
            kappa = cohen_kappa_score(y1, y2)
            kappa_scores[f"{rev1} vs {rev2}"] = kappa
            print(f"{rev1} vs {rev2}: κ = {kappa:.3f} (n={mask.sum()})")

if kappa_scores:
    avg_kappa = np.mean(list(kappa_scores.values()))
    print(f"\nMean Cohen's Kappa: {avg_kappa:.3f}")
else:
    print("Not enough reviewers or complete annotations for Cohen's Kappa")

# Create comparison table for all 3
print(f"\n--- Comparison Table (All 3 Annotators) ---")
comparison_summary = []
for idx in df_wide.index:
    row_data = {'video_id': idx}
    for rev in col_reviewers:
        row_data[rev] = df_wide.loc[idx, rev]
    
    # Check if unanimous
    votes = [df_wide.loc[idx, rev] for rev in col_reviewers if df_wide.loc[idx, rev] in ['True', 'False']]
    unanimous = len(set(votes)) == 1 if votes else False
    row_data['Consensus'] = '✅ Yes' if unanimous else '❌ No'
    comparison_summary.append(row_data)

comparison_df = pd.DataFrame(comparison_summary)
print(comparison_df.to_string(index=False))

# Save comparison table
output_comparison = base_dir / 'data' / 'export' / 'comparison_table.csv'
comparison_df.to_csv(output_comparison, index=False)
print(f"\n💾 Comparison table saved to data/export/comparison_table.csv")

# Count BabyDog appearances by reviewer
print(f"\n--- BabyDog Appearance Counts ---")
babydog_counts = (df_wide[col_reviewers] == 'True').sum()
total_reviewed = (df_wide[col_reviewers].isin(['True', 'False'])).sum()

for reviewer in col_reviewers:
    count = babydog_counts[reviewer]
    total = total_reviewed[reviewer]
    pct = count / total if total > 0 else 0
    print(f"{reviewer}: {count}/{total} videos ({pct:.1%})")

# Show disagreements
print(f"\n--- Disagreement Analysis ---")
df_disagreement = df_wide[~df_wide['unanimous']]
if len(df_disagreement) > 0:
    print(f"Total videos with disagreement: {len(df_disagreement)}\n")
    print("Videos with disagreement:")
    for idx, row in df_disagreement.iterrows():
        annotations = {rev: row[rev] for rev in col_reviewers}
        print(f"  {idx}: {annotations}")
else:
    print("Perfect agreement! All reviewers agree on all videos.")

# Create visualizations
print("\n📊 Generating visualizations...\n")

if len(df_wide) > 0 and len(col_reviewers) > 1:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Heatmap 1: Reviewer annotations
    df_heatmap = df_wide[col_reviewers].copy()
    df_heatmap = df_heatmap.replace({'True': 1, 'False': 0, '': np.nan}).astype(float)
    
    sns.heatmap(df_heatmap, annot=False, cmap='RdYlGn_r', cbar_kws={'label': 'BabyDog'}, 
                ax=ax1, yticklabels=False)
    ax1.set_title(f'Annotation Pattern ({len(df_heatmap)} videos)')
    ax1.set_ylabel('Video ID')
    ax1.set_xlabel('Reviewer')
    
    # Chart 2: Agreement histogram
    agreement_counts = df_wide[col_reviewers].nunique(axis=1).value_counts().sort_index()
    ax2.bar(agreement_counts.index, agreement_counts.values, color=['green', 'orange', 'red'][:len(agreement_counts)])
    ax2.set_xlabel('Number of Different Answers')
    ax2.set_ylabel('Number of Videos')
    ax2.set_title('Agreement Distribution')
    ax2.set_xticks(agreement_counts.index)
    
    plt.tight_layout()
    plt.savefig(base_dir / 'data' / 'export' / 'intercoder_agreement.png', dpi=100, bbox_inches='tight')
    print("✅ Saved visualization to data/export/intercoder_agreement.png")
    plt.close()

print("\n✅ Intercoder reliability analysis complete!")
