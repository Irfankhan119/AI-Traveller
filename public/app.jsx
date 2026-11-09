const DEFAULT_LOCATIONS = [
  "Delhi", "Jaipur", "Goa", "Mumbai", "Manali", "Kochi", "Varanasi",
  "Udaipur", "Agra", "Hyderabad", "Bengaluru", "Kolkata"
];

function formatInr(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value || 0);
}

function SectionedPlan({ text }) {
  if (!text) return null;

  return (
    <div className="plan-text">
      {text.split("\n").map((line, index) => {
        if (line.startsWith("## ")) return <h2 key={index}>{line.replace("## ", "")}</h2>;
        if (line.startsWith("- ")) return <p className="bullet" key={index}>{line.replace("- ", "")}</p>;
        if (line.startsWith("Day ")) return <h3 key={index}>{line}</h3>;
        if (!line.trim()) return <div className="space" key={index} />;
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

function AuthScreen({ onAuth }) {
  const [mode, setMode] = React.useState("login");
  const [form, setForm] = React.useState({ name: "", email: "", password: "" });
  const [message, setMessage] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submitAuth(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`/api/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Authentication failed.");
      onAuth(data.user);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell">
        <div className="auth-copy">
          <p className="eyebrow">India travel planner</p>
          <h1>AI Traveller</h1>
          <p className="lead">
            Sign in to create practical route maps, transport plans, food picks,
            scenic places, and budget-aware itineraries across India.
          </p>
          <div className="auth-highlights">
            <span>Route map</span>
            <span>Local food</span>
            <span>Budget check</span>
          </div>
        </div>

        <form className="auth-card" onSubmit={submitAuth}>
          <div className="tabs" role="tablist">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
            <button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
          </div>

          {mode === "register" && (
            <label>
              Full name
              <input name="name" value={form.name} onChange={updateField} minLength="2" required />
            </label>
          )}

          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={updateField} required />
          </label>

          <label>
            Password
            <input name="password" type="password" value={form.password} onChange={updateField} minLength="6" required />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
          </button>

          {message && <p className="error">{message}</p>}
          <p className="fineprint">Demo login stores users locally in this project folder.</p>
        </form>
      </section>
    </main>
  );
}

function RouteMap({ routeMap }) {
  if (!routeMap?.length) return null;

  return (
    <section className="feature-section">
      <h2>Route Map</h2>
      <div className="route-map">
        {routeMap.map((step, index) => (
          <div className="route-step" key={`${step.label}-${index}`}>
            <span>{index + 1}</span>
            <div>
              <strong>{step.label}: {step.place}</strong>
              <p>{step.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ChipList({ title, items }) {
  if (!items?.length) return null;

  return (
    <section className="feature-section">
      <h2>{title}</h2>
      <div className="chips">
        {items.map((item) => <span key={item}>{item}</span>)}
      </div>
    </section>
  );
}

function PlannerApp({ user, onLogout }) {
  const [locations, setLocations] = React.useState(DEFAULT_LOCATIONS);
  const [form, setForm] = React.useState({
    start: "Delhi",
    destination: "Jaipur",
    days: 3,
    people: 2,
    budget: 15000,
    specifications: "Budget hotels, local food, historical places"
  });
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    fetch("/api/locations")
      .then((response) => response.json())
      .then((data) => setLocations(data.locations || DEFAULT_LOCATIONS))
      .catch(() => setLocations(DEFAULT_LOCATIONS));
  }, []);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submitPlan(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          days: Number(form.days),
          people: Number(form.people),
          budget: Number(form.budget)
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not create the travel plan.");
      setResult(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  const costEntries = result
    ? Object.entries(result.costs).map(([label, value]) => ({
        label: label.replace(/([A-Z])/g, " $1"),
        value
      }))
    : [];

  return (
    <main>
      <section className="shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">Welcome, {user.name}</p>
            <h1>AI Traveller</h1>
          </div>
          <button className="ghost-button" type="button" onClick={onLogout}>Logout</button>
        </header>

        <div className="intro">
          <div>
            <p className="lead">
              Create a realistic India trip with route map, transport facilities,
              special food, famous locations, and budget checks.
            </p>
          </div>
          <div className="route-visual" aria-hidden="true">
            <span className="city-pin start"></span>
            <span className="city-pin middle"></span>
            <span className="city-pin end"></span>
            <span className="route-line one"></span>
            <span className="route-line two"></span>
          </div>
        </div>

        <div className="workspace">
          <form className="planner-panel" onSubmit={submitPlan}>
            <label>
              Starting location
              <select name="start" value={form.start} onChange={updateField}>
                {locations.map((location) => <option key={location} value={location}>{location}</option>)}
              </select>
            </label>

            <label>
              Destination
              <select name="destination" value={form.destination} onChange={updateField}>
                {locations.map((location) => <option key={location} value={location}>{location}</option>)}
              </select>
            </label>

            <div className="split">
              <label>
                Trip days
                <input name="days" type="number" min="1" value={form.days} onChange={updateField} />
              </label>
              <label>
                People
                <input name="people" type="number" min="1" value={form.people} onChange={updateField} />
              </label>
            </div>

            <label>
              Total budget in INR
              <input name="budget" type="number" min="1" step="500" value={form.budget} onChange={updateField} />
            </label>

            <label>
              Special specifications
              <textarea name="specifications" rows="4" value={form.specifications} onChange={updateField}></textarea>
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Planning..." : "Create travel plan"}
            </button>
            {error && <p className="error">{error}</p>}
          </form>

          <section className="results-panel">
            {!result && (
              <div className="empty-state">
                <h2>Plan preview</h2>
                <p>Select trip details to generate the route, facilities, food, places, and budget plan.</p>
              </div>
            )}

            {result && (
              <>
                <div className={result.summary.isWithinBudget ? "status good" : "status warning"}>
                  <span>{result.summary.isWithinBudget ? "Within budget" : "Over budget"}</span>
                  <strong>{formatInr(result.summary.estimatedTotal)}</strong>
                  <small>Estimated total for {result.summary.people} people</small>
                </div>

                <div className="metrics">
                  <div>
                    <span>Per person</span>
                    <strong>{formatInr(result.summary.perPerson)}</strong>
                  </div>
                  <div>
                    <span>{result.summary.remaining >= 0 ? "Remaining" : "Over by"}</span>
                    <strong>{formatInr(Math.abs(result.summary.remaining))}</strong>
                  </div>
                  <div>
                    <span>Travel time</span>
                    <strong>{result.summary.travelTime}</strong>
                  </div>
                </div>

                <RouteMap routeMap={result.routeMap} />
                <ChipList title="Transportation Facilities" items={result.transportFacilities} />
                <ChipList title="Special Food At Location" items={result.specialFoods} />
                <ChipList title="Famous And Beautiful Locations" items={result.beautifulLocations} />
                <ChipList title="Popular Tourist Attractions" items={result.famousAttractions} />

                <div className="cost-grid">
                  {costEntries.map((entry) => (
                    <div className="cost-card" key={entry.label}>
                      <span>{entry.label}</span>
                      <strong>{formatInr(entry.value)}</strong>
                    </div>
                  ))}
                </div>

                <SectionedPlan text={result.plan} />
              </>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}

function App() {
  const savedUser = JSON.parse(localStorage.getItem("aiTravellerUser") || "null");
  const [user, setUser] = React.useState(savedUser);

  function handleAuth(nextUser) {
    localStorage.setItem("aiTravellerUser", JSON.stringify(nextUser));
    setUser(nextUser);
  }

  function handleLogout() {
    localStorage.removeItem("aiTravellerUser");
    setUser(null);
  }

  if (!user) return <AuthScreen onAuth={handleAuth} />;
  return <PlannerApp user={user} onLogout={handleLogout} />;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
