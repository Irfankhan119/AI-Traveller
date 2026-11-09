from dataclasses import dataclass
import math
import re


INDIAN_LOCATIONS = {
    "agra", "ahmedabad", "alleppey", "amritsar", "andaman", "aurangabad",
    "bengaluru", "bangalore", "bhopal", "bhubaneswar", "chandigarh",
    "chennai", "coimbatore", "darjeeling", "delhi", "dehradun", "gangtok",
    "goa", "guwahati", "gwalior", "hyderabad", "indore", "jaipur",
    "jaisalmer", "jodhpur", "kochi", "kolkata", "leh", "lucknow",
    "madurai", "manali", "mangalore", "mumbai", "munnar", "mysuru",
    "mysore", "nainital", "ooty", "pondicherry", "puducherry", "pune",
    "rishikesh", "shimla", "srinagar", "udaipur", "varanasi", "vizag",
    "visakhapatnam",
}


CITY_REGIONS = {
    "delhi": "north", "jaipur": "north", "agra": "north", "amritsar": "north",
    "rishikesh": "north", "manali": "north", "shimla": "north", "nainital": "north",
    "udaipur": "north", "jodhpur": "north", "jaisalmer": "north", "leh": "north",
    "srinagar": "north", "chandigarh": "north", "dehradun": "north",
    "mumbai": "west", "pune": "west", "goa": "west", "ahmedabad": "west",
    "aurangabad": "west", "indore": "west",
    "bengaluru": "south", "bangalore": "south", "chennai": "south",
    "hyderabad": "south", "kochi": "south", "munnar": "south",
    "alleppey": "south", "ooty": "south", "mysuru": "south", "mysore": "south",
    "madurai": "south", "pondicherry": "south", "puducherry": "south",
    "mangalore": "south", "coimbatore": "south",
    "kolkata": "east", "bhubaneswar": "east", "darjeeling": "east",
    "gangtok": "east", "guwahati": "east", "vizag": "east",
    "visakhapatnam": "east",
    "bhopal": "central", "gwalior": "central", "lucknow": "north",
    "varanasi": "north", "andaman": "island",
}


DESTINATION_THEMES = {
    "jaipur": ["Amber Fort", "City Palace", "Hawa Mahal", "Jantar Mantar", "local bazaars"],
    "goa": ["Calangute or Baga Beach", "Old Goa churches", "Fort Aguada", "Panjim Latin Quarter", "beach cafes"],
    "agra": ["Taj Mahal", "Agra Fort", "Mehtab Bagh", "Sadar Bazaar", "Fatehpur Sikri"],
    "varanasi": ["Kashi Vishwanath Temple", "Dashashwamedh Ghat", "Ganga boat ride", "Sarnath", "old city lanes"],
    "mumbai": ["Gateway of India", "Marine Drive", "Elephanta Caves", "Colaba Causeway", "Juhu Beach"],
    "delhi": ["Red Fort", "India Gate", "Qutub Minar", "Humayun's Tomb", "Chandni Chowk"],
    "udaipur": ["City Palace", "Lake Pichola", "Saheliyon Ki Bari", "Bagore Ki Haveli", "old city market"],
    "manali": ["Hadimba Temple", "Mall Road", "Solang Valley", "Vashisht", "Old Manali cafes"],
    "shimla": ["Mall Road", "The Ridge", "Jakhu Temple", "Kufri", "Christ Church"],
    "kochi": ["Fort Kochi", "Chinese Fishing Nets", "Mattancherry Palace", "Jew Town", "Marine Drive"],
    "munnar": ["tea gardens", "Eravikulam National Park", "Mattupetty Dam", "Top Station", "local spice shops"],
    "rishikesh": ["Triveni Ghat", "Lakshman Jhula area", "Beatles Ashram", "river rafting", "cafes by the Ganga"],
    "kolkata": ["Victoria Memorial", "Howrah Bridge", "Indian Museum", "Dakshineswar Temple", "Park Street"],
    "hyderabad": ["Charminar", "Golconda Fort", "Salar Jung Museum", "Hussain Sagar", "Laad Bazaar"],
    "bengaluru": ["Cubbon Park", "Lalbagh", "Bangalore Palace", "Church Street", "local breweries or cafes"],
    "bangalore": ["Cubbon Park", "Lalbagh", "Bangalore Palace", "Church Street", "local breweries or cafes"],
}


