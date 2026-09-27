# PromptBP Framework

## Definition

PromptBP is a structured prompting framework that turns vague prompting into a controlled instruction system.

It is designed to improve:
- execution fidelity
- repeatability
- clarity
- evaluation
- portability across tasks

## The Seven Layers

### 1. Role
Defines what the model is acting as.
Purpose:
- constrain behavior
- anchor domain posture
- reduce generic response patterns

### 2. Objective
Defines the exact result required.
Purpose:
- eliminate open-ended drift
- force task completion toward a measurable target

### 3. Inputs
Defines context, variables, source material, constraints, and dependencies.
Purpose:
- provide working memory
- prevent missing-context failure

### 4. Output Format
Defines how the response must be structured.
Purpose:
- create predictable outputs
- reduce reformatting overhead
- improve downstream usability

### 5. Performance Rules
Defines non-negotiable quality conditions.
Purpose:
- prevent weak output modes
- enforce standards
- create sharper control over model behavior

### 6. Style
Defines tone, density, voice, and rhetorical posture.
Purpose:
- align output to use-case and audience
- avoid mismatched delivery

### 7. Recursive Check
Defines a final self-review loop.
Purpose:
- improve quality before response
- catch ambiguity
- tighten execution

## Core Principle

PromptBP works because it separates prompt construction into distinct control surfaces.
Instead of hoping the model “gets it,” the prompt explicitly defines:
- who it is
- what it must do
- what it has to work with
- how it must respond
- what quality bar it must clear

## Failure Modes It Reduces

- vague objectives
- under-specified inputs
- inconsistent output structure
- style drift
- generic filler
- weak final polish
- poor reusability

## Best Practice

Do not rewrite the whole prompt every time.
Refine the weakest layer first:
- weak tone -> fix Style
- bad structure -> fix Output Format
- fuzzy result -> fix Objective
- incomplete execution -> fix Performance Rules or Inputs
