# Architecture

## Goal

Convert robot-task evidence into an auditable episode evaluation. The project separates **perception** from **evaluation** so benchmark claims can be measured rather than assumed.

## Planned flow

```text
Robot episode/video
        |
        v
Dataset / video adapter
        |
        v
Frame + metadata extraction
        |
        v
Object / robot state tracking
        |
        v
Temporal stage detector
        |
        v
Task evaluator
        |
        +--> JSON evaluation report
        +--> metrics / visual report
```

## Current implementation

Only the task-evaluator layer is implemented. It consumes explicit stage observations (`True`, `False`, or unknown/`None`) and produces deterministic reports. This gives later perception models a stable interface and makes unit testing possible before introducing model uncertainty.

## Evaluation principles

- Never label generated/demo results as benchmark results.
- Keep dataset provenance and licensing documented.
- Split training/evaluation data before reporting model metrics.
- Preserve unknown/ambiguous states rather than silently converting them to failure.
- Report failure-stage logic separately from perception confidence.