SPECIAL_FOODS = {
    "jaipur": ["dal baati churma", "pyaaz kachori", "ghewar", "laal maas"],
    "goa": ["fish curry rice", "prawn balchao", "bebinca", "poi bread"],
    "agra": ["petha", "bedai with aloo sabzi", "mughlai kebabs", "chaat"],
    "varanasi": ["kachori sabzi", "tamatar chaat", "malaiyyo", "banarasi paan"],
    "mumbai": ["vada pav", "pav bhaji", "bombay sandwich", "falooda"],
    "delhi": ["chole bhature", "parathas", "momos", "jalebi"],
    "udaipur": ["dal baati churma", "gatte ki sabzi", "mirchi vada", "kulhad chai"],
    "manali": ["siddu", "trout fish", "thukpa", "madra"],
    "shimla": ["chana madra", "siddu", "bun tikki", "local bakery snacks"],
    "kochi": ["appam with stew", "kerala sadya", "puttu kadala", "seafood curry"],
    "munnar": ["kerala sadya", "appam", "banana chips", "tea and spice snacks"],
    "rishikesh": ["aloo puri", "chole kulche", "satvik thali", "riverfront cafe food"],
    "kolkata": ["kathi roll", "mishti doi", "rosogolla", "fish curry"],
    "hyderabad": ["hyderabadi biryani", "haleem", "irani chai", "double ka meetha"],
    "bengaluru": ["masala dosa", "filter coffee", "idli vada", "mangalore buns"],
    "bangalore": ["masala dosa", "filter coffee", "idli vada", "mangalore buns"],
}


TRANSPORT_FACILITIES = {
    "jaipur": ["metro on limited routes", "e-rickshaws", "autos", "app cabs", "local buses"],
    "goa": ["rented scooters", "local buses", "taxis", "self-drive cars"],
    "agra": ["autos", "e-rickshaws", "taxis", "local buses"],
    "varanasi": ["e-rickshaws", "autos", "walking near ghats", "boat rides"],
    "mumbai": ["local trains", "metro", "BEST buses", "autos", "app cabs"],
    "delhi": ["metro", "DTC buses", "autos", "app cabs", "e-rickshaws"],
    "udaipur": ["autos", "app cabs", "walking in old city", "two-wheeler rentals"],
    "manali": ["local taxis", "shared jeeps", "walking near Mall Road", "rental bikes"],
    "shimla": ["local buses", "taxis", "walking near Mall Road", "toy train nearby"],
    "kochi": ["metro", "ferries", "autos", "buses", "app cabs"],
    "munnar": ["local taxis", "jeeps", "rental bikes", "private cab day tours"],
    "rishikesh": ["autos", "shared jeeps", "walking near ghats", "scooter rentals"],
    "kolkata": ["metro", "trams on selected routes", "buses", "yellow taxis", "ferries"],
    "hyderabad": ["metro", "TSRTC buses", "autos", "app cabs"],
    "bengaluru": ["metro", "BMTC buses", "autos", "app cabs"],
    "bangalore": ["metro", "BMTC buses", "autos", "app cabs"],
}


