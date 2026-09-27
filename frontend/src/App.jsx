import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "https://grainflow-farmer-access.onrender.com/api/message";
const CORE_API_URL = "https://smart-procurement-platform-1.onrender.com";
const AI_API_URL = "https://grainflow-ai-api.onrender.com";
const AUTH_API_URL = "https://smart-procurement-platform-1.onrender.com";
const API_TIMEOUT_MS = 20000;
const getTodayDate = () => {
  const today = new Date();
  const offset = today.getTimezoneOffset();
  return new Date(today.getTime() - offset * 60000)
    .toISOString()
    .split("T")[0];
};

function App() {
  const [page, setPage] = useState("home");
  const [farmer, setFarmer] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [sessionId] = useState(
    () => `web_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  );
  const [dashboardData, setDashboardData] = useState(null);
  const [centreData, setCentreData] = useState([]);
  const [alertsData, setAlertsData] = useState([]);
  const [bookingData, setBookingData] = useState([]);

  useEffect(() => {
    if (page !== "dashboard") return;

    const loadDashboardData = async () => {
      try {
        const [summaryResponse, centresResponse, alertsResponse, bookingResponse] =
          await Promise.all([
            fetch(`${CORE_API_URL}/dashboard/summary`),
            fetch(`${CORE_API_URL}/dashboard/centres`),
            fetch(`${CORE_API_URL}/dashboard/alerts`),
            fetch(`${CORE_API_URL}/booking/`),
          ]);

        if (!summaryResponse.ok) {
          throw new Error("Dashboard summary request failed.");
        }
        if (!centresResponse.ok) {
          throw new Error("Dashboard centres request failed.");
        }
        if (!alertsResponse.ok) {
          throw new Error("Dashboard alerts request failed.");
        }
        if (!bookingResponse.ok) {
          throw new Error("Booking data request failed.");
        }

        setDashboardData(await summaryResponse.json());
        setCentreData(await centresResponse.json());
        setAlertsData(await alertsResponse.json());
        setBookingData(await bookingResponse.json());
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    loadDashboardData();
  }, [page]);

  const goTo = (target) => {
    setPage(target);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="app">
      <Header goTo={goTo} activePage={page} />
      {page === "home" && <HomePage goTo={goTo} sessionId={sessionId} />}
      {page === "login" && (
        <LoginPage
          onLogin={(data) => {
            setAccessToken(data.access_token);
            setFarmer(data.farmer);
            setPage("home");
          }}
        />
      )}

      {page === "sell" && (
        <SellPage goTo={goTo} sessionId={sessionId} />
      )}
      {page === "buy" && (
        <BuyPage goTo={goTo} sessionId={sessionId} />
      )}
      {page === "track" && (
        <TrackPage goTo={goTo} sessionId={sessionId} />
      )}
      {page === "booking" && <BookSlotPage />}
      {page === "voice" && (
        <VoicePage goTo={goTo} sessionId={sessionId} />
      )}
      {page === "sms" && (
        <SmsPage goTo={goTo} sessionId={sessionId} />
      )}
      {page === "assisted" && (
        <AssistedPage goTo={goTo} sessionId={sessionId} />
      )}
      {page === "dashboard" && (
        <DashboardPage
          dashboardData={dashboardData}
          centreData={centreData}
          alertsData={alertsData}
          bookingData={bookingData}
        />
      )}

      <Footer />
    </div>
  );
}

/* ============================================================
   API
============================================================ */

async function sendMessage(message, sessionId) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  let response;
  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The request took too long. Please try again.", {
        cause: error,
      });
    }
    throw new Error("GrainFlow can't reach the server right now.", {
      cause: error,
    });
  } finally {
    window.clearTimeout(timeoutId);
  }

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("GrainFlow API returned an invalid response.");
  }

  if (!response.ok) {
    throw new Error(data?.message || "GrainFlow could not process your request.");
  }

  return data;
}

/* ============================================================
   HEADER
============================================================ */

function Header({ goTo, activePage }) {
  return (
    <>
      <header className="navbar">
        <button
          className="logo-button"
          onClick={() => goTo("home")}
        >
          <span className="logo-mark">G</span>

          <div className="logo-text">
            <strong>GrainFlow</strong>
            <small>SMART PROCUREMENT</small>
          </div>
        </button>

        <nav className="top-nav">
          <button
            className={activePage === "home" ? "nav-active" : ""}
            onClick={() => goTo("home")}
          >
            Home
          </button>

          <button
            className={activePage === "sell" ? "nav-active" : ""}
            onClick={() => goTo("sell")}
          >
            Sell
          </button>

          <button
            className={activePage === "buy" ? "nav-active" : ""}
            onClick={() => goTo("buy")}
          >
            Buy
          </button>
        </nav>
      </header>

      {activePage === "home" && (
        <nav className="side-nav">
          <button
            className={activePage === "track" ? "nav-active" : ""}
            onClick={() => goTo("track")}
          >
            <span>Track</span>
            <span>›</span>
          </button>

          <button
            className={activePage === "booking" ? "nav-active" : ""}
            onClick={() => goTo("booking")}
          >
            <span>Book Slot</span>
            <span>›</span>
          </button>

          <button
            className={activePage === "voice" ? "nav-active" : ""}
            onClick={() => goTo("voice")}
          >
            <span>Voice</span>
            <span>›</span>
          </button>

          <button
            className={activePage === "sms" ? "nav-active" : ""}
            onClick={() => goTo("sms")}
          >
            <span>SMS</span>
            <span>›</span>
          </button>

          <button
            className={activePage === "assisted" ? "nav-active" : ""}
            onClick={() => goTo("assisted")}
          >
            <span>Assisted</span>
            <span>›</span>
          </button>

          <button
            className={activePage === "dashboard" ? "nav-active" : ""}
            onClick={() => goTo("dashboard")}
          >
            <span>Dashboard</span>
            <span>›</span>
          </button>
        </nav>
      )}
    </>
  );
}
/* ============================================================
   HOME
============================================================ */

function HomePage({ goTo }) {
  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            SMART AGRICULTURAL PROCUREMENT
          </div>

          <h1>
            From your <span>field</span>
            <br />
            to the right opportunity.
          </h1>

          <p className="hero-description">
            GrainFlow helps farmers and buyers connect, manage procurement
            requests and track their progress.
          </p>
          <div className="farmer-login-note">
            <span>🔐</span>
            <button onClick={() => goTo("login")}>
              Farmer Login
            </button>
          </div>
          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={() => goTo("sell")}
            >
              Sell your produce
              <span>→</span>
            </button>

            <button
              className="secondary-button"
              onClick={() => goTo("buy")}
            >
              Find produce
              <span>↗</span>
            </button>
          </div>

          <div className="hero-note">
            <span>✓</span>
            Simple. Accessible. Farmer-focused.
          </div>

          <div className="hero-proof">
            <div>
              <strong>01</strong>
              <span>One request ID</span>
            </div>
            <div>
              <strong>06</strong>
              <span>Ways to access</span>
            </div>
            <div>
              <strong>24/7</strong>
              <span>Clear next steps</span>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="field-decoration field-one" />
          <div className="field-decoration field-two" />
          <div className="field-decoration field-three" />

          <div className="hero-panel">
            <div className="panel-top">
              <span>GRAINFLOW</span>
              <span className="live-status">
                <i />
                LIVE
              </span>
            </div>

            <div className="crop-symbol">🌾</div>

            <h2>
              Better access.
              <br />
              Better procurement.
            </h2>

            <p>
              One platform for selling, buying and tracking agricultural
              requests.
            </p>

            <div className="panel-bottom">
              <span>FARMER</span>
              <span>BUYER</span>
              <span>PROCUREMENT</span>
            </div>
          </div>
        </div>
      </section>

      <section className="intro-strip">
        <div>
          <span>BUILT FOR THE FIELD</span>
          <strong>
            Choose what you need.
            <br />
            GrainFlow handles the rest.
          </strong>
        </div>

        <p>
          Create a request in seconds, receive a request ID and track its
          progress without navigating complicated systems.
        </p>
      </section>

      <section className="quick-section">
        <div className="section-heading">
          <span>START HERE</span>
          <h2>What do you want to do?</h2>
          <p>Choose an action and continue from there.</p>
        </div>

        <div className="quick-grid">
          <ActionCard
            number="01"
            icon="↗"
            title="Sell Produce"
            description="Tell GrainFlow what you have available and create a procurement request."
            action="Start selling"
            className="sell-card"
            onClick={() => goTo("sell")}
          />

          <ActionCard
            number="02"
            icon="⌁"
            title="Buy Produce"
            description="Create a requirement for agricultural produce you need to source."
            action="Start buying"
            className="buy-card"
            onClick={() => goTo("buy")}
          />

          <ActionCard
            number="03"
            icon="✓"
            title="Track Request"
            description="Use your request ID to see the latest status of your procurement journey."
            action="Track request"
            className="track-card"
            onClick={() => goTo("track")}
          />

          <ActionCard
            number="04"
            icon="◉"
            title="Voice Assistant"
            description="Speak naturally to GrainFlow when typing is inconvenient."
            action="Talk to GrainFlow"
            className="voice-card"
            onClick={() => goTo("voice")}
          />

          <ActionCard
            number="05"
            icon="✉"
            title="SMS Access"
            description="Send a short farmer message and use the same GrainFlow request processing flow."
            action="Send a message"
            className="sms-card"
            onClick={() => goTo("sms")}
          />

          <ActionCard
            number="06"
            icon="◎"
            title="Assisted Access"
            description="Follow simple guided steps when you would like help creating or tracking a request."
            action="Get guided help"
            className="assisted-card"
            onClick={() => goTo("assisted")}
          />
        </div>
      </section>

      <section className="value-section">
        <div className="value-intro">
          <span>WHY GRAINFLOW</span>
          <h2>Procurement that works the way you do.</h2>
          <p>
            Built for India&apos;s farmers, buyers and field teams — with clear
            language, flexible access and a reliable request trail.
          </p>
        </div>

        <div className="value-grid">
          <article className="value-card">
            <span className="value-icon">↔</span>
            <div>
              <h3>One connected flow</h3>
              <p>Sell, source and follow every request from one simple place.</p>
            </div>
          </article>
          <article className="value-card">
            <span className="value-icon">◌</span>
            <div>
              <h3>Made for access</h3>
              <p>Use forms, voice, SMS or assisted steps — your choice.</p>
            </div>
          </article>
          <article className="value-card">
            <span className="value-icon">✓</span>
            <div>
              <h3>Always know what&apos;s next</h3>
              <p>Get a request ID and a clear status at every stage.</p>
            </div>
          </article>
        </div>
      </section>

      <section className="journey-section">
        <div className="journey-heading">
          <span>THE JOURNEY</span>
          <h2>From request to completion.</h2>
        </div>

        <div className="journey-grid">
          <JourneyItem
            number="01"
            title="Create"
            text="Submit a sell or buy request."
          />

          <JourneyItem
            number="02"
            title="Review"
            text="Your request enters the procurement flow."
          />

          <JourneyItem
            number="03"
            title="Match"
            text="The requirement can be connected with an opportunity."
          />

          <JourneyItem
            number="04"
            title="Complete"
            text="Track the request until the process is complete."
          />
        </div>
      </section>
    </main>
  );
}

function ActionCard({
  number,
  icon,
  title,
  description,
  action,
  className,
  onClick,
}) {
  return (
    <button className={`action-card ${className}`} onClick={onClick}>
      <div className="action-card-top">
        <span>{number}</span>
        <b>{icon}</b>
      </div>

      <h3>{title}</h3>

      <p>{description}</p>

      <strong>{action} →</strong>
    </button>
  );
}

function JourneyItem({ number, title, text }) {
  return (
    <div className="journey-item">
      <span>{number}</span>
      <div>
        <h3>{title}</h3>
        <p>{text}</p>
      </div>
    </div>
  );
}

/* ============================================================
   SELL
============================================================ */

function SellPage({ goTo, sessionId }) {
  const [form, setForm] = useState({
    name: "",
    product: "",
    quantity: "",
    location: "",
    kisan_id: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [rescheduleId, setRescheduleId] = useState("");
  const [newBookingDate, setNewBookingDate] = useState("");
  const [rescheduleMessage, setRescheduleMessage] = useState("");

  const submitSell = async (event) => {
    event.preventDefault();

    setError("");
    setResult(null);

    if (!form.name.trim()) {
      setError("Please enter your name.");
      return;
    }

    if (!form.product.trim()) {
      setError("Please enter the produce you want to sell.");
      return;
    }

    const quantity = Number(form.quantity);
    if (!form.quantity.trim() || !Number.isFinite(quantity) || quantity <= 0) {
      setError("Please enter a quantity greater than zero.");
      return;
    }

    if (!form.location.trim()) {
      setError("Please enter your location.");
      return;
    }

    setLoading(true);

    try {
      const message = `I want to sell ${quantity} kg of ${form.product} from ${form.location} my name is ${form.name} my Kisan ID is ${form.kisan_id}`;
      const data = await sendMessage(message, sessionId);

      if (data.success) {
        const procurementResponse = await fetch(`${CORE_API_URL}/procurements/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            procurement_id: `PROC${Date.now()}`,
            farmer_id: form.name,
            crop_name: form.product,
            quantity_kg: quantity,
            quality_grade: "A",
            price_per_kg: 0,
            centre_id: "CENTRE001",
          }),
        });

        if (!procurementResponse.ok) {
          const procurementError = await procurementResponse.json().catch(() => ({}));
          throw new Error(
            procurementError?.detail || "Procurement record could not be created."
          );
        }
      }

      if (!data.success && data.message) {
        setError(data.message);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page sell-page">
      <PageBack onClick={() => goTo("home")} />

      <PageHeader
        eyebrow="GRAINFLOW / SELL"
        title="Sell your produce"
        description="Tell us what you have, how much you want to sell and where it is available."
      />

      <form className="form-card" onSubmit={submitSell}>
        <div className="form-card-header">
          <div>
            <span>NEW SELL REQUEST</span>
            <h2>Produce details</h2>
          </div>

          <span className="form-badge">FARMER</span>
        </div>

        <div className="form-grid">
          <FormInput
            id="sell-name"
            label="Farmer name"
            placeholder="Enter your name"
            value={form.name}
            onChange={(value) =>
              setForm({ ...form, name: value })
            }
          />

          <FormInput
            id="sell-product"
            label="Produce"
            placeholder="e.g. Tomatoes, Green Chillies"
            value={form.product}
            onChange={(value) =>
              setForm({ ...form, product: value })
            }
          />

          <FormInput
            id="sell-quantity"
            label="Quantity"
            placeholder="e.g. 50"
            value={form.quantity}
            onChange={(value) =>
              setForm({ ...form, quantity: value })
            }
            suffix="kg"
            type="number"
          />

          <FormInput
            id="sell-location"
            label="Location"
            placeholder="Village / City"
            value={form.location}
            onChange={(value) =>
              setForm({ ...form, location: value })
            }
          />
          <input
            className="sell-kisan-input"
            type="text"
            placeholder="Kisan ID"
            value={form.kisan_id}
            onChange={(e) =>
              setForm({ ...form, kisan_id: e.target.value })
            }
          />
        </div>

        {error && <ErrorBox message={error} />}

        <button className="primary-button full-button" disabled={loading}>
          {loading ? "Creating request..." : "Create Sell Request →"}
        </button>
      </form>

      {result && <RequestResult result={result} />}
    </main>
  );
}

