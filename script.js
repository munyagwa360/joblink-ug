const seedJobs = [
  {
    id: "1",
    title: "Frontend Developer",
    company: "Kampala Digital Studio",
    location: "Kampala",
    category: "IT & Software",
    type: "Full-time",
    experience: "Mid-Level",
    workMode: "Hybrid",
    salary: "UGX 2.5M - 4M",
    salaryMin: 2500000,
    salaryMax: 4000000,
    postedAt: "2026-06-10",
    skills: ["JavaScript", "React", "CSS"],
    status: "Live",
    applicants: 18,
    description:
      "Build mobile-first web products for local businesses and support the team with React interfaces."
  },
  {
    id: "2",
    title: "Customer Support Associate",
    company: "Pearl Logistics",
    location: "Entebbe",
    category: "Customer Service",
    type: "Part-time",
    experience: "Entry",
    workMode: "On-site",
    salary: "UGX 900K - 1.4M",
    salaryMin: 900000,
    salaryMax: 1400000,
    postedAt: "2026-06-08",
    skills: ["Communication", "CRM", "Problem solving"],
    status: "Pending",
    applicants: 7,
    description:
      "Handle customer calls, track deliveries, and resolve client issues across daily operations."
  },
  {
    id: "3",
    title: "Solar Installation Technician",
    company: "Nile Energy",
    location: "Mbarara",
    category: "Construction",
    type: "Contract",
    experience: "Mid-Level",
    workMode: "On-site",
    salary: "UGX 120K / day",
    salaryMin: 2400000,
    salaryMax: 3200000,
    postedAt: "2026-06-06",
    skills: ["Electrical wiring", "Solar panels", "Field service"],
    status: "Live",
    applicants: 24,
    description:
      "Install and maintain solar home systems for residential and SME customers in western Uganda."
  },
  {
    id: "4",
    title: "Accounts Assistant",
    company: "Lakeview Foods",
    location: "Jinja",
    category: "Finance",
    type: "Full-time",
    experience: "Entry",
    workMode: "On-site",
    salary: "UGX 1M - 1.6M",
    salaryMin: 1000000,
    salaryMax: 1600000,
    postedAt: "2026-06-04",
    skills: ["Bookkeeping", "Excel", "Invoicing"],
    status: "Live",
    applicants: 11,
    description:
      "Support invoicing, petty cash reconciliation, supplier records, and weekly finance reporting."
  },
  {
    id: "5",
    title: "Python Developer",
    company: "XYZ Solutions",
    location: "Entebbe",
    category: "IT & Software",
    type: "Contract",
    experience: "Senior",
    workMode: "Remote",
    salary: "UGX 2M - 3.5M",
    salaryMin: 2000000,
    salaryMax: 3500000,
    postedAt: "2026-06-11",
    skills: ["Python", "FastAPI", "PostgreSQL"],
    status: "Live",
    applicants: 9,
    description:
      "Build APIs, database models, and integrations for a growing jobs and payments platform."
  },
  {
    id: "6",
    title: "Primary Teacher",
    company: "Bright Future School",
    location: "Gulu",
    category: "Education",
    type: "Full-time",
    experience: "Entry",
    workMode: "On-site",
    salary: "UGX 800K - 1.2M",
    salaryMin: 800000,
    salaryMax: 1200000,
    postedAt: "2026-06-09",
    skills: ["Lesson planning", "Classroom management", "English"],
    status: "Live",
    applicants: 16,
    description:
      "Teach upper primary learners, prepare schemes of work, and support assessment reporting."
  },
  {
    id: "7",
    title: "Delivery Driver",
    company: "Swift Parcels UG",
    location: "Kampala",
    category: "Transport",
    type: "Full-time",
    experience: "Mid-Level",
    workMode: "On-site",
    salary: "UGX 1.1M - 1.7M",
    salaryMin: 1100000,
    salaryMax: 1700000,
    postedAt: "2026-06-07",
    skills: ["Driving", "Route planning", "Customer handling"],
    status: "Live",
    applicants: 21,
    description:
      "Deliver parcels around greater Kampala and maintain accurate delivery records."
  },
  {
    id: "8",
    title: "Registered Nurse",
    company: "CarePlus Clinic",
    location: "Mbarara",
    category: "Healthcare",
    type: "Full-time",
    experience: "Senior",
    workMode: "On-site",
    salary: "UGX 1.8M - 2.6M",
    salaryMin: 1800000,
    salaryMax: 2600000,
    postedAt: "2026-05-25",
    skills: ["Patient care", "Triage", "Clinical records"],
    status: "Live",
    applicants: 13,
    description:
      "Provide outpatient care, support clinical procedures, and coordinate patient follow-up."
  }
];

