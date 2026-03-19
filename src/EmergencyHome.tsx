import React from "react";
import "./EmergencyHome.css";

const EmergencyHome: React.FC = () => {
  const emergencyOptions = [
    { title: "Police", subtitle: "Security & crime response", icon: "🚓" },
    { title: "Ambulance", subtitle: "Medical emergency support", icon: "🚑" },
    { title: "Fire Rescue", subtitle: "Fire & hazard response", icon: "🚒" },
    { title: "Disaster", subtitle: "Flood, collapse, evacuation", icon: "⚠️" },
  ];

  const incidents = [
    { title: "Road Accident", status: "Dispatching", area: "Mombasa CBD" },
    { title: "Medical Distress", status: "Active", area: "Nyali" },
    { title: "Fire Alert", status: "Resolved", area: "Likoni" },
  ];

  return (
    <div className="em-page">
      <div className="em-slider-arrow em-left">&#8249;</div>
      <div className="em-slider-arrow em-right">&#8250;</div>

      <section className="em-hero-card">
        <header className="em-topbar">
          <div className="em-logo">
            <span className="em-logo-icon"></span>
            <span className="em-logo-text">Emergency Response</span>
          </div>

          <nav className="em-nav-links">
            <a href="#services">Services</a>
            <a href="#report">Report</a>
            <a href="#responders">Responders</a>
            <a href="#tracking">Tracking</a>
          </nav>

          <button className="em-action-btn">Report Incident</button>
        </header>

        <div className="em-hero-content">
          <div className="em-left-copy">
            <p className="em-small-copy">
              Fast reporting for accidents,
              <br />
              crime, fire outbreaks and
              <br />
              medical emergencies with
              <br />
              real-time response support.
            </p>

            <h1>
              Rapid
              <br />
              Emergency
              <br />
              Response
              <br />
              <span className="em-white-text">When It Matters</span>
            </h1>

            <div className="em-cta-row">
              <button className="em-primary-btn">Send SOS</button>
              <button className="em-secondary-btn">Track Incident</button>
            </div>
          </div>

          <div className="em-center-visual">
            <div className="em-beacon-wrap">
              <div className="em-signal-ring em-ring-1"></div>
              <div className="em-signal-ring em-ring-2"></div>
              <div className="em-signal-ring em-ring-3"></div>

              <div className="em-emblem">
                <div className="em-cross-vertical"></div>
                <div className="em-cross-horizontal"></div>
              </div>

              <div className="em-pin">
                <div className="em-pin-dot"></div>
              </div>
            </div>
          </div>

          <div className="em-right-panel">
            <p className="em-small-copy em-right-copy">
              Connect instantly to the
              <br />
              right department and
              <br />
              monitor rescue progress
            </p>

            <div className="em-control-card">
              <div className="em-next-tag">Live Overview &gt;</div>

              <div className="em-control-grid">
                {emergencyOptions.map((item) => (
                  <div className="em-option-card" key={item.title}>
                    <div className="em-option-icon">{item.icon}</div>
                    <div>
                      <h3>{item.title}</h3>
                      <p>{item.subtitle}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="em-lower-panel">
          <div className="em-status-board">
            <div className="em-board-header">
              <h2>Recent Emergency Cases</h2>
              <span>Live updates</span>
            </div>

            <div className="em-incident-list">
              {incidents.map((incident) => (
                <div
                  className="em-incident-item"
                  key={incident.title + incident.area}
                >
                  <div>
                    <h4>{incident.title}</h4>
                    <p>{incident.area}</p>
                  </div>
                  <span
                    className={`em-status-pill ${incident.status.toLowerCase().replace(/\s+/g, "-")}`}
                  >
                    {incident.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="em-map-card">
            <div className="em-map-header">
              <h3>Responder Coverage</h3>
              <span>GPS zones</span>
            </div>

            <div className="em-map-grid">
              <div className="em-map-line em-map-line-v1"></div>
              <div className="em-map-line em-map-line-v2"></div>
              <div className="em-map-line em-map-line-h1"></div>
              <div className="em-map-line em-map-line-h2"></div>

              <span className="em-map-marker em-marker-a"></span>
              <span className="em-map-marker em-marker-b"></span>
              <span className="em-map-marker em-marker-c"></span>
              <span className="em-map-marker em-marker-d"></span>
            </div>
          </div>
        </div>

        <footer className="em-bottom-info">
          <div>
            <p>Emergency Support</p>
            <span>24/7 Availability</span>
          </div>

          <div>
            <p>Mombasa, Kenya</p>
            <span>Integrated Response Network</span>
          </div>

          <div>
            <p>Police • Ambulance • Fire</p>
            <span>Real-Time Coordination</span>
          </div>
        </footer>
      </section>
    </div>
  );
};

export default EmergencyHome;
