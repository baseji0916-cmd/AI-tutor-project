# GrowthPilot Architecture

## Overview

GrowthPilot follows **Clean Architecture** with clear separation between:

- **Presentation** (Frontend React PWA)
- **Application** (FastAPI routes, use cases)
- **Domain** (business logic, entities)
- **Infrastructure** (database, OpenAI, LangGraph)

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React PWA)                  │
│  Dashboard · Goals · Missions · Timeline · Coach Chat   │
└─────────────────────────┬───────────────────────────────┘
                          │ REST API
┌─────────────────────────▼───────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌─────────┐  ┌──────────┐  ┌────────────────────────┐  │
│  │   API   │→ │ Services │→ │ Domain (Models/Rules)  │  │
│  └─────────┘  └────┬─────┘  └────────────────────────┘  │
│                    │                                     │
│  ┌─────────────────▼─────────────────────────────────┐  │
│  │              LangGraph Multi-Agent Graph             │  │
│  │  Goal · Planner · Memory · Reflection · Coach ·   │  │
│  │  Recommendation · Future Sim · Timeline              │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              SQLite (Users, Goals, DNA, Logs)          │
└─────────────────────────────────────────────────────────┘
```

## Multi-Agent System

| Agent | Responsibility |
|-------|----------------|
| **Goal Agent** | Goal analysis, realism check, sub-goal generation |
| **Planner Agent** | Monthly / weekly / daily plans |
| **Memory Agent** | User data, goals, execution logs, Growth DNA |
| **Reflection Agent** | Failure analysis, pattern detection |
| **Recommendation Agent** | Goals, books, skills, habits |
| **Coach Agent** | Personality-based coaching feedback |
| **Future Simulation Agent** | Achievement probability, scenarios |
| **Timeline Agent** | Growth timeline and story |

## Core Metrics

- **Progress Rate** — task completion vs plan
- **Achievement Rate** — goals completed vs set
- **Growth Score** — composite score from consistency, DNA, and outcomes
- **Growth DNA** — focus time, failure/success patterns, execution style, feedback preference

## Coach Personalities

Each personality changes **coaching strategy**, not just tone:

- 선생님형 (Teacher)
- 친구형 (Friend)
- 열정 코치형 (Passion Coach)
- 데이터 분석형 (Data Analyst)
- CEO형 (CEO)
- 츤데레형 (Tsundere)