const reports = [
  "Employer verification request: Pearl Logistics",
  "Duplicate listing flagged: Sales Agent",
  "Applicant complaint awaiting review"
];

const API_BASE_URL = window.JOBLINK_API_URL || "http://127.0.0.1:8000";

let jobs = load("joblink.jobs", seedJobs).map(normalizeJob);
let saved = load("joblink.saved", []);
let applications = load("joblink.applications", []);
let activeRole = "seeker";
let apiOnline = false;
let authState = load("joblink.auth", null);

const titles = {
  seeker: ["Job seeker dashboard", "Find your next role"],
  employer: ["Employer dashboard", "Post and manage jobs"],
  admin: ["Admin dashboard", "Review platform activity"]
};

const roleTabs = document.querySelectorAll(".role-tab");
const views = document.querySelectorAll(".view");
const viewEyebrow = document.querySelector("#viewEyebrow");
const viewTitle = document.querySelector("#viewTitle");
const jobList = document.querySelector("#jobList");
const jobSearchForm = document.querySelector("#jobSearchForm");
const jobSearch = document.querySelector("#jobSearch");
const locationFilter = document.querySelector("#locationFilter");
const categoryFilter = document.querySelector("#categoryFilter");
const jobTypeFilter = document.querySelector("#jobTypeFilter");
const experienceFilter = document.querySelector("#experienceFilter");
const salaryFilter = document.querySelector("#salaryFilter");
const dateFilter = document.querySelector("#dateFilter");
const workModeFilter = document.querySelector("#workModeFilter");
const sortFilter = document.querySelector("#sortFilter");
const jobDialog = document.querySelector("#jobDialog");
const jobDetails = document.querySelector("#jobDetails");
const actionDialog = document.querySelector("#actionDialog");
const actionDetails = document.querySelector("#actionDetails");
const toast = document.querySelector("#toast");
const authDialog = document.querySelector("#authDialog");
const authDetails = document.querySelector("#authDetails");
const authButton = document.querySelector("#authButton");
const advantages = [
  {
    label: "Advantage 01",
    title: "Every job. One platform.",
    text: "See relevant jobs in one place and get notified when new opportunities appear."
  },
  {
    label: "Advantage 02",
    title: "Win more interviews",
    text: "Build a standout CV with clear, tailored guidance that helps employers notice you."
  },
  {
    label: "Advantage 03",
    title: "Find hidden opportunities",
    text: "Match with recruiters and employers opening doors to roles that may not be widely listed."
  },
  {
    label: "Advantage 04",
    title: "Better cover letters",
    text: "Create focused application notes that speak directly to each role you want."
  },
  {
    label: "Advantage 05",
    title: "Learn, apply, get hired.",
    text: "Access career tips, guides, and practical templates as you move through your job search."
  }
];
let activeAdvantage = 0;
let advantageTimer;

roleTabs.forEach((tab) => {
  tab.addEventListener("click", () => setRole(tab.dataset.role));
});

document.querySelector("#closeDialog").addEventListener("click", () => jobDialog.close());
document.querySelector("#closeActionDialog").addEventListener("click", () => actionDialog.close());
document.querySelector("#closeAuthDialog").addEventListener("click", () => authDialog.close());
authButton.addEventListener("click", () => {
  if (authState) {
    signOut();
    return;
  }
  openAuthDialog();
});
document.querySelector("#resetDemo").addEventListener("click", resetDemo);
document.querySelector("#jobForm").addEventListener("submit", submitJob);
document.querySelector("#clearFilters").addEventListener("click", clearFilters);
document.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-action]");
  if (!trigger) {
    return;
  }

  event.preventDefault();
  openAction(trigger.dataset.action);
});
document.querySelector("#prevAdvantage")?.addEventListener("click", () => {
  changeAdvantage(-1);
  restartAdvantageTimer();
});
document.querySelector("#nextAdvantage")?.addEventListener("click", () => {
  changeAdvantage(1);
  restartAdvantageTimer();
});
document.querySelectorAll(".quick-chip").forEach((chip) => {
  chip.addEventListener("click", () => applyQuickFilter(chip));
});
jobSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  render();
});
jobSearch.addEventListener("input", render);
[
  locationFilter,
  categoryFilter,
  jobTypeFilter,
  experienceFilter,
  salaryFilter,
  dateFilter,
  workModeFilter,
  sortFilter
].forEach((filter) => filter.addEventListener("change", render));

