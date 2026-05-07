# AI Classifier Rules

Questboard uses lightweight, deterministic NLP-like rules instead of model training.

## Inputs

- task title
- task description
- extracted numeric values such as pages or minutes
- keyword families for reading, studying, workout, coding, and cleaning

## Output Fields

- detected category
- estimated workload
- estimated duration
- detected difficulty
- AI multiplier
- explanation
- anomaly risk rules

## Examples

- `Read 10 pages` -> reading, easy, 15 minutes, 1.0 multiplier
- `Read 100 pages` -> reading, medium, about 120 minutes, 1.4 multiplier
- `Read 300 pages` -> reading, hard, about 360 minutes, 2.0 multiplier
- `Read 500 pages` -> reading, extreme, about 600 minutes, 2.5 multiplier
- `Build authentication system` -> coding, extreme, 240 minutes, 2.5 multiplier
- `Fix bug` -> coding, medium, 60 minutes, 1.5 multiplier

## Anti-Abuse Logic

- Flag if actual duration is greater than 3x the AI estimate.
- Flag if actual duration is unrealistically short for the classified task.
- Cap XP by difficulty tier.
- Keep completion allowed even when flagged, but store the anomaly details in the XP breakdown and cap the reward.

## XP Formula

```text
XP = round(completion_bonus + ((actual_duration_minutes / 3) * difficulty_multiplier))
```

Difficulty multipliers:

- easy = 1.0
- medium = 2.0
- hard = 3.5
- extreme = 5.0

Completion bonuses:

- easy = 2
- medium = 6
- hard = 12
- extreme = 20

Difficulty caps:

- easy = 100
- medium = 250
- hard = 500
- extreme = 800