BEAUTIFUL_LOCATIONS = {
    "jaipur": ["Nahargarh Fort sunset point", "Patrika Gate", "Jal Mahal", "Amber Fort viewpoints"],
    "goa": ["Palolem Beach", "Fontainhas", "Dudhsagar Falls", "Chapora Fort sunset"],
    "agra": ["Taj Mahal sunrise view", "Mehtab Bagh", "Agra Fort", "Fatehpur Sikri"],
    "varanasi": ["Assi Ghat sunrise", "Dashashwamedh Ghat", "Sarnath", "Ganga riverfront"],
    "mumbai": ["Marine Drive", "Bandra Fort", "Elephanta Caves", "Sanjay Gandhi National Park"],
    "delhi": ["Lodhi Garden", "Humayun's Tomb", "India Gate lawns", "Qutub Minar complex"],
    "udaipur": ["Lake Pichola", "Sajjangarh Monsoon Palace", "Fateh Sagar Lake", "Ambrai Ghat"],
    "manali": ["Solang Valley", "Sethan Valley", "Jogini Falls", "Old Manali"],
    "shimla": ["The Ridge", "Kufri", "Chadwick Falls", "Mashobra"],
    "kochi": ["Fort Kochi beach", "Marine Drive", "Jew Town", "Kumbalangi village"],
    "munnar": ["Top Station", "Eravikulam National Park", "tea garden viewpoints", "Mattupetty Dam"],
    "rishikesh": ["Ganga ghats", "Neer Garh waterfall", "Beatles Ashram", "Lakshman Jhula area"],
    "kolkata": ["Victoria Memorial gardens", "Princep Ghat", "Howrah Bridge view", "Eco Park"],
    "hyderabad": ["Golconda Fort", "Hussain Sagar", "Qutb Shahi Tombs", "Durgam Cheruvu"],
    "bengaluru": ["Lalbagh", "Cubbon Park", "Nandi Hills", "Ulsoor Lake"],
    "bangalore": ["Lalbagh", "Cubbon Park", "Nandi Hills", "Ulsoor Lake"],
}


@dataclass
class TripInput:
    start: str
    destination: str
    days: int
    people: int
    budget: int
    specifications: str


@dataclass
class CostPlan:
    intercity_transport: int
    local_transport: int
    accommodation: int
    food: int
    activities: int
    miscellaneous: int

    @property
    def total(self) -> int:
        return (
            self.intercity_transport
            + self.local_transport
            + self.accommodation
            + self.food
            + self.activities
            + self.miscellaneous
        )