initializeApp();
startAdvantageTimer();

async function initializeApp() {
  render();
  await loadJobsFromApi();
}

function changeAdvantage(direction) {
  activeAdvantage = (activeAdvantage + direction + advantages.length) % advantages.length;
  const advantage = advantages[activeAdvantage];
  const art = document.querySelector("#advantageArt");

  document.querySelector("#advantageLabel").textContent = advantage.label;
  document.querySelector("#advantageTitle").textContent = advantage.title;
  document.querySelector("#advantageText").textContent = advantage.text;
  art.className = `advantage-art advantage-art-${activeAdvantage + 1}`;
}

function startAdvantageTimer() {
  advantageTimer = window.setInterval(() => changeAdvantage(1), 2000);
}

function restartAdvantageTimer() {
  window.clearInterval(advantageTimer);
  startAdvantageTimer();
}

function setRole(role) {
  if (role === "employer" && !hasRole("employer", "admin")) {
    showToast("Sign in as an employer to manage job listings.");
    openAuthDialog("login");
    return;
  }

  if (role === "admin" && !hasRole("admin")) {
    showToast("Sign in as an admin to open platform controls.");
    openAuthDialog("login");
    return;
  }

  activeRole = role;
  roleTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.role === role));
  views.forEach((view) => view.classList.toggle("active", view.id === `${role}View`));
  viewEyebrow.textContent = titles[role][0];
  viewTitle.textContent = titles[role][1];
  render();
  loadJobsFromApi();
}

function render() {
  renderAuthButton();
  renderJobs();
  renderEmployer();
  renderAdmin();
  saveState();
}

async function loadJobsFromApi() {
  try {
    const endpoint = hasRole("admin")
      ? "/jobs?status=all"
      : hasRole("employer")
        ? "/employers/listings"
        : "/jobs";
    const apiJobs = await apiRequest(endpoint);
    jobs = apiJobs.map(normalizeJob);
    apiOnline = true;
    render();
  } catch (error) {
    apiOnline = false;
    if (error.status === 401 || error.status === 403) {
      showToast(error.message);
    }
  }
}

async function apiRequest(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (authState?.token) {
    headers.Authorization = `Bearer ${authState.token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = `API request failed with ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      // Keep the generic message when the response is not JSON.
    }
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function hasRole(...roles) {
  return Boolean(authState?.user && roles.includes(authState.user.role));
}

function renderAuthButton() {
  authButton.textContent = authState ? "Sign out" : "Sign in";
}

function openAuthDialog(mode = "login") {
  authDetails.innerHTML = `
    <form class="auth-form" id="authForm">
      <p class="eyebrow">JobLink UG account</p>
      <h2 id="authTitle">${mode === "register" ? "Create your account" : "Sign in"}</h2>
      <p id="authIntro">${
        mode === "register"
          ? "Create a seeker or employer account to use protected actions."
          : "Sign in to apply for jobs, post roles, or manage the platform."
      }</p>
      <label>
        Account action
        <select id="authMode" name="mode">
          <option value="login" ${mode === "login" ? "selected" : ""}>Sign in</option>
          <option value="register" ${mode === "register" ? "selected" : ""}>Create account</option>
        </select>
      </label>
      <label id="authRoleField" ${mode === "login" ? "hidden" : ""}>
        Account type
        <select name="role">
          <option value="seeker">Job seeker</option>
          <option value="employer">Employer</option>
        </select>
      </label>
      <label>
        Email address
        <input name="email" type="email" autocomplete="email" required placeholder="you@example.com" />
      </label>
      <label>
        Password
        <input name="password" type="password" autocomplete="current-password" required minlength="8" placeholder="At least 8 characters" />
      </label>
      <p class="auth-message" id="authMessage">Admin accounts are created securely by the platform owner.</p>
      <button class="primary-button" id="authSubmit" type="submit">${
        mode === "register" ? "Create account" : "Sign in"
      }</button>
    </form>
  `;

  const form = authDetails.querySelector("#authForm");
  const modeSelect = authDetails.querySelector("#authMode");
  modeSelect.addEventListener("change", () => updateAuthMode(modeSelect.value));
  form.addEventListener("submit", submitAuth);
  authDialog.showModal();
}

function updateAuthMode(mode) {
  const isRegistering = mode === "register";
  authDetails.querySelector("#authRoleField").hidden = !isRegistering;
  authDetails.querySelector("#authTitle").textContent = isRegistering
    ? "Create your account"
    : "Sign in";
  authDetails.querySelector("#authIntro").textContent = isRegistering
    ? "Create a seeker or employer account to use protected actions."
    : "Sign in to apply for jobs, post roles, or manage the platform.";
  authDetails.querySelector("#authSubmit").textContent = isRegistering
    ? "Create account"
    : "Sign in";
}

async function submitAuth(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const mode = form.get("mode");
  const payload = {
    email: form.get("email").trim(),
    password: form.get("password")
  };

  if (mode === "register") {
    payload.role = form.get("role");
  }

  const submitButton = authDetails.querySelector("#authSubmit");
  submitButton.disabled = true;
  submitButton.textContent = mode === "register" ? "Creating account..." : "Signing in...";

  try {
    const response = await apiRequest(mode === "register" ? "/auth/register" : "/auth/login", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    authState = { token: response.access_token, user: response.user };
    applications = [];
    localStorage.setItem("joblink.auth", JSON.stringify(authState));
    authDialog.close();
    showToast(`Signed in as ${response.user.role}.`);
    setRole(response.user.role);
  } catch (error) {
    authDetails.querySelector("#authMessage").textContent = error.message;
    submitButton.disabled = false;
    updateAuthMode(mode);
  }
}

function signOut() {
  authState = null;
  localStorage.removeItem("joblink.auth");
  activeRole = "seeker";
  roleTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.role === "seeker"));
  views.forEach((view) => view.classList.toggle("active", view.id === "seekerView"));
  viewEyebrow.textContent = titles.seeker[0];
  viewTitle.textContent = titles.seeker[1];
  showToast("Signed out.");
  render();
  loadJobsFromApi();
}

