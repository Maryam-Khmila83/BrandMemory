
import { useState, useEffect } from "react";
import "./App.css";

const navigation = [
  { id: "Overview", icon: "◫" },
  { id: "Analytics", icon: "▥" },
  { id: "AI Assistant", icon: "✧" },
  { id: "Decision Replay", icon: "↺" },
  { id: "Reports", icon: "▤" },
];

function AnalyticsPage({ platforms, platformObjectives, monthlyData }) {
  const formatNumber = (value) =>
    Number(value).toLocaleString("en-US", {
      maximumFractionDigits: 0,
    });

  const formatROAS = (value) =>
    value == null ? "N/A" : `${Number(value).toFixed(2)}x`;

  const maxPlatformRoas = Math.max(
    0,
    ...platforms.map((item) => Number(item.roas) || 0)
  );

  const maxMonthlyRoas = Math.max(
    0,
    ...monthlyData.map((item) => Number(item.roas) || 0)
  );

  const objectives = ["Awareness", "Consideration", "Conversion"];

  return (
    <div className="analytics-page">

      <div className="analytics-header">
        <div>
          <span className="section-eyebrow">MARKETING INTELLIGENCE</span>
          <h1>Analytics</h1>
          <p>Understand your campaign performance across channels and time.</p>
        </div>
      </div>

      {/* PLATFORM PERFORMANCE */}
      <section className="analytics-section">
        <div className="section-heading">
          <div>
            <h2>Performance by platform</h2>
            <p>Overall return on advertising spend</p>
          </div>
          <span className="section-tag">All periods</span>
        </div>

        <div className="platform-chart">
          {platforms.map((item) => (
            <div className="platform-row" key={item.platform}>
              <div className="platform-name">{item.platform}</div>

              <div className="platform-bar-track">
                <div
                  className="platform-bar"
                  style={{
                    width: `${
                      maxPlatformRoas > 0
                        ? (Number(item.roas) / maxPlatformRoas) * 100
                        : 0
                    }%`,
                  }}
                />
              </div>

              <strong>{formatROAS(item.roas)}</strong>
            </div>
          ))}
        </div>
      </section>

      {/* PLATFORM BY OBJECTIVE */}
      <section className="analytics-section">
        <div className="section-heading">
          <div>
            <h2>Platform by objective</h2>
            <p>Compare results across campaign objectives</p>
          </div>
        </div>

        <div className="objective-grid">
          {objectives.map((objective) => {
            const objectiveData = platformObjectives.filter(
              (item) => item.objective === objective
            );

            return (
              <div className="objective-card" key={objective}>
                <h3>{objective}</h3>

                {objectiveData.map((item) => (
                  <div className="objective-row" key={item.platform}>
                    <span>{item.platform}</span>
                    <strong>{formatROAS(item.roas)}</strong>
                  </div>
                ))}
              </div>
            );
          })}
        </div>

        <p className="chart-note">
          ROAS is unavailable for Awareness and Consideration because
          these records report zero revenue.
        </p>
      </section>
      
      {/* MONTHLY TRENDS */}
      <section className="analytics-section">
        <div className="section-heading">
          <div>
            <h2>Monthly ROAS trends</h2>
            <p>Track conversion performance from 2023 to 2025</p>
          </div>
          <span className="section-tag">36 months</span>
        </div>

        <div className="monthly-chart-scroll">
          <div className="monthly-timeline">

            {/* YEAR LABELS */}
            <div className="monthly-years">
              {(() => {
                const years = [...new Set(
                  monthlyData.map((item) => item.month_date.slice(0, 4))
                )];

                return years.map((year) => {
                  const count = monthlyData.filter(
                    (item) => item.month_date.startsWith(year)
                  ).length;

                  return (
                    <div
                      className="monthly-year"
                      key={year}
                      style={{ gridColumn: `span ${count}` }}
                    >
                      {year}
                    </div>
                  );
                });
              })()}
            </div>

            {/* MONTHLY BARS */}
            <div className="monthly-bars">
              {monthlyData.map((item) => {
                const height =
                  maxMonthlyRoas > 0
                    ? (Number(item.roas) / maxMonthlyRoas) * 100
                    : 0;

                return (
                  <div className="monthly-column" key={item.month_date}>
                    <div className="monthly-bar-area">
                      <div
                        className={`monthly-bar ${
                          item.month_date === "2024-11"
                            ? "anomaly-bar"
                            : ""
                        }`}
                        style={{ height: `${height}%` }}
                        title={`${item.month_date}: ${formatROAS(item.roas)}`}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* MONTH LABELS */}
            <div className="monthly-months">
              {monthlyData.map((item) => {
                const monthNames = [
                  "Jan", "Feb", "Mar", "Apr",
                  "May", "Jun", "Jul", "Aug",
                  "Sep", "Oct", "Nov", "Dec"
                ];

                const month = Number(item.month_date.slice(5, 7));

                return (
                  <span
                    className="monthly-month"
                    key={item.month_date}
                  >
                    {monthNames[month - 1]}
                  </span>
                );
              })}
            </div>

          </div>
        </div>

        <div className="chart-legend">
          <span className="legend-dot" />
          <span>Monthly ROAS</span>
          <span className="legend-dot anomaly-dot" />
          <span>November 2024 — unusual result</span>
        </div>

        <p className="timeline-hint">
          <span>↔</span> Scroll horizontally to explore all 36 months.
        </p>
      </section>



      {/* DATA NOTE */}
      <p className="analytics-disclaimer">
        Demo data. ROAS = total revenue ÷ total advertising spend.
        ROAS is not profit and does not establish causality.
      </p>

    </div>
  );
}

function AssistantPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your BrandMemory assistant. I can help you explore FashionCo's campaign reports, performance data, and past marketing decisions. What would you like to know?",
      sources: [],
    },
  ]);

  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const suggestedQuestions = [
    "Why did FashionCo decide not to scale its summer campaign?",
    "Which marketing theme has the highest ROAS?",
    "What happened in November 2024?",
  ];

  async function sendMessage(question = input) {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || sending) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: trimmedQuestion },
    ]);

    setInput("");
    setSending(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/assistant/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("The assistant could not process your question.");
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I'm having trouble connecting to the AI service. Please check that the FastAPI server and Ollama are running, then try again.",
          sources: [],
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendMessage();
  }

  return (
    <div className="assistant-page">
      <div className="assistant-header">
        <div>
          <span className="section-eyebrow">MARKETING INTELLIGENCE</span>
          <h1>AI Assistant</h1>
          <p>
            Ask questions about FashionCo's campaigns, performance,
            and marketing decisions.
          </p>
        </div>

        <div className="assistant-status">
          <span className="status-dot"></span>
          AI assistant
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div
              className={`chat-message ${message.role}`}
              key={index}
            >
              <div className="message-avatar">
                {message.role === "assistant" ? "✧" : "F"}
              </div>

              <div className="message-content">
                <span className="message-sender">
                  {message.role === "assistant" ? "BrandMemory" : "You"}
                </span>

                <div className="message-bubble">
                  {message.role === "assistant" ? (
                    <RichText content={message.content} />
                  ) : (
                    message.content
                  )}
                </div>

                {message.sources?.length > 0 && (
                  <details className="message-sources">
                    <summary>
                      View retrieved sources ({message.sources.length})
                    </summary>

                    <div className="sources-list">
                      {message.sources.map((source, sourceIndex) => (
                        <div
                          className="source-item"
                          key={`${source.name}-${sourceIndex}`}
                        >
                          <span className="source-icon">▤</span>
                          <span>{source.name}</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))}

          {sending && (
            <div className="chat-message assistant">
              <div className="message-avatar">✧</div>

              <div className="message-content">
                <span className="message-sender">BrandMemory</span>

                <div className="message-bubble typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        {messages.length === 1 && (
          <div className="suggested-questions">
            <p>TRY ASKING</p>

            <div className="suggestion-list">
              {suggestedQuestions.map((question) => (
                <button
                  key={question}
                  onClick={() => sendMessage(question)}
                  disabled={sending}
                >
                  {question}
                  <span>↗</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <form className="chat-input-area" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask something about FashionCo..."
            rows={1}
            disabled={sending}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSubmit(event);
              }
            }}
          />

          <button
            type="submit"
            className="chat-send-button"
            disabled={!input.trim() || sending}
          >
            {sending ? "..." : "↑"}
          </button>
        </form>

        <p className="chat-disclaimer">
          BrandMemory uses demo data. AI-generated answers should be
          reviewed against the retrieved sources.
        </p>
      </div>
    </div>
  );
}


function RichText({ content }) {
  if (!content) return null;

  const lines = content.split("\n");
  const elements = [];
  let index = 0;

  function renderInline(text) {
    return text.split(/(\*\*.*?\*\*)/g).map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  }

  while (index < lines.length) {
    const line = lines[index].trim();

    if (!line) {
      index++;
      continue;
    }

    // Bullet lists
    if (/^[-*]\s+/.test(line)) {
      const items = [];

      while (
        index < lines.length &&
        /^[-*]\s+/.test(lines[index].trim())
      ) {
        items.push(lines[index].trim().replace(/^[-*]\s+/, ""));
        index++;
      }

      elements.push(
        <ul key={`list-${index}`}>
          {items.map((item, i) => (
            <li key={i}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      continue;
    }

    // Numbered lists
    if (/^\d+\.\s+/.test(line)) {
      const items = [];

      while (
        index < lines.length &&
        /^\d+\.\s+/.test(lines[index].trim())
      ) {
        items.push(
          lines[index].trim().replace(/^\d+\.\s+/, "")
        );
        index++;
      }

      elements.push(
        <ol key={`ordered-${index}`}>
          {items.map((item, i) => (
            <li key={i}>{renderInline(item)}</li>
          ))}
        </ol>
      );
      continue;
    }

    elements.push(
      <p key={`paragraph-${index}`}>
        {renderInline(line)}
      </p>
    );

    index++;
  }

  return <div className="rich-text">{elements}</div>;
}


function DecisionReplayPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runReplay(event) {
    event.preventDefault();

    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/decision-replay",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question.trim(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Could not retrieve the decision.");
      }

      const data = await response.json();

      if (!data.found) {
        setError(data.message || "No relevant decision was found.");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(
        "Unable to connect to BrandMemory. Check that the FastAPI server and Ollama are running."
      );
    } finally {
      setLoading(false);
    }
  }

  function renderExperimentTable(markdown) {
    if (!markdown) return null;

    const rows = markdown
      .split("\n")
      .filter((line) => line.trim().startsWith("|"))
      .filter((line) => !line.includes("---"))
      .map((line) =>
        line
          .split("|")
          .slice(1, -1)
          .map((cell) => cell.trim())
      );

    if (rows.length < 2) return null;

    return (
      <div className="replay-table-wrapper">
        <table className="replay-table">
          <thead>
            <tr>
              {rows[0].map((cell, index) => (
                <th key={index}>{cell}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.slice(1).map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="replay-page">

      <div className="replay-header">
        <div>
          <span className="section-eyebrow">
            MARKETING INTELLIGENCE
          </span>
          <h1>Decision Replay</h1>
          <p>
            Revisit marketing decisions, examine their supporting
            evidence, and understand what happened afterward.
          </p>
        </div>
      </div>

      {/* QUESTION FORM */}
      <form className="replay-search" onSubmit={runReplay}>
        <label htmlFor="replay-question">
          Which decision would you like to investigate?
        </label>

        <div className="replay-search-row">
          <input
            id="replay-question"
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="e.g. Why did FashionCo decide not to scale its summer campaign?"
            disabled={loading}
          />

          <button
            type="submit"
            className="primary-button"
            disabled={!question.trim() || loading}
          >
            {loading ? "Investigating..." : "↺ Replay decision"}
          </button>
        </div>

        <span className="replay-search-hint">
          Try asking why a campaign was paused, changed, or not scaled.
        </span>
      </form>

      {loading && (
        <div className="replay-loading">
          <span className="replay-loading-icon">↺</span>
          <p>Retrieving the decision and examining its evidence...</p>
        </div>
      )}

      {error && (
        <div className="replay-error">
          {error}
        </div>
      )}

      {result && (
        <div className="replay-results">

          {/* DECISION OVERVIEW */}
          <section className="replay-section">
            <div className="replay-section-heading">
              <div>
                <span className="section-eyebrow">
                  ORIGINAL DECISION
                </span>
                <h2>What did FashionCo decide?</h2>
              </div>

              <span className="replay-status">
                {result.decision.status?.includes("Approved for experiment planning")
                  ? "Planning approved"
                  : "Recorded"}
              </span>
            </div>

            <div className="replay-decision-card">
              <span className="replay-card-label">
                THE DECISION
              </span>

              <p className="replay-decision-text">
                {result.decision.decision}
              </p>

              <div className="replay-source">
                <span>▤</span>
                {result.decision.source}
              </div>
            </div>

            <div className="replay-detail-grid">
              <div className="replay-detail-card">
                <h3>Context and evidence</h3>
                <RichText content={result.decision.context} />
              </div>

              <div className="replay-detail-card">
                <h3>Reasoning</h3>
                <RichText content={result.decision.reasoning} />
              </div>
            </div>
          </section>

          {/* ALTERNATIVES AND RISKS */}
          <section className="replay-section">
            <div className="replay-section-heading">
              <div>
                <span className="section-eyebrow">
                  DECISION ANALYSIS
                </span>
                <h2>What was considered?</h2>
              </div>
            </div>

            <div className="replay-detail-grid">
              <div className="replay-detail-card">
                <h3>Alternatives considered</h3>
                <RichText content={result.decision.alternatives} />
              </div>

              <div className="replay-detail-card">
                <h3>Risks and limitations</h3>
                <RichText content={result.decision.risks} />
              </div>
            </div>
          </section>

          {/* EVIDENCE */}
          <section className="replay-section">
            <div className="replay-section-heading">
              <div>
                <span className="section-eyebrow">
                  EVIDENCE QUALITY
                </span>
                <h2>What supports this decision?</h2>
                <p>
                  Documents retrieved to examine the original decision.
                </p>
              </div>

              <span className="replay-count">
                {result.evidence?.length || 0} sources
              </span>
            </div>

            <div className="replay-evidence-list">
              {result.evidence?.map((item, index) => (
                <div className="replay-evidence-card" key={index}>
                  <div className="replay-evidence-top">
                    <div className="replay-evidence-name">
                      <span>▤</span>
                      <strong>{item.source}</strong>
                    </div>

                    <span className="evidence-classification">
                      {item.classification}
                    </span>
                  </div>

                  {item.supports?.length > 0 && (
                    <div className="evidence-points">
                      <strong>What it supports</strong>
                      <ul>
                        {item.supports.map((point, pointIndex) => (
                          <li key={pointIndex}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {item.limitations?.length > 0 && (
                    <div className="evidence-limitations">
                      <strong>Limitations</strong>
                      <ul>
                        {item.limitations.map((limitation, limitIndex) => (
                          <li key={limitIndex}>{limitation}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <span className="evidence-data-status">
                    Data status: {item.data_status || "Not specified"}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* EXPERIMENT RESULTS */}
          {result.experiment_analysis && (
            <section className="replay-section">
              <div className="replay-section-heading">
                <div>
                  <span className="section-eyebrow">
                    FOLLOW-UP EXPERIMENT
                  </span>
                  <h2>What happened afterward?</h2>
                  <p>
                    {result.experiment_analysis.objective}
                  </p>
                </div>
              </div>

              <div className="replay-experiment-card">
                <h3>Experiment performance</h3>

                {renderExperimentTable(
                  result.experiment_analysis.results
                )}

                <div className="replay-comparison">
                  <strong>Performance comparison</strong>
                  <RichText content={result.experiment_analysis.comparison} />
                </div>
              </div>

              <div className="replay-detail-grid">
                <div className="replay-detail-card">
                  <h3>Hypothesis evaluation</h3>
                  <RichText content={result.experiment_analysis.hypothesis_evaluation} />
                </div>

                <div className="replay-detail-card">
                  <h3>Lessons learned</h3>
                  <RichText content={result.experiment_analysis.lessons} />
                </div>
              </div>

              <div className="replay-recommendation">
                <span className="replay-card-label">
                  RECOMMENDED NEXT STEP
                </span>
                <RichText content={result.experiment_analysis.recommendation} />
              </div>

              <p className="replay-simulation-note">
                <span>ⓘ</span>
                Experiment results are simulated for this portfolio
                demonstration. They should not be interpreted as real
                company results.
              </p>
            </section>
          )}

          {/* CLAIM VERIFICATION */}
          {result.claim_verification?.length > 0 && (
            <section className="replay-section">
              <div className="replay-section-heading">
                <div>
                  <span className="section-eyebrow">
                    CLAIM VERIFICATION
                  </span>
                  <h2>Reasoning checks</h2>
                </div>
              </div>

              {result.claim_verification.map((item, index) => (
                <div className="replay-detail-card" key={index}>
                  <h3>{item.claim}</h3>
                  {item.evidence_checks?.map((check, checkIndex) => (
                    <p key={checkIndex}>
                      {check.source}: {check.classification}
                    </p>
                  ))}
                </div>
              ))}
            </section>
          )}

        </div>
      )}

      <p className="replay-disclaimer">
        BrandMemory uses fictional FashionCo demo data. Evidence
        classifications describe support from retrieved documents,
        not independent verification of real-world outcomes.
      </p>

    </div>
  );
}

function ReportsPage() {
  const [generating, setGenerating] = useState(false);
  const [success, setSuccess] = useState("");

  async function generateReport() {
    if (generating) return;

    setGenerating(true);
    setSuccess("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/reports/generate",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Could not generate the PDF report.");
      }

      const blob = await response.blob();

      if (blob.type !== "application/pdf") {
        throw new Error("The server did not return a valid PDF file.");
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "FashionCo_Marketing_Report.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);

      setSuccess("Your marketing report has been generated and downloaded.");
    } catch (err) {
      console.error("Report download failed:", err);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="reports-page">
      <div className="reports-header">
        <div>
          <span className="section-eyebrow">
            MARKETING INTELLIGENCE
          </span>
          <h1>Reports</h1>
          <p>
            Generate a PDF report with FashionCo's marketing performance
            and campaign insights.
          </p>
        </div>
      </div>

      <section className="reports-card">
        <div className="reports-icon">▤</div>

        <div className="reports-card-content">
          <span className="section-eyebrow">
            MARKETING PERFORMANCE
          </span>

          <h2>FashionCo Marketing Report</h2>

          <p>
            A summary of campaign performance, including key metrics,
            theme and platform comparisons, monthly trends, and
            performance insights.
          </p>

          <div className="reports-details">
            <span>PDF format</span>
            <span>2023–2025 reporting period</span>
            <span>Demo data</span>
          </div>

          <button
            className="primary-button"
            onClick={generateReport}
            disabled={generating}
          >
            {generating
              ? "Generating report..."
              : "↓ Generate PDF report"}
          </button>

          {success && (
            <p className="reports-success">{success}</p>
          )}

        </div>
      </section>

      <p className="reports-disclaimer">
        This report uses public dataset-derived and simulated FashionCo
        demonstration data. It does not represent verified results
        from a real company.
      </p>
    </div>
  );
}

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("brandmemory-theme") === "dark";
  });

  useEffect(() => {
    localStorage.setItem(
      "brandmemory-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);
  const [activePage, setActivePage] = useState("Overview");

  // Dashboard data
  const [dashboard, setDashboard] = useState(null);
  const [themes, setThemes] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [platformObjectives, setPlatformObjectives] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);

  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch dashboard data from FastAPI
  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [
          dashboardResponse,
          themesResponse,
          platformsResponse,
          objectivesResponse,
          monthlyResponse
        ] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/dashboard"),
          fetch("http://127.0.0.1:8000/api/analytics/themes"),
          fetch("http://127.0.0.1:8000/api/analytics/platforms"),
          fetch("http://127.0.0.1:8000/api/analytics/platform-objectives"),
          fetch("http://127.0.0.1:8000/api/analytics/monthly")
        ]);

        if (
          !dashboardResponse.ok ||
          !themesResponse.ok ||
          !platformsResponse.ok ||
          !objectivesResponse.ok ||
          !monthlyResponse.ok
        ) {
          throw new Error("Could not load dashboard data.");
        }


        const dashboardData = await dashboardResponse.json();
        const themesData = await themesResponse.json();
        const platformsData = await platformsResponse.json();
        const objectivesData = await objectivesResponse.json();
        const monthlyDataResult = await monthlyResponse.json();

        setDashboard(dashboardData);
        setThemes(themesData);
        setPlatforms(platformsData);
        setPlatformObjectives(objectivesData);
        setMonthlyData(monthlyDataResult);

      } catch (err) {
        setError(err.message);

      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  // Find the highest ROAS for chart scaling
  const maxRoas = Math.max(
    0,
    ...themes.map((theme) => Number(theme.roas) || 0)
  );

  // Find the highest-performing theme
  const topTheme = [...themes].sort(
    (a, b) => Number(b.roas) - Number(a.roas)
  )[0];

  return (
    <div className={`app ${darkMode ? "dark" : ""}`}>

      <aside className="sidebar">

        <div className="brand">
          <img
            src="/brand/brandmemory-logo.png"
            alt="BrandMemory - Marketing Intelligence"
            className="brand-image"
          />
        </div>

        <p className="nav-label">WORKSPACE</p>

        <nav>
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                activePage === item.id ? "active" : ""
              }`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.id}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">

          <button
            className="theme-button"
            onClick={() => setDarkMode(!darkMode)}
          >
            <span>{darkMode ? "☀" : "☾"}</span>
            {darkMode ? "Light mode" : "Dark mode"}
          </button>

          <div className="profile">
            <div className="avatar">F</div>
            <div>
              <strong>FashionCo</strong>
              <span>Demo workspace</span>
            </div>
          </div>

        </div>
      </aside>

      <main className="main-content">

        <header className="topbar">
          <div>
            <span className="breadcrumb">
              Workspace / {activePage}
            </span>
          </div>

          <div className="topbar-right">
            <span className="status-dot"></span>
            <span>Demo data</span>
          </div>
        </header>

        {activePage === "Overview" ? (

          <div className="page-content">

            {/* Loading and error messages */}
            {loading && (
              <p>Loading your marketing data...</p>
            )}

            {error && (
              <p style={{ color: "#d45b6b" }}>
                {error}
              </p>
            )}

            <section className="welcome">
              <div>
                <p className="eyebrow">
                  MARKETING OVERVIEW
                </p>

                <h1>Good morning!</h1>

                <p>
                  Here's what's happening with your marketing performance.
                </p>
              </div>

              <button
                className="primary-button"
                onClick={() => setActivePage("Reports")}
              >
                + Generate report
              </button>
            </section>

            {/* Dynamic KPI cards */}
            <section className="kpi-grid">

              <KpiCard
                label="Campaign groups"
                value={
                  loading
                    ? "..."
                    : dashboard?.campaign_groups?.toLocaleString() ?? "—"
                }
                note="Across FashionCo data"
                icon="▦"
              />

              <KpiCard
                label="Campaign themes"
                value={
                  loading
                    ? "..."
                    : dashboard?.campaign_themes ?? "—"
                }
                note="Tracked categories"
                icon="◈"
              />

              <KpiCard
                label="Top theme ROAS"
                value={
                  loading
                    ? "..."
                    : dashboard?.top_theme_roas != null
                      ? `${Number(dashboard.top_theme_roas).toFixed(2)}x`
                      : "—"
                }
                note={
                  dashboard?.top_theme ?? "Best-performing theme"
                }
                icon="↗"
              />

              <KpiCard
                label="Reporting period"
                value={
                  loading
                    ? "..."
                    : dashboard?.reporting_period?.start &&
                      dashboard?.reporting_period?.end
                      ? `${dashboard.reporting_period.start.slice(0, 4)}–${dashboard.reporting_period.end.slice(0, 4)}`
                      : "—"
                }
                note="Available campaign history"
                icon="◷"
              />

            </section>

            <section className="content-grid">

              {/* Dynamic performance chart */}
              <div className="panel performance-panel">

                <div className="panel-heading">
                  <div>
                    <h3>Performance by theme</h3>
                    <p>Overall return on advertising spend</p>
                  </div>

                  <span className="period-tag">
                    All periods
                  </span>
                </div>

                <div className="chart">

                  {themes.map((theme) => {

                    const roas = Number(theme.roas) || 0;

                    const width = maxRoas > 0
                      ? (roas / maxRoas) * 100
                      : 0;

                    return (
                      <div
                        className="bar-row"
                        key={theme.theme}
                      >

                        <span className="bar-label">
                          {theme.theme}
                        </span>

                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{ width: `${width}%` }}
                          ></div>
                        </div>

                        <strong>
                          {roas.toFixed(2)}x
                        </strong>

                      </div>
                    );
                  })}

                  {!loading && !error && themes.length === 0 && (
                    <p>No theme data available.</p>
                  )}

                </div>

                <p className="chart-note">
                  ROAS = total revenue ÷ total advertising spend.
                  Demo data.
                </p>

              </div>

              {/* Dynamic key insight */}
              <div className="panel insight-panel">

                <div className="panel-heading">
                  <div>
                    <h3>Key insight</h3>
                    <p>From your campaign data</p>
                  </div>

                  <span className="insight-icon">✧</span>
                </div>

                <div className="insight-content">

                  <span className="insight-tag">
                    PERFORMANCE HIGHLIGHT
                  </span>

                  <h2>
                    {loading
                      ? "Analyzing performance..."
                      : topTheme
                        ? `${topTheme.theme} leads by ROAS`
                        : "No performance insights yet"}
                  </h2>

                  <p>
                    {loading
                      ? "Please wait while your marketing data is loading."
                      : topTheme
                        ? `${topTheme.theme} recorded the highest overall ROAS at ${Number(topTheme.roas).toFixed(2)}x.`
                        : "No theme performance data is currently available."}
                  </p>

                </div>

                <button
                  className="text-button"
                  onClick={() => setActivePage("Analytics")}
                >
                  Explore analytics →
                </button>

              </div>

            </section>

            {/* Quick navigation */}
            <section className="panel bottom-panel">

              <div className="panel-heading">
                <div>
                  <h3>Explore BrandMemory</h3>
                  <p>Choose what you want to work on next.</p>
                </div>
              </div>

              <div className="quick-links">

                <button
                  onClick={() => setActivePage("AI Assistant")}
                >
                  <span>✧</span>
                  <strong>Ask AI Assistant</strong>
                  <small>Explore your marketing data</small>
                </button>

                <button
                  onClick={() => setActivePage("Decision Replay")}
                >
                  <span>↺</span>
                  <strong>Decision Replay</strong>
                  <small>Understand past decisions</small>
                </button>

                <button
                  onClick={() => setActivePage("Reports")}
                >
                  <span>▤</span>
                  <strong>View reports</strong>
                  <small>Generate and access reports</small>
                </button>

              </div>

            </section>

          </div>

        ) : 

        activePage === "Analytics" ? (
          <AnalyticsPage
            platforms={platforms}
            platformObjectives={platformObjectives}
            monthlyData={monthlyData}
          />
        ) : activePage === "AI Assistant" ? (
          <AssistantPage />
        ) : activePage === "Decision Replay" ? (
          <DecisionReplayPage />
        ) : activePage === "Reports" ? (
          <ReportsPage />
        ) : (
          <div className="placeholder-page">

            <span className="placeholder-icon">
              {navigation.find(
                (item) => item.id === activePage
              )?.icon}
            </span>

            <h1>{activePage}</h1>

            <p>
              This section will be built in the next steps.
            </p>

            <button
              className="primary-button"
              onClick={() => setActivePage("Overview")}
            >
              Back to overview
            </button>

          </div>
        )}
      </main>

    </div>
  );
}

function KpiCard({ label, value, note, icon }) {
  return (
    <div className="panel kpi-card">

      <div className="kpi-top">
        <span>{label}</span>
        <span className="kpi-icon">{icon}</span>
      </div>

      <h2>{value}</h2>

      <p>{note}</p>

    </div>
  );
}

export default App;