def normalize_location(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def title_location(value: str) -> str:
    return normalize_location(value).title()


def read_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value.")


def read_positive_int(prompt: str) -> int:
    while True:
        value = input(prompt).replace(",", "").strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
        print("Please enter a positive whole number.")


def read_location(prompt: str) -> str:
    while True:
        value = read_non_empty(prompt)
        key = normalize_location(value)
        if key in INDIAN_LOCATIONS:
            return key
        print("Please enter a known Indian city or destination.")
        print("Examples: Delhi, Jaipur, Goa, Mumbai, Manali, Kochi, Varanasi")


def ask_trip_details() -> TripInput:
    print("\nAI Travel Planning Agent - India Budget Trip Planner\n")
    start = read_location("Starting location in India: ")
    destination = read_location("Destination in India: ")
    days = read_positive_int("Number of trip days: ")
    people = read_positive_int("Number of people: ")
    budget = read_positive_int("Total budget in INR: Rs. ")
    specifications = read_non_empty(
        "Special specifications/preferences: "
    )
    return TripInput(start, destination, days, people, budget, specifications)


def trip_distance_band(start: str, destination: str) -> str:
    if start == destination:
        return "local"
    start_region = CITY_REGIONS.get(start, "unknown")
    destination_region = CITY_REGIONS.get(destination, "unknown")
    if start_region == destination_region:
        return "near"
    if "island" in {start_region, destination_region}:
        return "flight"
    return "far"


def travel_style(specifications: str, budget_per_person_per_day: float) -> str:
    text = specifications.lower()
    if any(word in text for word in ["luxury", "premium", "resort"]):
        return "premium-leaning, but adjusted to stay budget-aware"
    if any(word in text for word in ["family", "senior", "parents", "kids"]):
        return "comfortable family-friendly budget travel"
    if any(word in text for word in ["adventure", "trek", "rafting"]):
        return "budget adventure travel"
    if budget_per_person_per_day <= 1200:
        return "strict budget travel"
    if budget_per_person_per_day <= 2500:
        return "balanced budget travel"
    return "comfortable mid-budget travel"


def choose_transport(band: str, specifications: str) -> tuple[str, str, int]:
    text = specifications.lower()
    no_flight = "no flight" in text or "train" in text
    if band == "local":
        return "No intercity travel required", "Within city", 0
    if band == "near":
        return "Train or AC bus", "4-9 hours depending on route", 900
    if band == "flight" and not no_flight:
        return "Economy flight booked early", "2-5 hours plus airport time", 7500
    if no_flight:
        return "Sleeper/3AC train where available", "10-30 hours depending on route", 2200
    return "Train for budget, flight only if time is limited", "10-30 hours by train or 2-4 hours by flight", 2500


def nightly_hotel_cost(specifications: str, budget_per_person_per_day: float) -> int:
    text = specifications.lower()
    if any(word in text for word in ["hostel", "dorm"]):
        return 700
    if any(word in text for word in ["family", "senior", "parents", "kids"]):
        return 1800
    if any(word in text for word in ["luxury", "resort", "premium"]):
        return 3500
    if budget_per_person_per_day <= 1200:
        return 900
    if budget_per_person_per_day <= 2500:
        return 1500
    return 2300


def estimate_costs(trip: TripInput) -> CostPlan:
    budget_pppd = trip.budget / trip.people / trip.days
    band = trip_distance_band(trip.start, trip.destination)
    _, _, one_way_transport = choose_transport(band, trip.specifications)
    rooms = math.ceil(trip.people / 2)
    nights = max(trip.days - 1, 0)
    hotel_per_room = nightly_hotel_cost(trip.specifications, budget_pppd)
    daily_food_per_person = 450 if budget_pppd <= 1200 else 700 if budget_pppd <= 2500 else 1000
    daily_local_per_person = 180 if budget_pppd <= 1200 else 300 if budget_pppd <= 2500 else 450
    daily_activity_per_person = 200 if budget_pppd <= 1200 else 450 if budget_pppd <= 2500 else 750

    return CostPlan(
        intercity_transport=one_way_transport * 2 * trip.people,
        local_transport=daily_local_per_person * trip.days * trip.people,
        accommodation=hotel_per_room * nights * rooms,
        food=daily_food_per_person * trip.days * trip.people,
        activities=daily_activity_per_person * trip.days * trip.people,
        miscellaneous=max(500 * trip.people, int(trip.budget * 0.08)),
    )


def attractions_for(destination: str) -> list[str]:
    return DESTINATION_THEMES.get(
        destination,
        [
            "main city landmark",
            "old market or local bazaar",
            "popular temple/museum/viewpoint",
            "local food street",
            "nearby nature or heritage spot",
        ],
    )


def special_foods_for(destination: str) -> list[str]:
    return SPECIAL_FOODS.get(
        destination,
        ["local thali", "regional snacks", "street food in busy markets", "seasonal sweets"],
    )


def transport_facilities_for(destination: str) -> list[str]:
    return TRANSPORT_FACILITIES.get(
        destination,
        ["local buses", "autos", "shared cabs", "walking in central areas"],
    )


def beautiful_locations_for(destination: str) -> list[str]:
    return BEAUTIFUL_LOCATIONS.get(
        destination,
        ["main viewpoint", "heritage area", "popular market street", "nearby nature spot"],
    )


def route_map_for(trip: TripInput, transport: str) -> list[dict]:
    if trip.start == trip.destination:
        return [
            {"label": "Start", "place": title_location(trip.start), "detail": "Begin from your selected local area."},
            {"label": "Explore", "place": title_location(trip.destination), "detail": "Use local transport for sightseeing."},
        ]

    return [
        {"label": "Start", "place": title_location(trip.start), "detail": "Reach the nearest railway station, bus stand, or airport."},
        {"label": "Intercity Travel", "place": transport, "detail": "Choose the budget-friendly option and book early."},
        {"label": "Arrive", "place": title_location(trip.destination), "detail": "Check in near attractions or public transport."},
        {"label": "Local Route", "place": "Stay -> attractions -> food area -> stay", "detail": "Cluster nearby places each day to reduce travel cost."},
    ]


def daily_itinerary(trip: TripInput, costs: CostPlan) -> str:
    places = attractions_for(trip.destination)
    food_per_day = round(costs.food / trip.days)
    local_per_day = round(costs.local_transport / trip.days)
    activity_per_day = round(costs.activities / trip.days)
    lines = []

    for day in range(1, trip.days + 1):
        first_place = places[(day - 1) % len(places)]
        second_place = places[day % len(places)]
        third_place = places[(day + 1) % len(places)]

        if day == 1:
            morning = "Travel to destination, check in, freshen up"
            afternoon = f"Light sightseeing around {first_place}"
            evening = f"Explore {second_place} and nearby food options"
        elif day == trip.days:
            morning = f"Visit {first_place} at an easy pace"
            afternoon = "Lunch, shopping, and return preparation"
            evening = "Start return journey or keep the evening relaxed if departing next morning"
        else:
            morning = f"Visit {first_place}"
            afternoon = f"Visit {second_place} with lunch break"
            evening = f"Relax around {third_place} or a nearby market/cafe"

        approx_daily = food_per_day + local_per_day + activity_per_day
        if day == 1 or day == trip.days:
            approx_daily += round(costs.intercity_transport / 2)

        lines.append(
            f"""Day {day}:
- Morning: {morning}
- Afternoon: {afternoon}
- Evening: {evening}
- Places to visit: {first_place}, {second_place}
- Activities: sightseeing, local food, relaxed exploration
- Estimated local transportation cost: Rs. {local_per_day:,}
- Estimated food cost: Rs. {food_per_day:,}
- Estimated activity/entry cost: Rs. {activity_per_day:,}
- Approximate daily cost: Rs. {approx_daily:,}
"""
        )

    return "\n".join(lines)


def build_plan(trip: TripInput) -> str:
    costs = estimate_costs(trip)
    budget_pppd = trip.budget / trip.people / trip.days
    style = travel_style(trip.specifications, budget_pppd)
    band = trip_distance_band(trip.start, trip.destination)
    transport, travel_time, one_way_transport = choose_transport(band, trip.specifications)
    rooms = math.ceil(trip.people / 2)
    nights = max(trip.days - 1, 0)
    hotel_per_room = nightly_hotel_cost(trip.specifications, budget_pppd)
    remaining = trip.budget - costs.total
    per_person = round(costs.total / trip.people)
    daily_food = round(costs.food / trip.days)
    local_daily = round(costs.local_transport / trip.days)

    budget_status = (
        f"Remaining Budget: Rs. {remaining:,}"
        if remaining >= 0
        else f"Amount Over Budget: Rs. {abs(remaining):,}"
    )

    optimization = "The estimated plan is within budget. Keep train/bus bookings early and avoid peak weekend hotel pricing."
    if remaining < 0:
        optimization = (
            "The requested trip is likely to exceed the budget.\n"
            "- Expensive components: intercity travel and accommodation.\n"
            "- Cheaper alternatives: choose sleeper/3AC trains, shared autos/metro, hostels, guesthouses, or homestays.\n"
            "- Reduce costs by travelling off-season, avoiding paid activities every day, and staying near the main attraction zone."
        )

    return f"""
## 1. Trip Overview
- Starting location: {title_location(trip.start)}
- Destination: {title_location(trip.destination)}
- Number of days: {trip.days}
- Number of people: {trip.people}
- Total budget: Rs. {trip.budget:,}
- Travel style based on specifications: {style}
- Assumption: Prices are practical estimates in INR for India and can vary by season, booking time, and exact location.

## 2. Transportation Plan
- Recommended transportation from starting location to destination: {transport}
- Estimated travel time: {travel_time}
- Estimated intercity transport cost: Rs. {costs.intercity_transport:,} total for {trip.people} people
- Local transportation facilities at destination: {", ".join(transport_facilities_for(trip.destination))}
- Estimated local transportation cost: Rs. {local_daily:,} per day for the group, Rs. {costs.local_transport:,} total

## 2A. Route Map
{chr(10).join(f"- {step['label']}: {step['place']} - {step['detail']}" for step in route_map_for(trip, transport))}

## 3. Accommodation Plan
- Recommended type of accommodation: budget hotel, guesthouse, hostel, or homestay based on comfort needs
- Preferred area/location to stay: central area near major attractions or public transport
- Estimated cost per night: Rs. {hotel_per_room:,} per room
- Rooms estimated: {rooms}
- Nights estimated: {nights}
- Total accommodation cost: Rs. {costs.accommodation:,}
- Reason for recommendation: staying central reduces local travel time and keeps the trip comfortable.

## 4. Day-by-Day Itinerary
{daily_itinerary(trip, costs)}
## 5. Food Plan
- Recommended food options: local restaurants, thalis, breakfast at stay, street food from busy and hygienic stalls, refill water where safe.
- Special food at {title_location(trip.destination)}: {", ".join(special_foods_for(trip.destination))}
- Estimated daily food budget: Rs. {daily_food:,} for the group.
- Based on specifications: {trip.specifications}

## 5A. Famous and Beautiful Locations
- Suggested beautiful places for travellers: {", ".join(beautiful_locations_for(trip.destination))}
- Famous tourist attractions: {", ".join(attractions_for(trip.destination))}

## 6. Budget Breakdown
Transportation: Rs. {costs.intercity_transport:,}
Accommodation: Rs. {costs.accommodation:,}
Food: Rs. {costs.food:,}
Activities: Rs. {costs.activities:,}
Local Travel: Rs. {costs.local_transport:,}
Miscellaneous: Rs. {costs.miscellaneous:,}
--------------------------------
Total Estimated Cost: Rs. {costs.total:,}
Approximate Per-Person Cost: Rs. {per_person:,}
{budget_status}

## 7. Budget Optimization
{optimization}

## 8. Important Travel Tips
- Best time considerations: avoid peak holiday weekends when possible; check local weather before booking.
- Local transportation tips: use public transport for predictable routes and app cabs only when needed.
- Important things to carry: government ID, medicines, reusable water bottle, power bank, comfortable shoes, weather-specific clothing.
- Safety considerations: keep valuables secure, avoid isolated late-night areas, and confirm hotel reviews before booking.
- Important local customs: dress modestly at religious places and ask before taking photos of people.
- Booking recommendations: book trains/flights and stays early, compare cancellation policies, and keep a small emergency buffer.

## 9. Final Recommendation
This trip is {"practical within the selected budget" if remaining >= 0 else "not fully practical within the selected budget"} based on the current estimates. The best strategy is to keep transport simple, stay centrally, choose local food, and limit paid activities to the most meaningful experiences.
""".strip()


def build_plan_payload(trip: TripInput) -> dict:
    costs = estimate_costs(trip)
    budget_pppd = trip.budget / trip.people / trip.days
    band = trip_distance_band(trip.start, trip.destination)
    transport, travel_time, _ = choose_transport(band, trip.specifications)
    remaining = trip.budget - costs.total

    return {
        "plan": build_plan(trip),
        "summary": {
            "start": title_location(trip.start),
            "destination": title_location(trip.destination),
            "days": trip.days,
            "people": trip.people,
            "budget": trip.budget,
            "travelStyle": travel_style(trip.specifications, budget_pppd),
            "transport": transport,
            "travelTime": travel_time,
            "estimatedTotal": costs.total,
            "perPerson": round(costs.total / trip.people),
            "remaining": remaining,
            "isWithinBudget": remaining >= 0,
        },
        "routeMap": route_map_for(trip, transport),
        "transportFacilities": transport_facilities_for(trip.destination),
        "specialFoods": special_foods_for(trip.destination),
        "beautifulLocations": beautiful_locations_for(trip.destination),
        "famousAttractions": attractions_for(trip.destination),
        "costs": {
            "transportation": costs.intercity_transport,
            "accommodation": costs.accommodation,
            "food": costs.food,
            "activities": costs.activities,
            "localTravel": costs.local_transport,
            "miscellaneous": costs.miscellaneous,
        },
    }


def main() -> None:
    trip = ask_trip_details()
    print("\n" + build_plan(trip))


if __name__ == "__main__":
    main()