function renderJobs() {
  const query = jobSearch.value.trim().toLowerCase();
  const filters = {
    location: locationFilter.value,
    category: categoryFilter.value,
    type: jobTypeFilter.value,
    experience: experienceFilter.value,
    salary: salaryFilter.value,
    date: dateFilter.value,
    workMode: workModeFilter.value,
    sort: sortFilter.value
  };
  const liveJobs = jobs.filter((job) => job.status === "Live").slice(0, 3);
  const filtered = liveJobs
    .filter((job) => matchesSearch(job, query))
    .filter((job) => matchesChoice(job.location, filters.location))
    .filter((job) => matchesChoice(job.category, filters.category))
    .filter((job) => matchesChoice(job.type, filters.type))
    .filter((job) => matchesChoice(job.experience, filters.experience))
    .filter((job) => matchesChoice(job.workMode, filters.workMode))
    .filter((job) => matchesSalary(job, filters.salary))
    .filter((job) => matchesDate(job, filters.date))
    .sort((first, second) => sortJobs(first, second, filters.sort));

  document.querySelector("#liveCount").textContent = liveJobs.length;
  document.querySelector("#savedCount").textContent = saved.length;
  document.querySelector("#applicationCount").textContent = applications.length;
  document.querySelector("#resultsCount").textContent = `Showing ${filtered.length} ${
    filtered.length === 1 ? "job" : "jobs"
  }`;

  jobList.innerHTML =
    filtered.length === 0
      ? `<p class="empty-state">No jobs match your search.</p>`
      : `${filtered.map(jobCard).join("")}${jobAlertCard(filtered.length)}`;

  jobList.querySelectorAll("[data-open]").forEach((button) => {
    button.addEventListener("click", () => openJob(button.dataset.open));
  });
  jobList.querySelectorAll("[data-save]").forEach((button) => {
    button.addEventListener("click", () => toggleSave(button.dataset.save));
  });
  jobList.querySelectorAll("[data-apply]").forEach((button) => {
    button.addEventListener("click", () => applyJob(button.dataset.apply));
  });
  jobList.querySelector("[data-alert-signup]")?.addEventListener("click", () => {
    showToast("Search saved. Job alerts are ready for this filter.");
  });
}

function normalizeJob(job) {
  return {
    category: "General",
    experience: "Entry",
    workMode: "On-site",
    salaryMin: 0,
    salaryMax: 0,
    postedAt: "2026-06-01",
    skills: [],
    ...job,
    id: String(job.id),
    workMode: job.workMode || job.work_mode || "On-site",
    salaryMin: job.salaryMin ?? job.salary_min ?? 0,
    salaryMax: job.salaryMax ?? job.salary_max ?? 0,
    postedAt: job.postedAt || job.posted_at || "2026-06-01",
    status: job.status || "Pending",
    applicants: job.applicants || 0,
    skills: job.skills || []
  };
}

