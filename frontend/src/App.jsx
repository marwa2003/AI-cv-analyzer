import { useRef, useState } from "react";

import {
  LayoutDashboard,
  BriefcaseBusiness,
  Users,
  Settings,
  FileSearch,
  Trophy,
  Upload,
  ChevronRight,
  LoaderCircle,
  X,
} from "lucide-react";

import "./index.css";


function ScoreBar({ score }) {
  const value = Number(score) || 0;

  return (
    <div className="score-wrapper">
      <div className="score-bar">
        <div
          className="score-progress"
          style={{
            width: `${Math.min(Math.max(value, 0), 100)}%`,
          }}
        />
      </div>

      <span>{value.toFixed(2)}%</span>
    </div>
  );
}


function SkillBadge({ result, showTilde }) {
  const matchType = result.match_type;

  const icon =
    matchType === "exact"
      ? "✓ "
      : matchType === "related" && showTilde
      ? "~ "
      : matchType === "related"
      ? "✓ "
      : "✕ ";

  return (
    <span className={`badge badge-${matchType}`}>
      {icon}
      {result.job_skill}
    </span>
  );
}


function App() {

  // ==========================================================
  // STATE
  // ==========================================================

  const fileInputRef = useRef(null);

  const [activeSection, setActiveSection] = useState("dashboard");

  const [selectedFiles, setSelectedFiles] = useState([]);

  const [jobDescription, setJobDescription] = useState(
`Machine Learning Intern

Required skills:
Python, Machine Learning, Scikit-learn, Pandas, NumPy, SQL, NLP, Git, Docker

Preferred skills:
RAG, FastAPI, Cloud platforms

Responsibilities:
Clean and preprocess datasets.
Train and evaluate machine learning models.
Perform exploratory data analysis.
Develop machine learning solutions.
Work with the AI team.
Document experiments and results.`
  );

  const [job, setJob] = useState(null);

  const [candidates, setCandidates] = useState([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [selectedCandidate, setSelectedCandidate] =
    useState(null);

  const [showTopOnly, setShowTopOnly] = useState(false);

  const [darkMode, setDarkMode] = useState(false);


  // ==========================================================
  // FILE SELECTION
  // ==========================================================

  const handleFileChange = (event) => {

    const files = Array.from(
      event.target.files || []
    );

    const pdfFiles = files.filter(
      (file) =>
        file.type === "application/pdf" ||
        file.name
          .toLowerCase()
          .endsWith(".pdf")
    );

    setSelectedFiles(pdfFiles);

    setError("");

    event.target.value = "";
  };


  // ==========================================================
  // OPEN FILE SELECTOR
  // ==========================================================

  const handleUploadClick = () => {

    fileInputRef.current?.click();

  };


  // ==========================================================
  // REMOVE ONE FILE
  // ==========================================================

  const removeFile = (indexToRemove) => {

    setSelectedFiles(
      (previousFiles) =>
        previousFiles.filter(
          (_, index) =>
            index !== indexToRemove
        )
    );

  };


  // ==========================================================
  // ANALYZE
  // ==========================================================

  const handleAnalyze = async () => {

    if (selectedFiles.length === 0) {

      setError(
        "Please select at least one CV."
      );

      return;
    }

    if (!jobDescription.trim()) {

      setError(
        "Please enter a job description."
      );

      return;
    }

    setLoading(true);
    setError("");

    try {

      const formData = new FormData();

      selectedFiles.forEach(
        (file) => {
          formData.append(
            "cvs",
            file
          );
        }
      );

      formData.append(
        "job_description",
        jobDescription
      );


      const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );


      if (!response.ok) {

        const text =
          await response.text();

        throw new Error(
          text ||
          `Server error: ${response.status}`
        );
      }


      const data =
        await response.json();


      setJob(
        data.job || null
      );

      setCandidates(
        data.candidates || []
      );

      setSelectedCandidate(
        data.top_candidate || null
      );


    } catch (err) {

      console.error(
        "Analysis error:",
        err
      );

      setError(
        "Unable to connect to the AI Analyzer API. " +
        "Make sure FastAPI is running on port 8000."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==========================================================
  // TOP CANDIDATE
  // ==========================================================

  const topCandidate =
    candidates.length > 0
      ? candidates[0]
      : null;


  // ==========================================================
  // JOB
  // ==========================================================

  const jobTitle =
    job?.job_title ||
    "Machine Learning Intern";

  const visibleCandidates = showTopOnly
    ? candidates.filter(
        (c) => Number(c.smart_score) >= 50
      )
    : candidates;


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className={darkMode ? "app theme-dark" : "app"}>


      {/* ======================================================
          SIDEBAR
      ====================================================== */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            <FileSearch size={22} />
          </div>

          <div>
            <h2>CV Analyzer</h2>
            <span>AI Screening</span>
          </div>

        </div>


        <nav>

          <p className="menu-title">
            MAIN MENU
          </p>

          <button
            type="button"
            className={
              activeSection === "dashboard"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActiveSection("dashboard")}
          >
            <LayoutDashboard size={19} />
            Dashboard
          </button>

          <button
            type="button"
            className={
              activeSection === "jobs"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActiveSection("jobs")}
          >
            <BriefcaseBusiness size={19} />
            Jobs
          </button>

          <button
            type="button"
            className={
              activeSection === "candidates"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActiveSection("candidates")}
          >
            <Users size={19} />
            Candidates
          </button>

          <p className="menu-title settings-title">
            SYSTEM
          </p>

          <button
            type="button"
            className={
              activeSection === "settings"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActiveSection("settings")}
          >
            <Settings size={19} />
            Settings
          </button>

        </nav>


        <div className="sidebar-bottom">

          <div className="ai-status">

            <span className="status-dot"></span>

            <div>
              <strong>AI Engine</strong>

              <small>
                {loading
                  ? "Analyzing..."
                  : "System ready"}
              </small>
            </div>

          </div>

        </div>

      </aside>


      {/* ======================================================
          MAIN
      ====================================================== */}

      <main className="main">


        {/* ====================================================
            DASHBOARD SECTION
        ==================================================== */}

        {activeSection === "dashboard" && (

          <div>

            <header className="header">

              <div>

                <h1>Dashboard</h1>

                <p>
                  AI-powered candidate screening
                </p>

              </div>


              <div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  multiple
                  onChange={handleFileChange}
                  style={{
                    display: "none"
                  }}
                />


                <button
                  className="upload-btn"
                  onClick={handleUploadClick}
                  disabled={loading}
                >

                  <Upload size={18} />

                  Upload CVs

                </button>

              </div>

            </header>


            {selectedFiles.length > 0 && (

              <section
                className="selected-files"
                style={{
                  marginBottom: "20px"
                }}
              >

                <div className="selected-files-header">

                  <h3>
                    Selected CVs (
                    {selectedFiles.length}
                    )
                  </h3>

                  <span>
                    Multiple files selected
                  </span>

                </div>


                <div className="file-list">

                  {selectedFiles.map(
                    (file, index) => (

                      <div
                        className="file-row"
                        key={`${file.name}-${index}`}
                      >

                        <div className="file-row-info">

                          <FileSearch
                            size={18}
                          />

                          <div>

                            <strong>
                              {file.name}
                            </strong>

                            <small>
                              {(
                                file.size /
                                1024
                              ).toFixed(1)}{" "}
                              KB
                            </small>

                          </div>

                        </div>


                        <button
                          className="file-remove-btn"
                          onClick={() =>
                            removeFile(index)
                          }
                          disabled={loading}
                        >

                          <X size={17} />

                        </button>

                      </div>

                    )
                  )}

                </div>

              </section>

            )}


            <section className="job-header">

              <div className="job-main">

                <span className="job-label">
                  CURRENT JOB
                </span>


                <h2>
                  {jobTitle}
                </h2>


                <p>
                  Candidate screening based on
                  skills, experience, education
                  and projects.
                </p>


                <textarea
                  className="job-textarea"
                  value={jobDescription}
                  onChange={(event) =>
                    setJobDescription(
                      event.target.value
                    )
                  }
                  placeholder="Enter the job description..."
                />


                {error && (

                  <div className="error-banner">

                    {error}

                  </div>

                )}


                <button
                  className="analyze-btn"
                  onClick={handleAnalyze}
                  disabled={loading}
                >

                  {loading ? (

                    <>

                      <LoaderCircle
                        size={17}
                        className="spin"
                      />

                      Analyzing{" "}
                      {selectedFiles.length}{" "}
                      CV
                      {selectedFiles.length > 1
                        ? "s"
                        : ""}...

                    </>

                  ) : (

                    <>

                      <FileSearch
                        size={17}
                      />

                      Analyze Candidates

                    </>

                  )}

                </button>

              </div>


              <button
                className="job-button"
                onClick={() => setActiveSection("jobs")}
              >
                View Job
                <ChevronRight size={17} />
              </button>

            </section>


            <section className="stats">


              <div className="stat-card">

                <div className="stat-icon purple">
                  <Users size={21} />
                </div>

                <div>
                  <span>CVs Analyzed</span>

                  <strong>
                    {candidates.length}
                  </strong>
                </div>

              </div>


              <div className="stat-card">

                <div className="stat-icon green">
                  <Trophy size={21} />
                </div>

                <div>

                  <span>Best Score</span>

                  <strong>
                    {topCandidate
                      ? `${Number(
                          topCandidate.smart_score
                        ).toFixed(2)}%`
                      : "—"}
                  </strong>

                </div>

              </div>


              <div className="stat-card">

                <div className="stat-icon blue">
                  <FileSearch size={21} />
                </div>

                <div>

                  <span>
                    Required Match
                  </span>

                  <strong>

                    {topCandidate
                      ? `${topCandidate.required_matched}/${topCandidate.required_total}`
                      : "—"}

                  </strong>

                </div>

              </div>


              <div className="stat-card">

                <div className="stat-icon orange">
                  <BriefcaseBusiness
                    size={21}
                  />
                </div>

                <div>

                  <span>Job Position</span>

                  <strong className="job-stat">

                    {job?.job_title
                      ? job.job_title.replace(
                          "Machine Learning ",
                          "ML "
                        )
                      : "ML Intern"}

                  </strong>

                </div>

              </div>


            </section>


            {topCandidate && (

              <section className="top-candidate">

                <div className="trophy-circle">
                  <Trophy size={25} />
                </div>


                <div className="top-info">

                  <span>
                    TOP CANDIDATE
                  </span>

                  <h2>
                    {
                      topCandidate
                        .candidate
                        ?.candidate_name
                    }
                  </h2>

                  <p>
                    {topCandidate.cv_filename}
                    {" · "}
                    {
                      topCandidate.required_matched
                    }
                    /
                    {
                      topCandidate.required_total
                    }
                    {" required skills matched"}
                  </p>

                </div>


                <div className="top-score">

                  <span>
                    Smart Score
                  </span>

                  <strong>
                    {Number(
                      topCandidate.smart_score
                    ).toFixed(2)}
                    %
                  </strong>

                </div>


                <button
                  className="view-btn"
                  onClick={() =>
                    setSelectedCandidate(
                      topCandidate
                    )
                  }
                >

                  View Profile

                  <ChevronRight
                    size={17}
                  />

                </button>

              </section>

            )}


            <section className="ranking-card">

              <div className="section-header">

                <div>

                  <h2>
                    Candidate Ranking
                  </h2>

                  <p>
                    Candidates ranked by
                    Smart Match Score
                  </p>

                </div>


                <button
                  className={
                    showTopOnly
                      ? "filter-btn active"
                      : "filter-btn"
                  }
                  onClick={() =>
                    setShowTopOnly((prev) => !prev)
                  }
                >
                  {showTopOnly
                    ? "Top Matches (≥50%)"
                    : "All Candidates"}
                </button>

              </div>


              <div className="table">


                <div className="table-head">

                  <span>#</span>

                  <span>
                    CANDIDATE
                  </span>

                  <span>
                    SMART SCORE
                  </span>

                  <span>
                    REQUIRED
                  </span>

                  <span>
                    PREFERRED
                  </span>

                  <span></span>

                </div>


                {visibleCandidates.length === 0 ? (

                  <div className="empty-state">

                    <FileSearch
                      size={35}
                    />

                    <div>
                      Upload CVs and click{" "}
                      <strong>
                        Analyze Candidates
                      </strong>
                    </div>

                  </div>

                ) : (

                  visibleCandidates.map(
                    (candidate, index) => (

                      <div
                        className="table-row"
                        key={
                          candidate.cv_filename ||
                          index
                        }
                      >

                        <div className="rank">

                          {candidate.rank === 1
                            ? (
                              <Trophy
                                size={18}
                              />
                            )
                            : candidate.rank}

                        </div>


                        <div className="candidate">

                          <div className="avatar">

                            {candidate
                              .candidate
                              ?.candidate_name
                              ?.charAt(0)
                              ?.toUpperCase() ||
                              "?"}

                          </div>


                          <div>

                            <strong>

                              {candidate
                                .candidate
                                ?.candidate_name ||
                                "Unknown Candidate"}

                            </strong>

                            <small>
                              {
                                candidate.cv_filename
                              }
                            </small>

                          </div>

                        </div>


                        <ScoreBar
                          score={
                            candidate.smart_score
                          }
                        />


                        <div className="match">

                          {
                            candidate.required_matched
                          }
                          /
                          {
                            candidate.required_total
                          }

                        </div>


                        <div className="match">

                          {
                            candidate.preferred_matched
                          }
                          /
                          {
                            candidate.preferred_total
                          }

                        </div>


                        <button
                          className="details-btn"
                          onClick={() =>
                            setSelectedCandidate(
                              candidate
                            )
                          }
                        >

                          Details

                          <ChevronRight
                            size={15}
                          />

                        </button>

                      </div>

                    )
                  )

                )}

              </div>

            </section>

          </div>

        )}


        {/* ====================================================
            JOBS SECTION
        ==================================================== */}

        {activeSection === "jobs" && (

          <div>

            <header className="header">

              <div>
                <h1>Job Details</h1>
                <p>What this position is asking for</p>
              </div>

            </header>


            {!job ? (

              <div className="ranking-card">

                <div className="empty-state">

                  <BriefcaseBusiness size={35} />

                  <div>
                    No job analyzed yet — go to{" "}
                    <strong>Dashboard</strong> and click{" "}
                    <strong>Analyze Candidates</strong>.
                  </div>

                </div>

              </div>

            ) : (

              <div className="ranking-card">

                <div className="section-header">

                  <div>

                    <h2>{job.job_title}</h2>

                    <p>
                      {job.years_of_experience_required > 0
                        ? `${job.years_of_experience_required}+ years of experience expected`
                        : "No minimum experience specified"}
                    </p>

                  </div>

                </div>


                <h3 style={{ marginTop: "10px" }}>
                  Required Skills
                </h3>

                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "8px",
                    marginTop: "10px"
                  }}
                >
                  {job.required_skills.map((skill, i) => (
                    <span key={i} className="badge badge-exact">
                      {skill}
                    </span>
                  ))}
                </div>


                <h3 style={{ marginTop: "20px" }}>
                  Preferred Skills
                </h3>

                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "8px",
                    marginTop: "10px"
                  }}
                >
                  {job.preferred_skills.map((skill, i) => (
                    <span key={i} className="badge badge-related">
                      {skill}
                    </span>
                  ))}
                </div>


                <h3 style={{ marginTop: "20px" }}>
                  Responsibilities
                </h3>

                <ul style={{ marginTop: "10px", color: "var(--text-dim)" }}>
                  {job.responsibilities.map((item, i) => (
                    <li key={i} style={{ marginBottom: "6px" }}>
                      {item}
                    </li>
                  ))}
                </ul>

              </div>

            )}

          </div>

        )}


        {/* ====================================================
            CANDIDATES SECTION
        ==================================================== */}

        {activeSection === "candidates" && (

          <div>

            <header className="header">

              <div>
                <h1>Candidates</h1>
                <p>Everyone screened for the current job</p>
              </div>

            </header>


            <section className="ranking-card">

              <div className="section-header">

                <div>
                  <h2>All Candidates</h2>
                  <p>{candidates.length} candidate(s) screened</p>
                </div>


                <button
                  className={
                    showTopOnly
                      ? "filter-btn active"
                      : "filter-btn"
                  }
                  onClick={() =>
                    setShowTopOnly((prev) => !prev)
                  }
                >
                  {showTopOnly
                    ? "Top Matches (≥50%)"
                    : "All Candidates"}
                </button>

              </div>


              <div className="table">

                <div className="table-head">
                  <span>#</span>
                  <span>CANDIDATE</span>
                  <span>SMART SCORE</span>
                  <span>REQUIRED</span>
                  <span>PREFERRED</span>
                  <span></span>
                </div>

                {visibleCandidates.length === 0 ? (

                  <div className="empty-state">
                    <FileSearch size={35} />
                    <div>
                      No candidates yet — analyze CVs from the{" "}
                      <strong>Dashboard</strong>.
                    </div>
                  </div>

                ) : (

                  visibleCandidates.map((candidate, index) => (

                    <div
                      className="table-row"
                      key={candidate.cv_filename || index}
                    >

                      <div className="rank">
                        {candidate.rank === 1 ? (
                          <Trophy size={18} />
                        ) : (
                          candidate.rank
                        )}
                      </div>

                      <div className="candidate">
                        <div className="avatar">
                          {candidate.candidate?.candidate_name
                            ?.charAt(0)
                            ?.toUpperCase() || "?"}
                        </div>

                        <div>
                          <strong>
                            {candidate.candidate?.candidate_name ||
                              "Unknown Candidate"}
                          </strong>
                          <small>{candidate.cv_filename}</small>
                        </div>
                      </div>

                      <ScoreBar score={candidate.smart_score} />

                      <div className="match">
                        {candidate.required_matched}/
                        {candidate.required_total}
                      </div>

                      <div className="match">
                        {candidate.preferred_matched}/
                        {candidate.preferred_total}
                      </div>

                      <button
                        className="details-btn"
                        onClick={() =>
                          setSelectedCandidate(candidate)
                        }
                      >
                        Details
                        <ChevronRight size={15} />
                      </button>

                    </div>

                  ))

                )}

              </div>

            </section>

          </div>

        )}


        {/* ====================================================
            SETTINGS SECTION
        ==================================================== */}

                {activeSection === "settings" && (

          <div>

            <header className="header">

              <div>
                <h1>Settings</h1>
                <p>Adjust how the dashboard looks and behaves</p>
              </div>

            </header>


            <div className="settings-panel">

              <div className="settings-row">

                <div className="settings-row-info">

                  <div className="settings-row-icon">
                    <Settings size={18} />
                  </div>

                  <div className="settings-row-text">
                    <strong>Dark theme</strong>
                    <small>Switch to the indigo dark palette</small>
                  </div>

                </div>

                <button
                  type="button"
                  className={
                    darkMode ? "toggle on" : "toggle"
                  }
                  onClick={() =>
                    setDarkMode((prev) => !prev)
                  }
                >
                  <span className="toggle-knob" />
                </button>

              </div>


              <div className="settings-row">

                <div className="settings-row-info">

                  <div className="settings-row-icon">
                    <Trophy size={18} />
                  </div>

                  <div className="settings-row-text">
                    <strong>Show only top matches by default</strong>
                    <small>Filter candidates below 50% on load</small>
                  </div>

                </div>

                <button
                  type="button"
                  className={
                    showTopOnly ? "toggle on" : "toggle"
                  }
                  onClick={() =>
                    setShowTopOnly((prev) => !prev)
                  }
                >
                  <span className="toggle-knob" />
                </button>

              </div>

            </div>

          </div>

        )}


        {/* ====================================================
            DETAILS
        ==================================================== */}

        {selectedCandidate && (

          <section
            className="ranking-card"
            style={{
              marginTop: "20px",
              marginBottom: "40px"
            }}
          >

            <div className="section-header">

              <div>

                <h2>
                  Candidate Details
                </h2>

                <p>
                  {
                    selectedCandidate
                      .candidate
                      ?.candidate_name
                  }
                </p>

              </div>


              <button
                className="filter-btn"
                onClick={() =>
                  setSelectedCandidate(
                    null
                  )
                }
              >
                Close
              </button>

            </div>


            <div
              style={{
                padding: "20px"
              }}
            >

              <h3>

                Smart Score:{" "}

                <span className="score-highlight">
                  {Number(
                    selectedCandidate.smart_score
                  ).toFixed(2)}
                  %
                </span>

              </h3>


              <h3
                style={{
                  marginTop: "20px"
                }}
              >
                Required Skills
              </h3>


              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "8px",
                  marginTop: "10px"
                }}
              >

                {selectedCandidate
                  .semantic_matching
                  ?.required
                  ?.map(
                    (result, index) => (

                      <SkillBadge
                        key={index}
                        result={result}
                        showTilde
                      />

                    )
                  )}

              </div>


              <h3
                style={{
                  marginTop: "20px"
                }}
              >
                Preferred Skills
              </h3>


              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "8px",
                  marginTop: "10px"
                }}
              >

                {selectedCandidate
                  .semantic_matching
                  ?.preferred
                  ?.map(
                    (result, index) => (

                      <SkillBadge
                        key={index}
                        result={result}
                      />

                    )
                  )}

              </div>


              {selectedCandidate
                .recommendations && (

                <div
                  style={{
                    marginTop: "25px"
                  }}
                >

                  <h3>
                    AI Recommendations
                  </h3>

                  <p
                    style={{
                      marginTop: "10px",
                      color: "var(--text-dim)"
                    }}
                  >
                    {
                      selectedCandidate
                        .recommendations
                        .summary
                    }
                  </p>

                </div>

              )}

            </div>

          </section>

        )}

      </main>

    </div>
  );
}


export default App;