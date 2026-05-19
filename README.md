User Request
     ↓
Intent Analyzer
     ↓
Project Architect Agent
     ↓
Planner Agent
     ↓
Task + File Breakdown
     ↓
Generate File Tree
     ↓
Generate Files One-by-One
     ↓
Save Files
     ↓
Dependency Generator
(requirements.txt, package.json)
     ↓
Docker Sandbox Executor
     ↓
Collect Output + Errors
     ↓
              Error?
         ↙              ↘
       Yes              No
        ↓                ↓
 Debugger Agent     Test Generator
        ↓                ↓
 Refiner Agent      Run Tests
        ↓                ↓
 Retry Loop        Evaluator Agent
          ↘        ↙
         README Generator
                ↓
      Dockerfile + .env.example
                ↓
         Memory Update
                ↓
        Zip Entire Project
                ↓
        Download Project