function jobCard(job) {
  const isSaved = saved.includes(job.id);
  return `
    <article class="job-card">
      <div class="card-top">
        <div class="company-mark">${escapeHtml(job.company.charAt(0))}</div>
        <button class="save-button" data-save="${job.id}" type="button" aria-label="Save job">
          ${isSaved ? "★" : "☆"}
        </button>
      </div>
      <div>
        <h3>${escapeHtml(job.title)}</h3>
        <p class="company">${escapeHtml(job.company)}</p>
      </div>
      <div class="badge-row">
        <span class="verified-badge">Verified</span>
        <span class="verified-badge">${escapeHtml(job.workMode)}</span>
      </div>
      <div class="tag-row">
        <span class="tag">${escapeHtml(job.location)}</span>
        <span class="tag">${escapeHtml(job.category)}</span>
        <span class="tag">${escapeHtml(job.type)}</span>
        <span class="tag">${escapeHtml(job.experience)}</span>
        <span class="tag">${escapeHtml(job.workMode)}</span>
      </div>
      <p class="meta">Skills: ${escapeHtml(job.skills.join(", "))}</p>
      <p class="meta">Posted ${formatDate(job.postedAt)}</p>
      <p class="salary">${escapeHtml(job.salary || "Salary not listed")}</p>
      <p class="description">${escapeHtml(job.description)}</p>
      <div class="card-actions">
        <button class="primary-button" data-apply="${job.id}" type="button">Apply</button>
        <button class="secondary-button" data-open="${job.id}" type="button">Details</button>
      </div>
    </article>
  `;
}

function jobAlertCard(count) {
  return `
    <aside class="alert-card" aria-label="Job alerts">
      <p class="eyebrow">Job alerts</p>
      <h3>Get matched when new roles are posted</h3>
      <p>
        Save this search and JobLink UG can notify you when similar ${count === 1 ? "job is" : "jobs are"}
        added.
      </p>
      <div class="alert-list">
        <span>New listings first</span>
        <span>Location-based matches</span>
        <span>Remote and on-site roles</span>
      </div>
      <button class="primary-button" type="button" data-alert-signup>Save search</button>
      <div class="mini-company-panel">
        <p>Companies hiring now</p>
        <div>
          <span>KD</span>
          <span>NE</span>
          <span>CP</span>
          <span>BF</span>
        </div>
      </div>
    </aside>
  `;
}

function renderEmployer() {
  const target = document.querySelector("#employerListings");
  target.innerHTML = jobs
    .map(
      (job) => `
        <div class="list-row">
          <div>
            <strong>${escapeHtml(job.title)}</strong>
            <p>${escapeHtml(job.company)} · ${job.applicants} applicants</p>
          </div>
          <div class="listing-actions">
            <span class="status-pill ${job.status === "Live" ? "status-live" : "status-pending"}">
              ${job.status}
            </span>
            <button class="mini-action" data-action="job-${job.id}" type="button">View</button>
          </div>
        </div>
      `
    )
    .join("");
}

function renderAdmin() {
  const pending = jobs.filter((job) => job.status === "Pending");
  const active = jobs.filter((job) => job.status === "Live");
  document.querySelector("#adminJobs").textContent = jobs.length;
  document.querySelector("#adminActiveJobs").textContent = active.length;
  document.querySelector("#adminPending").textContent = pending.length;
  document.querySelector("#adminUsers").textContent = "1,248";
  document.querySelector("#adminApplications").textContent = jobs.reduce(
    (total, job) => total + job.applicants,
    0
  );

  const pendingJobs = document.querySelector("#pendingJobs");
  pendingJobs.innerHTML =
    pending.length === 0
      ? `<p class="empty-state">No jobs are waiting for approval.</p>`
      : pending
          .map(
            (job) => `
              <div class="list-row">
                <div>
                  <strong>${escapeHtml(job.title)}</strong>
                  <p>${escapeHtml(job.company)} · ${escapeHtml(job.location)}</p>
                </div>
                <button class="primary-button" data-approve="${job.id}" type="button">Approve</button>
              </div>
            `
          )
          .join("");

  pendingJobs.querySelectorAll("[data-approve]").forEach((button) => {
    button.addEventListener("click", () => approveJob(button.dataset.approve));
  });

  document.querySelector("#reportsList").innerHTML = reports
    .map(
      (report) => `
        <div class="list-row">
          <div>
            <strong>Needs review</strong>
            <p>${escapeHtml(report)}</p>
          </div>
        </div>
      `
    )
    .join("");
}