/* ============================================================
   BUY
============================================================ */

function BuyPage({ goTo, sessionId }) {
  const [form, setForm] = useState({
    name: "",
    product: "",
    quantity: "",
    location: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submitBuy = async (event) => {
    event.preventDefault();

    setError("");
    setResult(null);

    if (!form.name.trim()) {
      setError("Please enter your name.");
      return;
    }

    if (!form.product.trim()) {
      setError("Please enter the produce you need.");
      return;
    }

    const quantity = Number(form.quantity);
    if (!form.quantity.trim() || !Number.isFinite(quantity) || quantity <= 0) {
      setError("Please enter a quantity greater than zero.");
      return;
    }

    if (!form.location.trim()) {
      setError("Please enter the delivery location.");
      return;
    }

    setLoading(true);

    try {
      const message = `I want to buy ${quantity} kg of ${form.product} from ${form.location} my name is ${form.name}`;

      const data = await sendMessage(message, sessionId);

      await fetch(`${CORE_API_URL}/procurements/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          procurement_id: `PROC${Date.now()}`,
          farmer_id: form.name,
          crop_name: form.product,
          quantity_kg: quantity,
          quality_grade: "A",
          price_per_kg: 0,
          centre_id: "CENTRE001",
        }),
      });
      if (!data.success && data.message) {
        setError(data.message);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page buy-page">
      <PageBack onClick={() => goTo("home")} />

      <PageHeader
        eyebrow="GRAINFLOW / BUY"
        title="Find agricultural produce"
        description="Create a requirement and let GrainFlow process your procurement request."
      />

      <form className="form-card" onSubmit={submitBuy}>
        <div className="form-card-header">
          <div>
            <span>NEW BUY REQUEST</span>
            <h2>Requirement details</h2>
          </div>

          <span className="form-badge buyer-badge">BUYER</span>
        </div>

        <div className="form-grid">
          <FormInput
            id="buy-name"
            label="Buyer name"
            placeholder="Enter your name"
            value={form.name}
            onChange={(value) =>
              setForm({ ...form, name: value })
            }
          />

          <FormInput
            id="buy-product"
            label="Produce required"
            placeholder="e.g. Tomatoes, Rice"
            value={form.product}
            onChange={(value) =>
              setForm({ ...form, product: value })
            }
          />

          <FormInput
            id="buy-quantity"
            label="Quantity"
            placeholder="e.g. 100"
            value={form.quantity}
            onChange={(value) =>
              setForm({ ...form, quantity: value })
            }
            suffix="kg"
            type="number"
          />

          <FormInput
            id="buy-location"
            label="Location"
            placeholder="Delivery location"
            value={form.location}
            onChange={(value) =>
              setForm({ ...form, location: value })
            }
          />
        </div>

        {error && <ErrorBox message={error} />}

        <button className="primary-button full-button" disabled={loading}>
          {loading ? "Creating request..." : "Create Buy Request →"}
        </button>
      </form>

      {result && <RequestResult result={result} />}
    </main>
  );
}

/* ============================================================
   SMS ACCESS
============================================================ */

function SmsPage({ goTo, sessionId }) {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submitSms = async (event) => {
    event.preventDefault();
    const trimmedMessage = message.trim();
    setError("");
    setResult(null);

    if (!trimmedMessage) {
      setError("Please enter a farmer message.");
      return;
    }

    setLoading(true);
    try {
      const data = await sendMessage(trimmedMessage, `${sessionId}_sms`);
      if (!data.success) {
        setError(data.message || "GrainFlow could not process that message.");
      } else {
        setResult(data);
        setMessage("");
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <PageBack onClick={() => goTo("home")} />
      <PageHeader
        eyebrow="GRAINFLOW / SMS ACCESS"
        title="Send a farmer message"
        description="Type the message a farmer would send by SMS. GrainFlow will process it using the same procurement assistant."
      />

      <form className="form-card access-form-card" onSubmit={submitSms}>
        <div className="form-card-header">
          <div>
            <span>SMS-STYLE MESSAGE</span>
            <h2>What would you like GrainFlow to know?</h2>
          </div>
          <span className="form-badge">TEXT</span>
        </div>

        <div className="form-field">
          <label htmlFor="sms-message">Farmer message</label>
          <textarea
            id="sms-message"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Example: I want to sell 50 kg tomatoes from Bhimavaram my name is Poorna"
            rows="5"
          />
        </div>

        <p className="form-hint">
          You can ask to sell, buy, or check a request status.
        </p>
        {error && <ErrorBox message={error} />}
        <button className="primary-button full-button" disabled={loading}>
          {loading ? "Processing message..." : "Send to GrainFlow →"}
        </button>
      </form>

      {result && <AccessResult result={result} />}
    </main>
  );
}

/* ============================================================
   ASSISTED ACCESS
============================================================ */

function AssistedPage({ goTo, sessionId }) {
  const [mode, setMode] = useState("");
  const [form, setForm] = useState({
    name: "",
    product: "",
    quantity: "",
    location: "",
    requestId: "",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const updateField = (field, value) => {
    setForm((previous) => ({ ...previous, [field]: value }));
  };

  const submitAssisted = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!mode) {
      setError("Please choose what you need help with.");
      return;
    }

    let message;
    if (mode === "track") {
      const requestId = form.requestId.trim().toUpperCase();
      if (!/^REQ\d+$/.test(requestId)) {
        setError("Please enter a valid request ID, for example REQ001.");
        return;
      }
      message = `status ${requestId}`;
    } else {
      const quantity = Number(form.quantity);
      if (!form.name.trim() || !form.product.trim() || !form.location.trim()) {
        setError("Please complete every field before continuing.");
        return;
      }
      if (!form.quantity.trim() || !Number.isFinite(quantity) || quantity <= 0) {
        setError("Please enter a quantity greater than zero.");
        return;
      }
      message = `I want to ${mode} ${quantity} kg of ${form.product} from ${form.location} my name is ${form.name}`;
    }

    setLoading(true);
    try {
      const data = await sendMessage(message, `${sessionId}_assisted`);
      if (!data.success) {
        setError(data.message || "GrainFlow could not process your request.");
      } else {
        setResult(data);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <PageBack onClick={() => goTo("home")} />
      <PageHeader
        eyebrow="GRAINFLOW / ASSISTED ACCESS"
        title="Let us guide you"
        description="Choose one simple task and complete only the details needed for your request."
      />

      <section className="assisted-access-panel">
        <div className="assisted-steps">
          <span className={mode ? "step-done" : "step-current"}>1. Choose a task</span>
          <span className={mode ? "step-current" : ""}>2. Add details</span>
          <span>3. Submit</span>
        </div>

        <div className="assisted-options" role="group" aria-label="Choose an assisted task">
          {[
            ["sell", "Sell produce", "I have produce to offer"],
            ["buy", "Buy produce", "I need to source produce"],
            ["track", "Track a request", "I already have a request ID"],
          ].map(([value, title, description]) => (
            <button
              className={`assisted-option ${mode === value ? "selected" : ""}`}
              key={value}
              type="button"
              onClick={() => {
                setMode(value);
                setError("");
                setResult(null);
              }}
              aria-pressed={mode === value}
            >
              <strong>{title}</strong>
              <span>{description}</span>
            </button>
          ))}
        </div>

        {mode && (
          <form className="assisted-form" onSubmit={submitAssisted}>
            {mode === "track" ? (
              <FormInput
                id="assisted-request-id"
                label="Request ID"
                placeholder="Example: REQ001"
                value={form.requestId}
                onChange={(value) => updateField("requestId", value)}
              />
            ) : (
              <div className="form-grid">
                <FormInput
                  id="assisted-name"
                  label="Your name"
                  placeholder="Enter your name"
                  value={form.name}
                  onChange={(value) => updateField("name", value)}
                />
                <FormInput
                  id="assisted-product"
                  label="Produce"
                  placeholder="e.g. Tomatoes or Rice"
                  value={form.product}
                  onChange={(value) => updateField("product", value)}
                />
                <FormInput
                  id="assisted-quantity"
                  label="Quantity"
                  placeholder="e.g. 50"
                  type="number"
                  suffix="kg"
                  value={form.quantity}
                  onChange={(value) => updateField("quantity", value)}
                />
                <FormInput
                  id="assisted-location"
                  label={mode === "buy" ? "Delivery location" : "Location"}
                  placeholder="Village / City"
                  value={form.location}
                  onChange={(value) => updateField("location", value)}
                />
              </div>
            )}

            {error && <ErrorBox message={error} />}
            <button className="primary-button full-button" disabled={loading}>
              {loading ? "Working..." : "Continue with GrainFlow →"}
            </button>
          </form>
        )}
      </section>

      {result && <AccessResult result={result} />}
    </main>
  );
}

function AccessResult({ result }) {
  return (
    <section className="access-result">
      <div className="success-icon">✓</div>
      <div>
        <span>GRAINFLOW RESPONSE</span>
        <h2>{result.message}</h2>
        {result.request && (
          <div className="access-result-details">
            <strong>{result.request.request_id}</strong>
            <StatusPill status={result.request.status} />
          </div>
        )}
      </div>
    </section>
  );
}

/* ============================================================
   TRACK
============================================================ */
function BookSlotPage() {
  const [rescheduleId, setRescheduleId] = useState("");
  const [newBookingDate, setNewBookingDate] = useState("");
  const [rescheduleMessage, setRescheduleMessage] = useState("");

  const [form, setForm] = useState({
    farmer_name: "",
    crop: "",
    quantity: "",
    booking_date: "",
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [aiRecommendation, setAiRecommendation] = useState(null);

  async function handleBooking(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!form.booking_date) {
      setError("Please select a booking date.");
      return;
    }

    if (form.booking_date < getTodayDate()) {
      setError("Booking date cannot be in the past.");
      return;
    }

    try {
      const response = await fetch(`${CORE_API_URL}/booking/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          farmer_name: form.farmer_name,
          crop: form.crop,
          quantity: Number(form.quantity),
          booking_date: form.booking_date,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Booking failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function getAIRecommendation() {
    setError("");
    setAiRecommendation(null);

    try {
      const response = await fetch(
        `${AI_API_URL}/predict/smart-slot`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "AI recommendation failed."
        );
      }

      setAiRecommendation(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleReschedule(e) {
    e.preventDefault();
    setRescheduleMessage("");
    setError("");
    if (!newBookingDate) {
      setError("Please select a new booking date.");
      return;
    }

    if (newBookingDate < getTodayDate()) {
      setError("Reschedule date cannot be in the past.");
      return;
    }

    try {
      const response = await fetch(
        `${CORE_API_URL}/booking/reschedule`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            booking_id: Number(rescheduleId),
            new_booking_date: newBookingDate,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Rescheduling failed."
        );
      }

      if (data.message) {
        setRescheduleMessage(data.message);
      } else {
        setRescheduleMessage(
          "Booking rescheduled successfully."
        );
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function viewAlternativeSlots() {
    setError("");

    try {
      const response = await fetch(
        `${CORE_API_URL}/booking/alternatives?requested_date=2026-09-17`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Failed to load alternative slots."
        );
      }

      alert(JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="page booking-page">

      {/* PAGE HEADER */}
      <section className="booking-page-header">
        <div>
          <span className="section-eyebrow">GRAINFLOW / BOOKING</span>
          <h1>Book your procurement slot</h1>
          <p>
            Choose a convenient date and reserve your place at the
            procurement centre.
          </p>
        </div>

        <div className="booking-header-badge">
          <span className="booking-badge-dot"></span>
          Slot Booking
        </div>
      </section>

      {/* BOOK NEW SLOT */}
      <section className="booking-main-card">

        <div className="booking-card-header">
          <div>
            <span className="section-eyebrow">NEW BOOKING</span>
            <h2>Reserve a procurement slot</h2>
            <p>
              Enter your details and select your preferred procurement date.
            </p>
          </div>

          <div className="booking-card-icon">
            +
          </div>
        </div>

        <form
          className="booking-form"
          onSubmit={handleBooking}
        >

          <div className="booking-form-grid">

            {/* FARMER NAME */}
            <div className="booking-field">
              <label htmlFor="booking-farmer-name">
                Farmer name
              </label>

              <input
                id="booking-farmer-name"
                type="text"
                placeholder="Enter farmer name"
                value={form.farmer_name}
                onChange={(e) =>
                  setForm({
                    ...form,
                    farmer_name: e.target.value,
                  })
                }
                required
              />
            </div>

            {/* CROP */}
            <div className="booking-field">
              <label htmlFor="booking-crop">
                Crop
              </label>

              <input
                id="booking-crop"
                type="text"
                placeholder="e.g. Rice, Wheat, Maize"
                value={form.crop}
                onChange={(e) =>
                  setForm({
                    ...form,
                    crop: e.target.value,
                  })
                }
                required
              />
            </div>

            {/* QUANTITY */}
            <div className="booking-field">
              <label htmlFor="booking-quantity">
                Quantity
              </label>

              <div className="booking-input-with-suffix">
                <input
                  id="booking-quantity"
                  type="number"
                  placeholder="Enter quantity"
                  value={form.quantity}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      quantity: e.target.value,
                    })
                  }
                  min="1"
                  required
                />

                <span>kg</span>
              </div>
            </div>

            {/* DATE */}
            <div className="booking-field">
              <label htmlFor="booking-date">
                Preferred date
              </label>

              <input
                id="booking-date"
                type="date"
                min={getTodayDate()}
                value={form.booking_date}
                onChange={(e) =>
                  setForm({
                    ...form,
                    booking_date: e.target.value,
                  })
                }
                required
              />
            </div>

          </div>

          <div className="booking-form-footer">
            <span>
              Select today or a future date for your procurement visit.
            </span>

            <button
              className="booking-primary-button"
              type="submit"
            >
              Book Procurement Slot
              <span>→</span>
            </button>
          </div>

        </form>

        {/* ERROR */}
        {error && (
          <div className="booking-error">
            <span className="booking-message-icon">!</span>
            <div>
              <strong>Something went wrong</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

      </section>


      {/* BOOKING RESULT */}
      {result && (
        <section className="booking-success-card">

          <div className="booking-success-icon">
            ✓
          </div>

          <div className="booking-success-content">

            <span className="section-eyebrow">
              BOOKING CONFIRMED
            </span>

            <h2>Your procurement slot is reserved</h2>

            <p>
              Keep your confirmation token for future reference.
            </p>

            <div className="booking-details-grid">

              <div className="booking-detail">
                <span>Booking ID</span>
                <strong>{result.booking_id}</strong>
              </div>

              <div className="booking-detail">
                <span>Confirmation Token</span>
                <strong>{result.confirmation_token}</strong>
              </div>

              <div className="booking-detail">
                <span>Farmer</span>
                <strong>{result.farmer_name}</strong>
              </div>

              <div className="booking-detail">
                <span>Crop</span>
                <strong>{result.crop}</strong>
              </div>

              <div className="booking-detail">
                <span>Quantity</span>
                <strong>{result.quantity} kg</strong>
              </div>

              <div className="booking-detail">
                <span>Date</span>
                <strong>{result.booking_date}</strong>
              </div>

              <div className="booking-detail booking-detail-status">
                <span>Status</span>
                <strong>{result.status}</strong>
              </div>

            </div>

          </div>
        </section>
      )}


      {/* LOWER ACTIONS */}
      <section className="booking-actions-grid">

        {/* RESCHEDULE */}
        <div className="booking-action-card">

          <div className="booking-action-icon">
            ↻
          </div>

          <span className="section-eyebrow">
            CHANGE YOUR DATE
          </span>

          <h2>Reschedule booking</h2>

          <p>
            Already have a booking? Change your procurement date
            without creating a new booking.
          </p>

          <form
            className="booking-secondary-form"
            onSubmit={handleReschedule}
          >

            <div className="booking-field">
              <label htmlFor="reschedule-id">
                Booking ID
              </label>

              <input
                id="reschedule-id"
                type="number"
                placeholder="Enter booking ID"
                value={rescheduleId}
                onChange={(e) =>
                  setRescheduleId(e.target.value)
                }
                min="1"
                required
              />
            </div>

            <div className="booking-field">
              <label htmlFor="reschedule-date">
                New date
              </label>

              <input
                id="reschedule-date"
                type="date"
                min={getTodayDate()}
                value={newBookingDate}
                onChange={(e) =>
                  setNewBookingDate(e.target.value)
                }
                required
              />
            </div>

            <button
              className="booking-secondary-button"
              type="submit"
            >
              Reschedule Booking
              <span>→</span>
            </button>

          </form>

          {rescheduleMessage && (
            <div className="booking-success-message">
              <span>✓</span>
              {rescheduleMessage}
            </div>
          )}

        </div>


        {/* ALTERNATIVE / AI */}
        <div className="booking-action-card booking-ai-card">

          <div className="booking-action-icon booking-ai-icon">
            AI
          </div>

          <span className="section-eyebrow">
            SMART SLOT ASSISTANCE
          </span>

          <h2>Find a better slot</h2>

          <p>
            Explore alternative procurement slots or let GrainFlow
            recommend a slot using AI predictions.
          </p>

          <div className="booking-ai-actions">

            <button
              className="booking-secondary-button"
              type="button"
              onClick={viewAlternativeSlots}
            >
              View Alternative Slots
              <span>→</span>
            </button>

            <button
              className="booking-ai-button"
              type="button"
              onClick={getAIRecommendation}
            >
              Get AI Recommended Slot
              <span>✦</span>
            </button>

          </div>

        </div>

      </section>


      {/* AI RECOMMENDATION */}
      {aiRecommendation && (
        <section className="ai-recommendation-card">

          <div className="ai-recommendation-header">

            <div>
              <span className="section-eyebrow">
                GRAINFLOW AI
              </span>

              <h2>Recommended procurement slot</h2>

              <p>
                Based on predicted arrivals, queue conditions and
                congestion.
              </p>
            </div>

            <div className="ai-score">
              <span>Slot Score</span>
              <strong>{aiRecommendation.slot_score}</strong>
            </div>

          </div>


          <div className="ai-recommendation-grid">

            <div className="ai-stat">
              <span>Recommended Slot</span>
              <strong>
                {aiRecommendation.recommended_slot}
              </strong>
            </div>

            <div className="ai-stat">
              <span>Predicted Arrivals</span>
              <strong>
                {aiRecommendation.predicted_arrivals}
              </strong>
            </div>

            <div className="ai-stat">
              <span>Predicted Queue</span>
              <strong>
                {aiRecommendation.predicted_queue}
              </strong>
            </div>

            <div className="ai-stat">
              <span>Waiting Time</span>
              <strong>
                {aiRecommendation.predicted_waiting_time} min
              </strong>
            </div>

            <div className="ai-stat">
              <span>Congestion</span>
              <strong>
                {aiRecommendation.congestion_level}
              </strong>
            </div>

            <div className="ai-stat">
              <span>Congestion Score</span>
              <strong>
                {aiRecommendation.congestion_score}
              </strong>
            </div>

          </div>

        </section>
      )}

    </main>
  );
}
function TrackPage({ goTo, sessionId }) {
  const [requestId, setRequestId] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const checkStatus = async (event) => {
    event.preventDefault();

    setError("");
    setResult(null);

    const cleanedId = requestId.trim().toUpperCase();

    if (!/^REQ\d+$/.test(cleanedId)) {
      setError("Please enter a valid request ID, for example REQ001.");
      return;
    }

    setLoading(true);

    try {
      const data = await sendMessage(
        `status ${cleanedId}`,
        `${sessionId}_track`
      );

      if (!data.success) {
        setError(data.message || "Request not found.");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const request = result?.request;

  return (
    <main className="page">
      <PageBack onClick={() => goTo("home")} />

      <PageHeader
        eyebrow="GRAINFLOW / TRACK"
        title="Track your request"
        description="Enter your GrainFlow request ID to see its current procurement status."
      />

      <form className="track-card-large" onSubmit={checkStatus}>
        <div className="track-label">
          <span>REQUEST ID</span>
          <small>Example: REQ015</small>
        </div>

        <div className="track-row">
          <input
            id="request-id"
            aria-label="Request ID"
            value={requestId}
            onChange={(event) => setRequestId(event.target.value)}
            placeholder="Enter request ID"
            autoComplete="off"
          />

          <button className="primary-button" disabled={loading}>
            {loading ? "Checking..." : "Check Status"}
          </button>
        </div>

        {error && <ErrorBox message={error} />}
      </form>

      {result && (
        <div className="tracking-result">
          <div className="result-top">
            <div>
              <span>REQUEST FOUND</span>
              <h2>
                {request?.request_id || requestId.toUpperCase()}
              </h2>
            </div>

            <StatusPill status={request?.status} />
          </div>

          {request ? (
            <>
              <div className="request-summary">
                <SummaryItem
                  label="Request type"
                  value={formatRequestType(request.request_type)}
                />

                <SummaryItem
                  label="Product"
                  value={request.grain_type}
                />

                <SummaryItem
                  label="Quantity"
                  value={`${request.quantity} kg`}
                />

                <SummaryItem
                  label="Location"
                  value={request.location}
                />
              </div>

              <StatusJourney status={request.status} />
            </>
          ) : (
            <p className="result-message">{result.message}</p>
          )}
        </div>
      )}
    </main>
  );
}

/* ============================================================
   VOICE
============================================================ */

function VoicePage({ goTo, sessionId }) {
  const [isListening, setIsListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [transcript, setTranscript] = useState("");
  const [messages, setMessages] = useState([]);
  const [processing, setProcessing] = useState(false);

  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript("");
    };

    recognition.onresult = (event) => {
      let text = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        text += event.results[i][0].transcript;
      }

      setTranscript(text);
    };

    recognition.onerror = (event) => {
      setIsListening(false);

      if (event.error === "not-allowed") {
        setTranscript(
          "Microphone permission was denied. Please allow microphone access."
        );
      } else {
        setTranscript(
          "I couldn't hear that clearly. Please try again."
        );
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
    };
  }, []);

  const speak = (text) => {
    if (!("speechSynthesis" in window)) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-IN";
    utterance.rate = 0.95;
    utterance.pitch = 1;

    window.speechSynthesis.speak(utterance);
  };

  const startListening = () => {
    if (!supported || !recognitionRef.current) return;

    setTranscript("");

    try {
      recognitionRef.current.start();
    } catch {
      // Browser may throw if recognition is already running.
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const sendVoiceMessage = async () => {
    const message = transcript.trim();

    if (!message || processing) return;

    setProcessing(true);

    setMessages((previous) => [
      ...previous,
      {
        type: "user",
        text: message,
      },
    ]);

    setTranscript("");

    try {
      const data = await sendMessage(message, sessionId);

      const responseText =
        data.message ||
        "Your request has been processed.";

      setMessages((previous) => [
        ...previous,
        {
          type: "assistant",
          text: responseText,
          data,
        },
      ]);

      speak(responseText);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          type: "assistant",
          text: error.message,
        },
      ]);

      speak(error.message);
    } finally {
      setProcessing(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setTranscript("");
    window.speechSynthesis?.cancel();
  };

  return (
    <main className="page voice-page">
      <PageBack onClick={() => goTo("home")} />

      <div className="voice-layout">
        <section className="voice-main-card">
          <div className="voice-eyebrow">
            <span className="voice-live-dot" />
            GRAINFLOW / VOICE
          </div>

          <h1>Talk to GrainFlow.</h1>

          <p>
            Speak naturally about selling, buying or tracking a request.
            GrainFlow will understand the request and guide you.
          </p>

          {!supported && (
            <div className="browser-warning">
              Your browser does not support speech recognition. Please use
              Google Chrome or another supported browser.
            </div>
          )}

          <div className={`voice-orb ${isListening ? "listening" : ""}`}>
            <div className="orb-ring ring-one" />
            <div className="orb-ring ring-two" />
            <div className="orb-core">
              {isListening ? "●" : "🎙"}
            </div>
          </div>

          <div className="voice-status">
            {isListening
              ? "Listening... speak now"
              : processing
                ? "GrainFlow is processing your request..."
                : "Press the microphone and speak"}
          </div>

          <button
            className={`voice-start-button ${isListening ? "voice-stop" : ""
              }`}
            onClick={isListening ? stopListening : startListening}
            disabled={!supported || processing}
            aria-label={isListening ? "Stop listening" : "Start voice assistant"}
          >
            <span>{isListening ? "■" : "●"}</span>
            {isListening ? "Stop listening" : "Start voice assistant"}
          </button>

          {transcript && (
            <div className="voice-transcript">
              <span>YOU SAID</span>
              <p>{transcript}</p>

              {!isListening && (
                <button
                  className="transcript-send"
                  onClick={sendVoiceMessage}
                  disabled={processing}
                >
                  {processing ? "Processing..." : "Send to GrainFlow →"}
                </button>
              )}
            </div>
          )}

          <div className="voice-examples">
            <span>TRY SAYING</span>

            <button
              onClick={() =>
                setTranscript(
                  "I want to sell 50 kg of tomatoes from Bhimavaram my name is Mithra"
                )
              }
            >
              “I want to sell 50 kg of tomatoes from Bhimavaram”
            </button>

            <button
              onClick={() =>
                setTranscript(
                  "I want to buy 100 kg of rice from Bhimavaram my name is Mithra"
                )
              }
            >
              “I want to buy 100 kg of rice”
            </button>

            <button
              onClick={() => setTranscript("status REQ015")}
            >
              “Check status REQ015”
            </button>
          </div>
        </section>

        <aside className="voice-side">
          <div className="voice-side-card">
            <span>VOICE FLOW</span>

            <div className="voice-step">
              <b>01</b>
              <div>
                <strong>Speak</strong>
                <p>Tell GrainFlow what you need.</p>
              </div>
            </div>

            <div className="voice-line" />

            <div className="voice-step">
              <b>02</b>
              <div>
                <strong>Understand</strong>
                <p>GrainFlow identifies your request.</p>
              </div>
            </div>

            <div className="voice-line" />

            <div className="voice-step">
              <b>03</b>
              <div>
                <strong>Process</strong>
                <p>Your request goes through the same backend engine.</p>
              </div>
            </div>
          </div>

          {messages.length > 0 && (
            <div className="voice-history">
              <div className="history-header">
                <span>CONVERSATION</span>

                <button onClick={clearConversation}>
                  Clear
                </button>
              </div>

              {messages.map((item, index) => (
                <div
                  key={index}
                  className={`chat-message ${item.type}`}
                >
                  <span>
                    {item.type === "user" ? "YOU" : "GRAINFLOW"}
                  </span>

                  <p>{item.text}</p>

                  {item.data?.request && (
                    <div className="mini-request">
                      <strong>
                        {item.data.request.request_id}
                      </strong>

                      <StatusPill
                        status={item.data.request.status}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}

/* ============================================================
   SHARED UI
============================================================ */

function PageBack({ onClick }) {
  return (
    <button className="back-button" onClick={onClick}>
      ← Back to Home
    </button>
  );
}

function PageHeader({ eyebrow, title, description }) {
  return (
    <div className="page-header">
      <span>{eyebrow}</span>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  );
}

function FormInput({
  label,
  id,
  placeholder,
  value,
  onChange,
  suffix,
  type = "text",
}) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>

      <div className="input-wrapper">
        <input
          id={id}
          type={type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
        />

        {suffix && <span>{suffix}</span>}
      </div>
    </div>
  );
}

function ErrorBox({ message }) {
  return (
    <div className="error-box">
      <span>!</span>
      <p>{message}</p>
    </div>
  );
}

function RequestResult({ result }) {
  const request = result?.request;

  return (
    <section className="success-card">
      <div className="success-icon">✓</div>

      <div className="success-content">
        <span>REQUEST CREATED</span>

        <h2>{result.message}</h2>

        {request && (
          <div className="created-details">
            <div>
              <span>REQUEST ID</span>
              <strong>{request.request_id}</strong>
            </div>

            <div>
              <span>PRODUCT</span>
              <strong>{request.grain_type}</strong>
            </div>

            <div>
              <span>QUANTITY</span>
              <strong>{request.quantity} kg</strong>
            </div>

            <div>
              <span>LOCATION</span>
              <strong>{request.location}</strong>
            </div>
          </div>
        )}

        {request && (
          <p className="save-note">
            Save your request ID. You can use it anytime from the Track page.
          </p>
        )}
      </div>
    </section>
  );
}

function SummaryItem({ label, value }) {
  return (
    <div className="summary-item">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function StatusPill({ status }) {
  if (!status) return null;

  const readable = status
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

  return (
    <span className={`status-pill status-${status.toLowerCase()}`}>
      {readable}
    </span>
  );
}

function StatusJourney({ status }) {
  const statuses = [
    "REQUEST_CREATED",
    "UNDER_REVIEW",
    "MATCHED",
    "NEGOTIATION",
    "COMPLETED",
  ];

  const currentIndex = statuses.indexOf(status);

  if (status === "CANCELLED" || status === "REJECTED") {
    return (
      <div className="status-journey terminal-journey">
        <div className="journey-title">
          <span>REQUEST JOURNEY</span>
          <h3>This request is {status.toLowerCase()}.</h3>
        </div>
        <p className="result-message">
          No further procurement steps are expected for this request.
        </p>
      </div>
    );
  }

  return (
    <div className="status-journey">
      <div className="journey-title">
        <span>REQUEST JOURNEY</span>
        <h3>Current progress</h3>
      </div>

      <div className="status-track">
        {statuses.map((item, index) => {
          const active =
            currentIndex >= 0 && index <= currentIndex;

          return (
            <div
              className={`status-track-item ${active ? "completed-step" : ""
                }`}
              key={item}
            >
              <div className="status-circle">
                {active ? "✓" : index + 1}
              </div>

              <span>
                {item
                  .replaceAll("_", " ")
                  .toLowerCase()
                  .replace(/\b\w/g, (letter) =>
                    letter.toUpperCase()
                  )}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatRequestType(type) {
  if (!type) return "—";

  return type
    .replace("_GRAIN", "")
    .replace("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/* ============================================================
   FOOTER
============================================================ */

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-brand">
        <span className="footer-mark">G</span>

        <div>
          <strong>GrainFlow</strong>
          <small>Smart Procurement Platform</small>
        </div>
      </div>

      <p>
        Connecting agricultural produce with opportunity.
      </p>

      <span className="footer-copy">
        © {new Date().getFullYear()} GrainFlow
      </span>
    </footer>
  );
}

function DashboardPage({
  dashboardData,
  centreData,
  alertsData,
  bookingData,
}) {
  const [dashboardSection, setDashboardSection] = useState("dashboard");

  const sections = [
    { id: "dashboard", label: "Dashboard", icon: "🏠" },
    { id: "appointments", label: "Appointments", icon: "📅" },
    { id: "queue", label: "Queue Management", icon: "🎟️" },
    { id: "procurement", label: "Procurement", icon: "🌾" },
    { id: "reports", label: "Reports", icon: "📊" },
    { id: "settings", label: "Settings", icon: "⚙️" },
  ];

  const getBookingStatus = (booking) =>
    String(booking?.status || "").replaceAll("_", " ");

  const processingBooking =
    bookingData.find((booking) =>
      ["PROCESSING", "IN_PROGRESS", "SERVING"].includes(
        String(booking?.status || "").toUpperCase()
      )
    ) || bookingData[0];

  const targetPercentage =
    dashboardData && Number(dashboardData.daily_target) > 0
      ? Math.round(
        (Number(dashboardData.procured || 0) /
          Number(dashboardData.daily_target)) *
        100
      )
      : 0;

  return (
    <div className="dashboard-page">
      {/* Dashboard Sidebar */}
      <aside className="sidebar">
        <div className="logo">🌾 GrainFlow</div>

        <nav>
          {sections.map((section) => (
            <div
              key={section.id}
              className={`nav-item ${dashboardSection === section.id ? "active" : ""
                }`}
              onClick={() => setDashboardSection(section.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  setDashboardSection(section.id);
                }
              }}
            >
              {section.icon} {section.label}
            </div>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        {/* ======================================================
            OVERVIEW / DASHBOARD
        ====================================================== */}
        {dashboardSection === "dashboard" && (
          <>
            <div className="header">
              <h1>Procurement Centre Dashboard</h1>
              <p>
                Monitor farmers, appointments and procurement activities
              </p>
            </div>

            <div className="stats">
              <div className="card">
                <h3>Today's Farmers</h3>
                <p>
                  {dashboardData ? dashboardData.todays_farmers : "..."}
                </p>
              </div>

              <div className="card">
                <h3>Upcoming Appointments</h3>
                <p>
                  {dashboardData
                    ? dashboardData.upcoming_appointments
                    : "..."}
                </p>
              </div>

              <div className="card">
                <h3>Current Queue</h3>
                <p>
                  {dashboardData ? dashboardData.current_queue : "..."}
                </p>
              </div>

              <div className="card">
                <h3>Average Waiting Time</h3>
                <p>
                  {dashboardData
                    ? `${dashboardData.average_waiting_time} min`
                    : "..."}
                </p>
              </div>
            </div>

            <div className="bottom-section">
              <div className="status-panel">
                <h2>🏢 Centre Status</h2>

                <div className="status-item">
                  <span>Queue Status</span>
                  <strong className="active-text">
                    {dashboardData ? "Active" : "..."}
                  </strong>
                </div>

                <div className="status-item">
                  <span>Available Counters</span>
                  <strong>—</strong>
                </div>

                <div className="status-item">
                  <span>Expected Arrivals</span>
                  <strong>
                    {dashboardData
                      ? dashboardData.expected_arrivals
                      : "..."}
                  </strong>
                </div>

                <div className="status-item">
                  <span>Congestion Level</span>
                  <strong className="medium-text">
                    {dashboardData
                      ? dashboardData.congestion_level
                      : "..."}
                  </strong>
                </div>
              </div>

              <div className="progress-panel">
                <h2>🌾 Procurement Progress</h2>

                <div className="progress-info">
                  <span>Daily Target</span>
                  <strong>
                    {dashboardData
                      ? `${dashboardData.daily_target} Quintals`
                      : "..."}
                  </strong>
                </div>

                <div className="progress-info">
                  <span>Procured</span>
                  <strong>
                    {dashboardData
                      ? `${dashboardData.procured} Quintals`
                      : "..."}
                  </strong>
                </div>

                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${Math.min(targetPercentage, 100)}%` }}
                  ></div>
                </div>

                <p className="progress-text">
                  {dashboardData
                    ? dashboardData.daily_target > 0
                      ? `${targetPercentage}% of today's target completed`
                      : "No daily target set"
                    : "..."}
                </p>

                <div className="progress-info">
                  <span>Remaining</span>
                  <strong>
                    {dashboardData
                      ? `${dashboardData.remaining} Quintals`
                      : "..."}
                  </strong>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ======================================================
            APPOINTMENTS
        ====================================================== */}
        {dashboardSection === "appointments" && (
          <section className="appointments">
            <div className="header">
              <h1>Appointments</h1>
              <p>View the procurement bookings entered into GrainFlow.</p>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Farmer</th>
                  <th>Date</th>
                  <th>Token</th>
                  <th>Crop</th>
                  <th>Quantity</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {bookingData.length > 0 ? (
                  bookingData.map((booking) => (
                    <tr key={booking.booking_id}>
                      <td>{booking.farmer_name}</td>
                      <td>{booking.booking_date}</td>
                      <td>#{booking.booking_id}</td>
                      <td>{booking.crop}</td>
                      <td>
                        {booking.quantity !== undefined
                          ? `${booking.quantity} kg`
                          : "—"}
                      </td>
                      <td>
                        <span className="status waiting">
                          {getBookingStatus(booking)}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6">No bookings available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* ======================================================
            QUEUE MANAGEMENT
        ====================================================== */}
        {dashboardSection === "queue" && (
          <section className="queue-section">
            <div className="header">
              <h1>Queue Management</h1>
              <p>Monitor the current farmer queue and waiting time.</p>
            </div>

            <div className="queue-summary">
              <div className="queue-card">
                <span>Current Token</span>
                <strong>
                  {processingBooking
                    ? `#${processingBooking.booking_id}`
                    : "—"}
                </strong>
              </div>

              <div className="queue-card">
                <span>Now Processing</span>
                <strong>
                  {processingBooking
                    ? processingBooking.farmer_name
                    : "No farmer"}
                </strong>
              </div>

              <div className="queue-card">
                <span>Waiting Farmers</span>
                <strong>
                  {dashboardData ? dashboardData.current_queue : "..."}
                </strong>
              </div>

              <div className="queue-card">
                <span>Estimated Wait</span>
                <strong>
                  {dashboardData
                    ? `${dashboardData.average_waiting_time} min`
                    : "..."}
                </strong>
              </div>
            </div>

            <h3>Live Queue</h3>

            <table>
              <thead>
                <tr>
                  <th>Token</th>
                  <th>Farmer</th>
                  <th>Crop</th>
                  <th>Quantity</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {bookingData.length > 0 ? (
                  bookingData.map((booking) => (
                    <tr key={booking.booking_id}>
                      <td>#{booking.booking_id}</td>
                      <td>{booking.farmer_name}</td>
                      <td>{booking.crop}</td>
                      <td>
                        {booking.quantity !== undefined
                          ? `${booking.quantity} kg`
                          : "—"}
                      </td>
                      <td>
                        <strong>{getBookingStatus(booking)}</strong>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5">No farmers currently in queue</td>
                  </tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* ======================================================
            PROCUREMENT
        ====================================================== */}
        {dashboardSection === "procurement" && (
          <>
            <div className="header">
              <h1>Procurement</h1>
              <p>Monitor today's procurement target and progress.</p>
            </div>

            <div className="bottom-section">
              <div className="progress-panel">
                <h2>🌾 Procurement Progress</h2>

                <div className="progress-info">
                  <span>Daily Target</span>
                  <strong>
                    {dashboardData
                      ? `${dashboardData.daily_target} Quintals`
                      : "..."}
                  </strong>
                </div>

                <div className="progress-info">
                  <span>Procured</span>
                  <strong>
                    {dashboardData
                      ? `${dashboardData.procured} Quintals`
                      : "..."}
                  </strong>
                </div>

                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${Math.min(targetPercentage, 100)}%` }}
                  ></div>
                </div>

                <p className="progress-text">
                  {dashboardData
                    ? dashboardData.daily_target > 0
                      ? `${targetPercentage}% of today's target completed`
                      : "No daily target set"
                    : "..."}
                </p>

                <div className="progress-info">
                  <span>Remaining</span>
                  <strong>
                    {dashboardData
                      ? `${dashboardData.remaining} Quintals`
                      : "..."}
                  </strong>
                </div>
              </div>

              <div className="status-panel">
                <h2>🏢 Centre Procurement Status</h2>

                {centreData.length > 0 ? (
                  centreData.map((centre, index) => (
                    <div className="status-item" key={index}>
                      <span>{centre.centre}</span>
                      <strong>{centre.procurement} Q</strong>
                    </div>
                  ))
                ) : (
                  <p>No procurement centre data available.</p>
                )}
              </div>
            </div>
          </>
        )}

        {/* ======================================================
            REPORTS
        ====================================================== */}
        {dashboardSection === "reports" && (
          <>
            <div className="header">
              <h1>Reports & Analytics</h1>
              <p>
                Analyse procurement, farmer visits, centres and queue
                performance.
              </p>
            </div>

            <div className="report-grid">
              <div className="report-card">
                <span>Daily Procurement</span>
                <strong>
                  {dashboardData ? `${dashboardData.procured} Q` : "..."}
                </strong>
                <p>
                  {dashboardData
                    ? dashboardData.daily_target > 0
                      ? `${targetPercentage}% of daily target`
                      : "No daily target set"
                    : "..."}
                </p>
              </div>

              <div className="report-card">
                <span>Farmer Visits</span>
                <strong>
                  {dashboardData ? dashboardData.todays_farmers : "..."}
                </strong>
                <p>Farmers served today</p>
              </div>

              <div className="report-card">
                <span>Average Waiting Time</span>
                <strong>
                  {dashboardData
                    ? `${dashboardData.average_waiting_time} min`
                    : "..."}
                </strong>
                <p>Based on current queue</p>
              </div>

              <div className="report-card">
                <span>Procurement Centres</span>
                <strong>{centreData.length}</strong>
                <p>Centres returned by the dashboard API</p>
              </div>
            </div>

            <div className="admin-section">
              <h2>🏛️ Centre-wise Performance</h2>

              <div className="centre-performance">
                <table>
                  <thead>
                    <tr>
                      <th>Centre</th>
                      <th>Farmers</th>
                      <th>Queue</th>
                      <th>Procurement</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {centreData.length > 0 ? (
                      centreData.map((centre, index) => (
                        <tr key={index}>
                          <td>{centre.centre}</td>
                          <td>{centre.farmers}</td>
                          <td>{centre.queue}</td>
                          <td>{centre.procurement} Q</td>
                          <td>{centre.status}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5">
                          No procurement centre data available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="system-alerts">
                <h3>🚨 System Alerts</h3>

                {alertsData.length > 0 ? (
                  alertsData.map((alert, index) => (
                    <div className="alert-item" key={index}>
                      <strong>
                        {alert.type === "warning" ? "⚠️" : "🤖"} {alert.title}
                      </strong>
                      <p>{alert.message}</p>
                    </div>
                  ))
                ) : (
                  <p>No system alerts available.</p>
                )}
              </div>
            </div>
          </>
        )}

        {/* ======================================================
            SETTINGS
        ====================================================== */}
        {dashboardSection === "settings" && (
          <section className="settings-section">
            <div className="header">
              <h1>Settings</h1>
              <p>Dashboard settings and system information.</p>
            </div>

            <div className="status-panel">
              <h2>⚙️ Dashboard Information</h2>

              <div className="status-item">
                <span>Dashboard Data</span>
                <strong>{dashboardData ? "Connected" : "Loading"}</strong>
              </div>

              <div className="status-item">
                <span>Booking Data</span>
                <strong>{bookingData.length} records</strong>
              </div>

              <div className="status-item">
                <span>Centre Data</span>
                <strong>{centreData.length} centres</strong>
              </div>

              <div className="status-item">
                <span>System Alerts</span>
                <strong>{alertsData.length} alerts</strong>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
function LoginPage({ onLogin }) {
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState("phone");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const requestOtp = async () => {
    if (!phone.trim()) {
      setMessage("Please enter your registered mobile number.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${AUTH_API_URL}/farmers/auth/request-otp`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            phone: phone.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to send OTP.");
      }

      setStep("otp");
      setMessage("OTP sent successfully. Use the prototype OTP provided by the system.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    if (!otp.trim()) {
      setMessage("Please enter the OTP.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${AUTH_API_URL}/farmers/auth/verify-otp`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            phone: phone.trim(),
            otp: otp.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "OTP verification failed.");
      }

      onLogin(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page login-page">
      <section className="login-card">
        <div className="login-icon">🌾</div>

        <span className="login-eyebrow">
          FARMER ACCESS
        </span>

        <h1>
          Welcome back to <span>GrainFlow</span>
        </h1>

        <p>
          Login with your registered mobile number to access your
          farmer profile, bookings and procurement journey.
        </p>

        {step === "phone" ? (
          <>
            <label>Registered mobile number</label>

            <input
              type="tel"
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
              placeholder="Enter your mobile number"
              maxLength="15"
            />

            <button
              className="primary-button login-button"
              onClick={requestOtp}
              disabled={loading}
            >
              {loading ? "Sending..." : "Send OTP"}
              <span>→</span>
            </button>
          </>
        ) : (
          <>
            <label>Enter OTP</label>

            <input
              type="text"
              value={otp}
              onChange={(event) => setOtp(event.target.value)}
              placeholder="Enter 6-digit OTP"
              maxLength="6"
            />

            <button
              className="primary-button login-button"
              onClick={verifyOtp}
              disabled={loading}
            >
              {loading ? "Verifying..." : "Verify & Login"}
              <span>✓</span>
            </button>

            <button
              className="login-back-button"
              onClick={() => {
                setStep("phone");
                setOtp("");
                setMessage("");
              }}
            >
              ← Change mobile number
            </button>
          </>
        )}

        {message && (
          <div className="login-message">
            {message}
          </div>
        )}
      </section>
    </main>
  );
}
export default App;