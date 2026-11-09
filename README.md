# AI Traveller

A lightweight India-only travel planning website with a React frontend and Python backend.

## Run

```bash
python server.py
```

Then open:

```text
http://127.0.0.1:8000
```

The website asks for:

- Starting location in India
- Destination in India
- Number of trip days
- Number of people
- Total budget in INR
- Special specifications or preferences

It then generates transportation suggestions, accommodation estimates, a day-by-day itinerary, food guidance, budget breakdown, optimization tips, and a final recommendation.

The website also includes:

- Register and login pages
- Route map-style travel steps
- Destination transportation facilities
- Special local food suggestions
- Famous and beautiful locations for travellers

Demo user accounts are stored in `users.json` with hashed passwords.

## CLI

You can still run the original terminal version:

```bash
python travel_planner.py
```

## Notes

- Prices are estimates in INR.
- The planner supports common Indian cities and destinations.
- If the estimated trip cost exceeds the budget, the output suggests cheaper alternatives.