async function submitJob(event) {
  event.preventDefault();

  if (!hasRole("employer", "admin")) {
    showToast("Sign in as an employer to submit a job.");
    openAuthDialog("login");
    return;
  }

  const form = new FormData(event.currentTarget);
  const job = {
    id: String(Date.now()),
    title: form.get("title").trim(),
    company: form.get("company").trim(),
    location: form.get("location").trim(),
    category: form.get("category"),
    type: form.get("type"),
    experience: form.get("experience"),
    workMode: form.get("workMode"),
    salary: form.get("salary").trim(),
    description: form.get("description").trim() || "No description added yet.",
    salaryMin: parseSalaryMin(form.get("salary")),
    salaryMax: parseSalaryMax(form.get("salary")),
    postedAt: new Date().toISOString().slice(0, 10),
    skills: form
      .get("skills")
      .split(",")
      .map((skill) => skill.trim())
      .filter(Boolean),
    status: "Pending",
    applicants: 0
  };

  if (!job.title || !job.company || !job.location) {
    showToast("Add a title, company, and location.");
    return;
  }

  if (apiOnline) {
    try {
      const createdJob = await apiRequest("/jobs", {
        method: "POST",
        body: JSON.stringify(toApiJob(job))
      });
      jobs = [normalizeJob(createdJob), ...jobs];
    } catch {
      apiOnline = false;
      jobs = [job, ...jobs];
      showToast("API unavailable. Job saved in demo mode.");
      render();
      return;
    }
  } else {
    jobs = [job, ...jobs];
  }

if (event.target && typeof event.target.reset === "function") {
  event.target.reset();
}
  showToast("Job submitted for admin approval.");
  render();
}

async function approveJob(id) {
  if (!hasRole("admin")) {
    showToast("Sign in as an admin to approve jobs.");
    openAuthDialog("login");
    return;
  }

  if (apiOnline) {
    try {
      const approvedJob = await apiRequest(`/jobs/${id}/approve`, { method: "PATCH" });
      jobs = jobs.map((job) => (job.id === id ? normalizeJob(approvedJob) : job));
    } catch {
      apiOnline = false;
      jobs = jobs.map((job) => (job.id === id ? { ...job, status: "Live" } : job));
      showToast("API unavailable. Approval saved in demo mode.");
      render();
      return;
    }
  } else {
    jobs = jobs.map((job) => (job.id === id ? { ...job, status: "Live" } : job));
  }

  showToast("Job approved.");
  render();
}

function toggleSave(id) {
  saved = saved.includes(id) ? saved.filter((item) => item !== id) : [...saved, id];
  render();
}

async function applyJob(id) {
  if (!hasRole("seeker")) {
    showToast("Sign in as a job seeker to apply.");
    openAuthDialog("login");
    return;
  }

  const alreadyApplied = applications.includes(id);

  if (!alreadyApplied) {
    applications = [...applications, id];
  }

  const job = jobs.find((item) => item.id === id);

  if (!job) {
    showToast("Job not found.");
    return;
  }

  if (apiOnline && !alreadyApplied) {
    try {
      const application = await apiRequest(`/jobs/${id}/applications`, {
        method: "POST",
        body: JSON.stringify({
          note: "Application submitted from the JobLink UG website."
        })
      });
      jobs = jobs.map((item) =>
        item.id === id ? { ...item, applicants: item.applicants + 1 } : item
      );
      applications = [...new Set([...applications, application.job_id])];
    } catch {
      apiOnline = false;
      showToast("API unavailable. Application saved in demo mode.");
      render();
      return;
    }
  }

  showToast(`Application sent for ${job.title}.`);
  render();
}

function toApiJob(job) {
  return {
    title: job.title,
    company: job.company,
    location: job.location,
    category: job.category,
    type: job.type,
    experience: job.experience,
    work_mode: job.workMode,
    salary: job.salary,
    salary_min: job.salaryMin,
    salary_max: job.salaryMax,
    posted_at: job.postedAt,
    skills: job.skills,
    description: job.description
  };
}

function openJob(id) {
  const job = jobs.find((item) => item.id === id);
  jobDetails.innerHTML = `
    <article class="dialog-job">
      <div class="company-mark">${escapeHtml(job.company.charAt(0))}</div>
      <h2>${escapeHtml(job.title)}</h2>
      <p class="company">${escapeHtml(job.company)}</p>
      <div class="tag-row">
        <span class="tag">${escapeHtml(job.location)}</span>
        <span class="tag">${escapeHtml(job.category)}</span>
        <span class="tag">${escapeHtml(job.type)}</span>
        <span class="tag">${escapeHtml(job.experience)}</span>
        <span class="tag">${escapeHtml(job.workMode)}</span>
      </div>
      <p class="meta">Skills: ${escapeHtml(job.skills.join(", ") || "Not listed")}</p>
      <p class="meta">Posted ${formatDate(job.postedAt)}</p>
      <p class="salary">${escapeHtml(job.salary || "Salary not listed")}</p>
      <p class="description">${escapeHtml(job.description)}</p>
      <button class="primary-button" data-dialog-apply="${job.id}" type="button">Apply now</button>
    </article>
  `;
  jobDetails.querySelector("[data-dialog-apply]").addEventListener("click", () => {
    applyJob(job.id);
    jobDialog.close();
  });
  jobDialog.showModal();
}

function openAction(action) {
  const jobMatch = action.match(/^job-(.+)$/);
  if (jobMatch) {
    const job = jobs.find((item) => item.id === jobMatch[1]);
    openActionDialog(jobListingTemplate(job));
    return;
  }

  const templates = {
    applicants: applicantsTemplate(),
    "candidate-database": candidateDatabaseTemplate(),
    "candidate-graduates": candidateTemplate(
      "Recent graduates",
      "Entry-level talent with fresh training in business, IT, finance, education, and operations.",
      ["Bachelor's degree", "Internship experience", "Ready for junior roles"]
    ),
    "candidate-technicians": candidateTemplate(
      "Skilled technicians",
      "Hands-on candidates for field service, construction, transport, installation, and maintenance.",
      ["Practical experience", "Location-ready", "Trade and safety skills"]
    ),
    "candidate-professionals": candidateTemplate(
      "Verified professionals",
      "Experienced applicants with stronger profiles, clearer work history, and relevant skills.",
      ["Verified profile", "Mid to senior level", "Shortlist-ready"]
    ),
    email: contactTemplate(),
    "hiring-updates": updatesTemplate(),
    "verify-employer": verifyEmployerTemplate()
  };

  openActionDialog(templates[action] || contactTemplate());
}

function openActionDialog(markup) {
  actionDetails.innerHTML = markup;
  actionDialog.showModal();
}

function applicantsTemplate() {
  const topJobs = jobs
    .slice(0, 3)
    .map(
      (job) => `
        <div class="modal-row">
          <div>
            <strong>${escapeHtml(job.title)}</strong>
            <p>${job.applicants} applicants · ${escapeHtml(job.status)}</p>
          </div>
          <button class="mini-action" type="button">Shortlist</button>
        </div>
      `
    )
    .join("");

  return `
    <section class="action-content">
      <p class="eyebrow">Applicants</p>
      <h2>Review applicants faster</h2>
      <p>Track applications, shortlist promising candidates, and follow up from one employer workspace.</p>
      <div class="modal-list">${topJobs}</div>
    </section>
  `;
}

function candidateDatabaseTemplate() {
  return `
    <section class="action-content">
      <p class="eyebrow">Candidate database</p>
      <h2>Search qualified talent</h2>
      <p>Filter candidates by category, location, experience level, skills, and availability.</p>
      <div class="modal-chip-row">
        <span>IT & Software</span>
        <span>Healthcare</span>
        <span>Transport</span>
        <span>Entry level</span>
        <span>Senior talent</span>
      </div>
      <button class="primary-button" type="button">Open database</button>
    </section>
  `;
}

function candidateTemplate(title, text, items) {
  return `
    <section class="action-content">
      <p class="eyebrow">Candidate preview</p>
      <h2>${escapeHtml(title)}</h2>
      <p>${escapeHtml(text)}</p>
      <div class="modal-chip-row">
        ${items.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
      </div>
      <button class="primary-button" type="button">Request matches</button>
    </section>
  `;
}

function jobListingTemplate(job) {
  return `
    <section class="action-content">
      <p class="eyebrow">Listing details</p>
      <h2>${escapeHtml(job.title)}</h2>
      <p>${escapeHtml(job.company)} · ${escapeHtml(job.location)} · ${job.applicants} applicants</p>
      <div class="modal-chip-row">
        <span>${escapeHtml(job.status)}</span>
        <span>${escapeHtml(job.type)}</span>
        <span>${escapeHtml(job.experience)}</span>
      </div>
      <button class="primary-button" type="button">Manage listing</button>
    </section>
  `;
}

function contactTemplate() {
  return `
    <section class="action-content">
      <p class="eyebrow">Contact</p>
      <h2>Email JobLink UG</h2>
      <p>Tell us what role you are hiring for and our team will help you choose the best posting option.</p>
      <div class="modal-row">
        <strong>employers@joblinkug.example</strong>
        <button class="mini-action" type="button">Copy</button>
      </div>
    </section>
  `;
}

function updatesTemplate() {
  return `
    <section class="action-content">
      <p class="eyebrow">Hiring updates</p>
      <h2>Subscribe to employer insights</h2>
      <p>Get hiring tips, talent trends, and product updates for employers in Uganda.</p>
      <label class="modal-field">
        Work email
        <input placeholder="you@company.com" />
      </label>
      <button class="primary-button" type="button">Subscribe</button>
    </section>
  `;
}

function verifyEmployerTemplate() {
  return `
    <section class="action-content">
      <p class="eyebrow">Employer verification</p>
      <h2>Review company details</h2>
      <p>Check uploaded documents, contact details, business category, and active listings before approval.</p>
      <div class="modal-chip-row">
        <span>License uploaded</span>
        <span>Contact verified</span>
        <span>2 active listings</span>
      </div>
      <button class="primary-button" type="button">Approve employer</button>
    </section>
  `;
}

function resetDemo() {
  jobs = [...seedJobs];
  saved = [];
  applications = [];
  showToast("Demo data reset.");
  render();
}

function clearFilters() {
  jobSearch.value = "";
  locationFilter.value = "all";
  categoryFilter.value = "all";
  jobTypeFilter.value = "all";
  experienceFilter.value = "all";
  salaryFilter.value = "all";
  dateFilter.value = "all";
  workModeFilter.value = "all";
  sortFilter.value = "newest";
  render();
}

function applyQuickFilter(chip) {
  clearFilters();

  if (chip.dataset.quickCategory) {
    categoryFilter.value = chip.dataset.quickCategory;
  }

  if (chip.dataset.quickMode) {
    workModeFilter.value = chip.dataset.quickMode;
  }

  if (chip.dataset.quickExperience) {
    experienceFilter.value = chip.dataset.quickExperience;
  }

  render();
}

function matchesSearch(job, query) {
  if (!query) {
    return true;
  }

  return [
    job.title,
    job.company,
    job.location,
    job.category,
    job.type,
    job.experience,
    job.workMode,
    ...(job.skills || [])
  ]
    .join(" ")
    .toLowerCase()
    .includes(query);
}

function matchesChoice(value, selected) {
  return selected === "all" || value === selected;
}

function matchesSalary(job, selected) {
  if (selected === "all") {
    return true;
  }

  const [min, max] = selected.split("-").map(Number);
  return job.salaryMax >= min && job.salaryMin <= max;
}

function matchesDate(job, selected) {
  if (selected === "all") {
    return true;
  }

  const posted = new Date(`${job.postedAt}T00:00:00`);
  const now = new Date("2026-06-11T00:00:00");
  const daysOld = (now - posted) / (1000 * 60 * 60 * 24);
  return daysOld <= Number(selected);
}

function sortJobs(first, second, sort) {
  if (sort === "salaryHigh") {
    return second.salaryMax - first.salaryMax;
  }

  if (sort === "salaryLow") {
    return first.salaryMin - second.salaryMin;
  }

  return new Date(second.postedAt) - new Date(first.postedAt);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en-UG", {
    day: "numeric",
    month: "short",
    year: "numeric"
  }).format(new Date(`${value}T00:00:00`));
}

function parseSalaryMin(value) {
  const numbers = extractSalaryNumbers(value);
  return numbers[0] || 0;
}

function parseSalaryMax(value) {
  const numbers = extractSalaryNumbers(value);
  return numbers[numbers.length - 1] || parseSalaryMin(value);
}

function extractSalaryNumbers(value) {
  return String(value)
    .match(/\d+(\.\d+)?\s*[km]?/gi)
    ?.map((item) => {
      const amount = Number.parseFloat(item);
      if (item.toLowerCase().includes("k")) {
        return amount * 1000;
      }
      return item.toLowerCase().includes("m") ? amount * 1000000 : amount;
    }) || [];
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("show"), 2200);
}

function saveState() {
  localStorage.setItem("joblink.jobs", JSON.stringify(jobs));
  localStorage.setItem("joblink.saved", JSON.stringify(saved));
  localStorage.setItem("joblink.applications", JSON.stringify(applications));
}

function load(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
